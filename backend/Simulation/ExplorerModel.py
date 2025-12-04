import random
from mesa import Model
from mesa.space import MultiGrid
from Simulation.AgentBaseModel import AgentBaseModel
from Simulation.AgentFireFighter import AgentFireFighter
from Simulation.AgentRescuer import AgenteRescuer
from Simulation.AuxFunctions import readMap, get_grid
from mesa.datacollection import DataCollector

class ExplorerModel(Model):
    """
    Modelo principal de simulación de rescate en incendios.
    Gestiona el grid, agentes, propagación de fuego, víctimas y condiciones de victoria/derrota.
    Implementa el patrón Observer para notificar cambios de estado en cada paso.
    """
    
    def __init__(self, width, height, agents, pa, strategy="random", printable=False, on_step_callback=None):
        """
        Inicializa el modelo de simulación con el mapa y los agentes según la estrategia elegida.
        
        Parámetros:
            width (int): Ancho del grid de simulación
            height (int): Alto del grid de simulación
            agents (int): Número de agentes a desplegar
            pa (int): Puntos de acción (energía máxima) de cada agente
            strategy (str): Estrategia de despliegue ('random' o 'intelligent')
            printable (bool): Indica si se deben imprimir mensajes de debug en consola
            on_step_callback (function): Función a ejecutar después de cada paso (patrón Observer)
        """
        super().__init__()

        self.on_step_callback = on_step_callback

        # Carga el estado inicial del mapa desde archivo
        mapData = readMap()
        if mapData is None: 
            raise Exception("Error leyendo InitialState.txt")

        self.grid = MultiGrid(width, height, torus=False)
        self.walls = mapData['walls']
        self.doors = mapData['doors'] 
        # Estructura de fuego: [y, x, intensity] donde intensity: 1=humo, 2=fuego
        self.fires = [[f[0], f[1], 2] for f in mapData['fires']]
        self.pois = mapData['pois'] 
        self.entryPoints = mapData['entryPoints']
        
        self.agents_list = []
        self.replenish_pois()

        # Métricas de juego
        self.steps = 0
        self.pa = pa
        self.victims_saved = 0
        self.victims_lost = 0
        self.damage_taken = 0
        self.running = True
        self.printable = printable
        self.strategy = strategy

        # Despliegue de agentes según estrategia seleccionada
        if self.strategy == "intelligent":
            self._place_intelligent_agents(agents, pa)
        else:
            self._place_random_agents(agents, pa)

    def _place_random_agents(self, num_agents, pa):
        """
        Despliega agentes de tipo base en posiciones aleatorias del perímetro exterior.
        
        Parámetros:
            num_agents (int): Cantidad de agentes a desplegar
            pa (int): Puntos de acción de cada agente
        """
        # Recopila todas las posiciones del perímetro exterior del edificio
        exterior_positions = []
        for x in range(self.grid.width):
            exterior_positions.append((x, 0))
        for x in range(self.grid.width):
            exterior_positions.append((x, self.grid.height - 1))
        for y in range(1, self.grid.height - 1):
            exterior_positions.append((0, y))
        for y in range(1, self.grid.height - 1):
            exterior_positions.append((self.grid.width - 1, y))
        
        random.shuffle(exterior_positions)
        
        for i in range(num_agents):
            pos = exterior_positions[i % len(exterior_positions)]
            a = AgentBaseModel(self, pa, i, printable=self.printable)
            self.grid.place_agent(a, pos)
            self.agents_list.append(a)
            if self.printable:
                print(f"RANDOM - Agente {i} (Base) en {pos}")

    def _place_intelligent_agents(self, num_agents, pa):
        """
        Despliega agentes en parejas especializadas (Bombero + Rescatador) distribuidas en puntos de entrada.
        Cada pareja se asigna rotativamente a una ambulancia/puerta de entrada disponible.
        
        Parámetros:
            num_agents (int): Cantidad de agentes a desplegar
            pa (int): Puntos de acción de cada agente
        """
        # Convierte entry points de formato (y,x) a (x,y) para compatibilidad con grid
        outside_doors = [(ep[1], ep[0]) for ep in self.entryPoints]
        
        if self.printable:
            print(f"👥 Desplegando {num_agents} agentes en parejas...")
        
        for i in range(num_agents):
            # Calcula índice de pareja para distribución (0, 1, 2, ...)
            pair_idx = i // 2 
            
            # Asigna puerta de entrada rotando entre las disponibles
            ambulance_idx = pair_idx % len(outside_doors)
            pos = outside_doors[ambulance_idx]
            
            # Agentes pares son Bomberos, impares son Rescatadores
            if i % 2 == 0:
                a = AgentFireFighter(self, pa, i, printable=self.printable)
                role_icon = "Bomberos"
            else:
                a = AgenteRescuer(self, pa, i, printable=self.printable)
                role_icon = "Rescatadores"
            
            self.grid.place_agent(a, pos)
            self.agents_list.append(a)
            
            if self.printable:
                print(f"{role_icon} INTELLIGENT - Agente {i} ({a.role}) → "
                      f"Ambulancia {ambulance_idx + 1} en {pos} [Pareja {pair_idx + 1}]")

    def notify_observer(self):
        """
        Notifica al observador registrado (callback) sobre cambios en el estado del modelo.
        Implementa el patrón Observer para sincronización con visualizadores externos.
        """
        if self.on_step_callback:
            self.on_step_callback()

    def step(self):
        """
        Ejecuta un paso completo de simulación en el siguiente orden:
        1. Procesa acciones de todos los agentes
        2. Verifica rescates completados en puntos de entrada
        3. Avanza la propagación del fuego
        4. Repone víctimas si es necesario
        5. Verifica condiciones de fin de juego
        """
        outside_doors = [(ep[1], ep[0]) for ep in self.entryPoints]
        
        # Procesa las acciones de cada agente y verifica rescates
        for agent in self.agents_list:
            if agent.carrying_victim and agent.pos in outside_doors:
                agent.carrying_victim = False
                self.victims_saved += 1
                if self.printable:
                    print(f"¡Víctima salvada por Agente {agent.id} en {agent.pos}!")
            
            if not self.running: 
                break
            
            agent.step()
            self.notify_observer() 
            self.check_game_over()

        if not self.running: 
            return
        
        # Fase de ambiente: propagación de fuego y reposición de víctimas
        self.advance_fire()
        self.replenish_pois()
        self.notify_observer()
        self.check_game_over()
        
        self.steps += 1

    def get_door_index(self, pos1, pos2):
        """
        Busca si existe una puerta entre dos posiciones adyacentes.
        Las puertas se almacenan en formato [(y1, x1), (y2, x2), status].
        
        Parámetros:
            pos1 (tuple): Primera posición en formato (x, y)
            pos2 (tuple): Segunda posición en formato (x, y)
        
        Retorna:
            int: Índice de la puerta en self.doors, o -1 si no existe puerta
        """
        y1, x1 = pos1[1], pos1[0]
        y2, x2 = pos2[1], pos2[0]
        
        for i, d in enumerate(self.doors):
            door_p1 = d[0]
            door_p2 = d[1]
            # Verifica coincidencia en ambas direcciones (bidireccional)
            if ((door_p1 == (y1, x1) and door_p2 == (y2, x2)) or
                (door_p1 == (y2, x2) and door_p2 == (y1, x1))):
                return i
        return -1

    def replenish_pois(self):
        """
        Mantiene siempre 3 situaciones activas de víctimas/falsas alarmas considerando:
        - POIs físicamente en el mapa
        - Víctimas siendo transportadas por agentes
        Genera nuevos POIs aleatoriamente (50% víctima, 50% falsa alarma) en celdas válidas.
        """
        # Cuenta POIs físicos en el mapa
        pois_on_map = len(self.pois)
        
        # Cuenta víctimas siendo transportadas por agentes
        victims_being_carried = sum(1 for a in self.agents_list if getattr(a, 'carrying_victim', False))

        # Total de situaciones activas debe ser 3
        total_active = pois_on_map + victims_being_carried

        while total_active < 3:
            # Identifica celdas válidas para nuevo POI (sin fuego ni POI existente)
            valid_spots = []
            for x in range(self.grid.width):
                for y in range(self.grid.height):
                    pos = (x, y)
                    if not self.is_fire(pos) and not self.is_poi(pos):
                        valid_spots.append(pos)
            
            if valid_spots:
                pos = self.random.choice(valid_spots)
                # Genera tipo aleatorio: 50% víctima ('v'), 50% falsa alarma ('f')
                ptype = 'v' if random.random() > 0.5 else 'f'
                # Estructura POI: [y, x, tipo, revelado]
                self.pois.append([pos[1], pos[0], ptype, False]) 
                total_active += 1
            else: 
                break

    def is_poi(self, pos):
        """
        Verifica si existe un POI en la posición especificada.
        
        Parámetros:
            pos (tuple): Posición a verificar en formato (x, y)
        
        Retorna:
            bool: True si hay un POI en esa posición, False en caso contrario
        """
        x, y = pos
        return any(p[0] == y and p[1] == x for p in self.pois)

    def reveal_poi(self, pos):
        """
        Revela el tipo de un POI en la posición especificada.
        Si es falsa alarma, se elimina inmediatamente del mapa.
        Si es víctima, permanece para ser rescatada.
        
        Parámetros:
            pos (tuple): Posición del POI en formato (x, y)
        
        Retorna:
            str: 'Victim' si es víctima real, 'FalseAlarm' si es falsa alarma, None si no hay POI
        """
        x, y = pos
        target_poi = None
        
        # Busca el POI específico en la posición
        for p in self.pois:
            if p[0] == y and p[1] == x:
                target_poi = p
                break
        
        if target_poi:
            # Marca como revelado (manejo seguro para compatibilidad con versiones anteriores)
            if len(target_poi) == 3: 
                target_poi.append(True)
            else: 
                target_poi[3] = True
            
            # Determina el tipo de POI
            p_type = target_poi[2]
            result = 'Victim' if p_type in ['v', 'Victim'] else 'FalseAlarm'

            # Las falsas alarmas se eliminan inmediatamente al ser reveladas
            if result == 'FalseAlarm':
                self.remove_poi(pos)
                if self.printable:
                    print(f"Falsa alarma en {pos} eliminada.")
            
            return result
            
        return None

    def remove_poi(self, pos):
        """
        Elimina un POI de la posición especificada.
        
        Parámetros:
            pos (tuple): Posición en formato (x, y)
        """
        x, y = pos
        self.pois = [p for p in self.pois if not (p[0] == y and p[1] == x)]

    def check_victims_and_pois_in_fire(self):
        """
        Verifica y procesa víctimas/POIs consumidos por fuego activo.
        Se ejecuta una vez por turno para contabilizar pérdidas.
        """
        for f in self.fires:
            if f[2] == 2:  # Solo fuego activo (no humo)
                fx, fy = f[1], f[0]
                self.check_poi_on_fire(fx, fy)

    def check_poi_on_fire(self, x, y):
        """
        Verifica si hay un POI en una celda con fuego y procesa las consecuencias.
        Incrementa victims_lost si es una víctima real.
        
        Parámetros:
            x (int): Coordenada x de la celda
            y (int): Coordenada y de la celda
        """
        poi_removed = False
        
        # Itera en reversa para poder eliminar elementos durante la iteración
        for i in range(len(self.pois) - 1, -1, -1):
            p = self.pois[i]
            py, px = p[0], p[1] 
            
            if px == x and py == y:
                p_type = p[2]
                
                if p_type in ['Victim', 'v']:
                    self.victims_lost += 1
                    if self.printable:
                        print(f"¡Víctima perdida en el fuego en ({x}, {y})! Total perdidas: {self.victims_lost}")
                elif p_type in ['f']:
                    if self.printable:
                        print(f"Falsa alarma consumida por el fuego en ({x}, {y})")
                
                self.pois.pop(i)
                poi_removed = True
        
        # Repone POIs si el total cae por debajo de 3
        if poi_removed and len(self.pois) < 3:
            self.replenish_pois()

    def has_wall(self, x, y, dir_idx):
        """
        Verifica si existe una pared en una dirección específica desde una posición.
        
        Parámetros:
            x (int): Coordenada x de la celda
            y (int): Coordenada y de la celda
            dir_idx (int): Índice de dirección (0=Arriba, 1=Izquierda, 2=Abajo, 3=Derecha)
        
        Retorna:
            bool: True si existe pared en esa dirección, False en caso contrario
        """
        if 0 <= y < len(self.walls) and 0 <= x < len(self.walls[0]):
            return self.walls[y][x][dir_idx] != '0'
        return False
    
    def remove_wall(self, x, y, dir_idx):
        """
        Elimina una pared en una dirección específica y su contraparte en la celda adyacente.
        Incrementa el contador de daño estructural del edificio.
        
        Parámetros:
            x (int): Coordenada x de la celda
            y (int): Coordenada y de la celda
            dir_idx (int): Índice de dirección de la pared a eliminar
        """
        if 0 <= y < len(self.walls) and 0 <= x < len(self.walls[0]):
            w = list(self.walls[y][x])
            w[dir_idx] = '0'
            self.walls[y][x] = "".join(w)
            
            # Calcula posición de celda adyacente y dirección opuesta
            nx, ny = x, y
            opp = -1
            
            if dir_idx == 0: 
                ny += 1
                opp = 2
            elif dir_idx == 1: 
                nx -= 1
                opp = 3
            elif dir_idx == 2: 
                ny -= 1
                opp = 0
            elif dir_idx == 3: 
                nx += 1
                opp = 1
            
            # Elimina la pared desde el lado opuesto para mantener consistencia
            if 0 <= ny < len(self.walls) and 0 <= nx < len(self.walls[0]):
                w2 = list(self.walls[ny][nx])
                w2[opp] = '0'
                self.walls[ny][nx] = "".join(w2)

    def can_move(self, from_pos, to_pos):
        """
        Verifica si un agente puede moverse legalmente desde una posición a otra adyacente.
        Considera paredes y puertas cerradas como obstáculos.
        
        Parámetros:
            from_pos (tuple): Posición origen en formato (x, y)
            to_pos (tuple): Posición destino en formato (x, y)
        
        Retorna:
            bool: True si el movimiento es legal, False en caso contrario
        """
        fx, fy = from_pos
        tx, ty = to_pos
        dx = tx - fx
        dy = ty - fy

        # Verifica que sean celdas adyacentes (distancia Manhattan = 1)
        if abs(dx) + abs(dy) != 1:
            return False

        # Mapea el movimiento a índice de dirección según convención
        if dy == -1 and dx == 0:
            dir_idx = 0  # Arriba
        elif dx == -1 and dy == 0:
            dir_idx = 1  # Izquierda
        elif dy == 1 and dx == 0:
            dir_idx = 2  # Abajo
        elif dx == 1 and dy == 0:
            dir_idx = 3  # Derecha
        else:
            return False

        # Verifica obstáculos: pared bloquea el paso
        if self.has_wall(fx, fy, dir_idx):
            return False

        # Verifica puerta: si existe y está cerrada, bloquea el paso
        d_idx = self.get_door_index(from_pos, to_pos)
        if d_idx != -1:
            status = self.doors[d_idx][2]
            if status == 'Closed':
                return False

        return True

    def advance_fire(self):
        """
        Avanza la propagación del fuego mediante tirada de dados.
        Dado rojo (1-6) determina fila, dado negro (1-8) determina columna.
        La celda afectada evoluciona: Vacía→Humo, Humo→Fuego, Fuego→Explosión.
        Ejecuta flashover (propagación de fuego a humo adyacente) después de la tirada.
        """
        # Simula tirada de dados para determinar celda afectada
        red_die = self.random.randint(1, 6)
        black_die = self.random.randint(1, 8)
        x = black_die - 1
        y = self.grid.height - red_die
        
        pos = (x, y)
        status = self.get_cell_status(pos)
        
        if self.printable:
            print(f"Fuego en {pos}: {status}")
        
        # Evoluciona el estado de la celda según su estado actual
        if status == 'Empty':
            self.add_fire_or_smoke(pos, 1)
        elif status == 'Smoke':
            self.add_fire_or_smoke(pos, 2)
        elif status == 'Fire': 
            if self.printable:
                print("EXPLOSIÓN")
            self.resolve_explosion(pos)
        
        # Procesa efectos secundarios: flashover y víctimas en fuego
        self.resolve_flashover()
        self.check_victims_and_pois_in_fire()

    def add_fire_or_smoke(self, pos, intensity):
        """
        Agrega humo o fuego a una celda específica.
        El humo se convierte automáticamente en fuego si hay fuego adyacente.
        El fuego daña a agentes presentes y destruye víctimas.
        
        Parámetros:
            pos (tuple): Posición en formato (x, y)
            intensity (int): Intensidad del fuego (1=humo, 2=fuego)
        """
        x, y = pos
        
        # Si se intenta agregar humo pero hay fuego adyacente, se convierte directamente en fuego
        if intensity == 1:
            neighbors = self.grid.get_neighborhood((x, y), moore=False, include_center=False)
            for n in neighbors:
                if self.get_cell_status(n) == 'Fire':
                    intensity = 2
                    break

        # Procesa consecuencias del fuego activo
        if intensity == 2:
            self.check_poi_on_fire(x, y)
            cell_contents = self.grid.get_cell_list_contents(pos)
            for obj in cell_contents:
                if isinstance(obj, AgentBaseModel): 
                    self.send_to_ambulance(obj)
        
        # Actualiza o crea registro de fuego en la posición
        found = False
        for f in self.fires:
            if f[0] == y and f[1] == x:
                f[2] = intensity
                found = True
                break
        
        if not found: 
            self.fires.append([y, x, intensity])

    def resolve_explosion(self, center_pos):
        """
        Resuelve una explosión propagando fuego en las 4 direcciones cardinales.
        La propagación se detiene al encontrar: pared (la destruye), puerta cerrada (la destruye), 
        o celda sin fuego (la enciende). Si encuentra más fuego, continúa propagándose.
        
        Parámetros:
            center_pos (tuple): Posición central de la explosión en formato (x, y)
        """
        cx, cy = center_pos
        # Define vectores de dirección y sus índices correspondientes
        directions = [(0, 1, 0), (-1, 0, 1), (0, -1, 2), (1, 0, 3)] 
        
        for dx, dy, widx in directions:
            dist = 1
            active = True
            
            while active:
                nx, ny = cx + (dx*dist), cy + (dy*dist)
                
                # Verifica límites del grid
                if not (0 <= ny < self.grid.height and 0 <= nx < self.grid.width): 
                    break
                
                px, py = cx + (dx*(dist-1)), cy + (dy*(dist-1))
                
                # Verifica colisión con pared: la destruye y detiene propagación
                if self.has_wall(px, py, widx):
                    self.remove_wall(px, py, widx)
                    self.damage_taken += 1
                    active = False
                    break
                
                # Verifica colisión con puerta cerrada: la destruye y detiene propagación
                d_idx = self.get_door_index((px,py), (nx,ny))
                if d_idx != -1 and self.doors[d_idx][2] == 'Closed':
                    self.doors.pop(d_idx)
                    active = False
                    break

                # Propaga fuego según estado de celda destino
                status = self.get_cell_status((nx, ny))
                if status != 'Fire':
                    self.add_fire_or_smoke((nx, ny), 2)
                    active = False
                else:
                    # Continúa propagación si encuentra más fuego
                    dist += 1

    def resolve_flashover(self):
        """
        Convierte todo humo adyacente a fuego en fuego activo.
        """
        # Identifica todas las posiciones con fuego activo
        fire_locs = {(f[1], f[0]) for f in self.fires if f[2] == 2}
        
        # Acumula conversiones para no modificar la lista durante iteración
        to_convert = []
        for i, f in enumerate(self.fires):
            if f[2] == 1:  # Solo humo
                fy, fx = f[0], f[1]
                neighbors = self.grid.get_neighborhood((fx, fy), moore=False, include_center=False)
                # Convierte si tiene al menos un vecino con fuego
                if any(n in fire_locs for n in neighbors):
                    to_convert.append(i)
        
        # Ejecuta conversiones y verifica víctimas afectadas
        for idx in to_convert:
            if 0 <= idx < len(self.fires) and self.fires[idx][2] == 1:
                self.fires[idx][2] = 2
                fx, fy = self.fires[idx][1], self.fires[idx][0]
                self.check_poi_on_fire(fx, fy)

    def send_to_ambulance(self, agent):
        """
        Envía un agente herido a la ambulancia más cercana en el perímetro exterior.
        Si el agente cargaba una víctima, esta se pierde.
        
        Parámetros:
            agent (AgentBaseModel): Agente a evacuar
        """
        if self.printable:
            print(f"Agente {agent.id} herido -> Buscando Ambulancia.")
        
        # Víctima transportada se pierde si el agente es herido
        if agent.carrying_victim:
            self.victims_lost += 1
            agent.carrying_victim = False
            if self.printable:
                print(f"La víctima que cargaba el Agente {agent.id} ha muerto.")

        # Construye lista de posiciones del perímetro exterior
        width, height = self.grid.width, self.grid.height
        perimeter = []
        for x in range(width):
            perimeter.append((x, 0))            
            perimeter.append((x, height - 1)) 
        for y in range(1, height - 1):
            perimeter.append((0, y))            
            perimeter.append((width - 1, y))   
        
        # Busca primera posición del perímetro sin fuego
        target = None
        for pos in perimeter:
            if not self.is_fire(pos):
                target = pos
                break
        
        # Mueve agente a posición segura o esquina superior izquierda como fallback
        if target:
            self.grid.move_agent(agent, target)
        else:
            self.grid.move_agent(agent, (0,0))

    def get_cell_status(self, pos):
        """
        Obtiene el estado actual de una celda respecto al fuego.
        
        Parámetros:
            pos (tuple): Posición a consultar en formato (x, y)
        
        Retorna:
            str: 'Empty' si no hay fuego, 'Smoke' si hay humo, 'Fire' si hay fuego activo
        """
        x, y = pos
        for f in self.fires:
            if f[0] == y and f[1] == x: 
                return 'Smoke' if f[2]==1 else 'Fire'
        return 'Empty'
    
    def is_fire(self, pos):
        """
        Verifica si hay fuego activo en una posición específica.
        
        Parámetros:
            pos (tuple): Posición a verificar en formato (x, y)
        
        Retorna:
            bool: True si hay fuego activo, False en caso contrario
        """
        return self.get_cell_status(pos) == 'Fire'

    def is_outside_building(self, pos):
        """
        Verifica si una posición está en el perímetro exterior del edificio.
        
        Parámetros:
            pos (tuple): Posición a verificar en formato (x, y)
        
        Retorna:
            bool: True si está en el perímetro exterior, False en caso contrario
        """
        x, y = pos
        return (x == 0 or x == self.grid.width - 1 or 
                y == 0 or y == self.grid.height - 1)

    def remove_fire_completely(self, pos):
        """
        Elimina completamente un fuego de una posición específica sin degradarlo.
        
        Parámetros:
            pos (tuple): Posición en formato (x, y)
        """
        x, y = pos
        for i, f in enumerate(self.fires):
            if f[0] == y and f[1] == x:
                self.fires.pop(i)
                if self.printable:
                    print(f"Fuego removido completamente de {pos}")
                return

    def remove_smoke(self, pos):
        """
        Elimina humo de una posición específica si existe.
        
        Parámetros:
            pos (tuple): Posición en formato (x, y)
        """
        x, y = pos
        for i, f in enumerate(self.fires):
            if f[0] == y and f[1] == x and f[2] == 1:
                self.fires.pop(i)
                if self.printable:
                    print(f"Humo removido de {pos}")
                return

    def downgrade_fire(self, pos):
        """
        Degrada el nivel de fuego en una posición: Fuego->Humo o Humo->Eliminar.
        
        Parámetros:
            pos (tuple): Posición en formato (x, y)
        """
        x, y = pos
        for i, f in enumerate(self.fires):
            if f[0] == y and f[1] == x:
                if f[2] == 2:  # Fuego activo se convierte en humo
                    f[2] = 1
                    if self.printable:
                        print(f"Fuego convertido a humo en {pos}")
                else:  # Humo se elimina completamente
                    self.fires.pop(i)
                    if self.printable:
                        print(f"Humo removido de {pos}")
                return
            
    def check_game_over(self):
        """
        Verifica las condiciones de fin de juego y detiene la simulación si se cumplen.
        Victoria: 7 o más víctimas salvadas
        Derrota: 4 o más víctimas perdidas, o 24 o más puntos de daño estructural
        """
        if self.victims_saved >= 7: 
            self.running = False
            if self.printable:
                print("GANASTE")
        
        if self.victims_lost >= 4:
            self.running = False
            if self.printable:
                print("PERDISTE")
        
        if self.damage_taken >= 24:
            self.running = False
            if self.printable:
                print("DERRUMBE")
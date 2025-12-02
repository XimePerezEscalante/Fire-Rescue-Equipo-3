import random
from mesa import Model
from mesa.space import MultiGrid
from Simulation.AgentBaseModel import AgentBaseModel
from Simulation.AgentFireFighter import AgentFireFighter
from Simulation.AgentRescuer import AgenteRescuer
from Simulation.AuxFunctions import readMap, get_grid
from mesa.datacollection import DataCollector

class ExplorerModel(Model):
    def __init__(self, width, height, agents, pa, strategy="random", printable=False, on_step_callback=None):
        super().__init__()

        self.on_step_callback = on_step_callback

        mapData = readMap()
        if mapData is None: raise Exception("Error leyendo InitialState.txt")

        self.grid = MultiGrid(width, height, torus=False)
        self.walls = mapData['walls']
        self.doors = mapData['doors'] 
        self.fires = [[f[0], f[1], 2] for f in mapData['fires']]
        self.pois = mapData['pois'] 
        self.entryPoints = mapData['entryPoints']
        
        self.agents_list = []
        self.replenish_pois()

        self.steps = 0
        self.pa = pa
        self.victims_saved = 0
        self.victims_lost = 0
        self.damage_taken = 0
        self.running = True
        self.printable = printable
        self.strategy = strategy

        
        if self.strategy == "intelligent":
            self._place_intelligent_agents(agents, pa)
        else:
            self._place_random_agents(agents, pa)

    def _place_random_agents(self, num_agents, pa):
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
                print(f"🎲 RANDOM - Agente {i} (Base) en {pos}")

    def _place_intelligent_agents(self, num_agents, pa):
        outside_doors = [(ep[1], ep[0]) for ep in self.entryPoints]
        if self.printable:
            print(f"👥 Desplegando {num_agents} agentes en parejas...")
        
        for i in range(num_agents):
            # Lógica corregida: 
            # Calculamos a qué pareja pertenece el agente (0, 1, 2...)
            pair_idx = i // 2 
            
            # Asignamos la puerta usando el índice de la pareja, rotando por las puertas disponibles
            ambulance_idx = pair_idx % len(outside_doors)
            
            pos = outside_doors[ambulance_idx]
            
            # El par (even) es Bombero, el impar (odd) es Rescatador
            if i % 2 == 0:
                a = AgentFireFighter(self, pa, i, printable=self.printable)
                role_icon = "🔥"
            else:
                a = AgenteRescuer(self, pa, i, printable=self.printable)
                role_icon = "🚑"
            
            self.grid.place_agent(a, pos)
            self.agents_list.append(a)
            
            if self.printable:
                print(f"{role_icon} INTELLIGENT - Agente {i} ({a.role}) → "
                      f"Ambulancia {ambulance_idx + 1} en {pos} [Pareja {pair_idx + 1}]")

    def notify_observer(self):
        if self.on_step_callback:
            self.on_step_callback()

    def step(self):
        
        outside_doors = [(ep[1], ep[0]) for ep in self.entryPoints]
        
        for agent in self.agents_list:
            if agent.carrying_victim and agent.pos in outside_doors:
                agent.carrying_victim = False
                self.victims_saved += 1
                if self.printable:
                    print(f"¡Víctima salvada por Agente {agent.id} en {agent.pos}!")
            if not self.running: break
            agent.step()
            self.notify_observer() 
            self.check_game_over()

        if not self.running: return
        self.advance_fire()
        self.replenish_pois()
        self.notify_observer()
        self.check_game_over()
        
        self.steps += 1

    # --- PUERTAS ---
    def get_door_index(self, pos1, pos2):
        """
        Busca si hay una puerta entre pos1 y pos2.
        pos1/pos2 están en formato (x,y).
        Las puertas están guardadas como [(y1, x1), (y2, x2), status] — por eso hacemos la conversión
        """
        y1, x1 = pos1[1], pos1[0]
        y2, x2 = pos2[1], pos2[0]
        for i, d in enumerate(self.doors):
            door_p1 = d[0]
            door_p2 = d[1]
            if ((door_p1 == (y1, x1) and door_p2 == (y2, x2)) or
                (door_p1 == (y2, x2) and door_p2 == (y1, x1))):
                return i
        return -1

    # --- POIS ---
    def replenish_pois(self):
        # 1. Contamos los POIs físicos en el mapa
        pois_on_map = len(self.pois)
        
        # 2. Contamos las víctimas que los agentes llevan en brazos
        # (Asumiendo que tus agentes tienen el atributo boolean 'carrying_victim')
        victims_being_carried = sum(1 for a in self.agents_list if getattr(a, 'carrying_victim', False))

        # El total de "situaciones activas" es la suma de ambos
        total_active = pois_on_map + victims_being_carried

        # Solo reponemos si la suma total es menor a 3
        while total_active < 3:
            valid_spots = []
            for x in range(self.grid.width):
                for y in range(self.grid.height):
                    pos = (x, y)
                    # Solo colocar si no hay fuego y no hay otro POI
                    if not self.is_fire(pos) and not self.is_poi(pos):
                        valid_spots.append(pos)
            
            if valid_spots:
                pos = self.random.choice(valid_spots)
                ptype = 'v' if random.random() > 0.5 else 'f' # 50/50 Victima o Falsa Alarma
                self.pois.append([pos[1], pos[0], ptype, False]) 
                total_active += 1 # Importante: aumentamos el contador temporal para el loop
            else: 
                break

    def is_poi(self, pos):
        x, y = pos
        return any(p[0] == y and p[1] == x for p in self.pois)

    def reveal_poi(self, pos):
        x, y = pos
        target_poi = None
        
        # Buscamos el POI específico
        for p in self.pois:
            if p[0] == y and p[1] == x:
                target_poi = p
                break
        
        if target_poi:
            # Marcamos como revelado (manejo seguro de índices)
            if len(target_poi) == 3: target_poi.append(True)
            else: target_poi[3] = True
            
            # Determinamos tipo
            p_type = target_poi[2]
            result = 'Victim' if p_type in ['v', 'Victim'] else 'FalseAlarm'

            # --- REGLA: Si es Falsa Alarma, se elimina YA ---
            if result == 'FalseAlarm':
                self.remove_poi(pos)
                if self.printable:
                    print(f"🔍 Falsa alarma en {pos} eliminada.")
            # --- REGLA: Si es Víctima, se queda en el mapa ---
            # (El replenish_pois contará este POI y no generará uno nuevo)
            
            return result
            
        return None

    def remove_poi(self, pos):
        x, y = pos
        self.pois = [p for p in self.pois if not (p[0] == y and p[1] == x)]

    def check_victims_and_pois_in_fire(self):
        """Verifica POIs/Víctimas perdidos por fuego (una vez por turno)"""
        for f in self.fires:
            if f[2] == 2:  # Solo fuego, no humo
                fx, fy = f[1], f[0]
                self.check_poi_on_fire(fx, fy)

    def check_poi_on_fire(self, x, y):
        poi_removed = False
        for i in range(len(self.pois) - 1, -1, -1):
            p = self.pois[i]
            py, px = p[0], p[1] 
            if px == x and py == y:
                p_type = p[2]
                if p_type in ['Victim', 'v']:
                    self.victims_lost += 1
                    if self.printable:
                        print(f"💀 ¡Víctima perdida en el fuego en ({x}, {y})! Total perdidas: {self.victims_lost}")
                elif p_type in ['f']:
                    if self.printable:
                        print(f"🔥 Falsa alarma consumida por el fuego en ({x}, {y})")
                self.pois.pop(i)
                poi_removed = True
        if poi_removed and len(self.pois) < 3:
            self.replenish_pois()

    def has_wall(self, x, y, dir_idx):
        if 0 <= y < len(self.walls) and 0 <= x < len(self.walls[0]):
            return self.walls[y][x][dir_idx] != '0'
        return False
    
    def remove_wall(self, x, y, dir_idx):
        if 0 <= y < len(self.walls) and 0 <= x < len(self.walls[0]):
            w = list(self.walls[y][x])
            w[dir_idx] = '0'
            self.walls[y][x] = "".join(w)
            
            nx, ny = x, y
            opp = -1
            
            if dir_idx == 0: ny += 1; opp = 2
            elif dir_idx == 1: nx -= 1; opp = 3
            elif dir_idx == 2: ny -= 1; opp = 0
            elif dir_idx == 3: nx += 1; opp = 1
            
            if 0 <= ny < len(self.walls) and 0 <= nx < len(self.walls[0]):
                w2 = list(self.walls[ny][nx])
                w2[opp] = '0'
                self.walls[ny][nx] = "".join(w2)

    # --- HELPERS DE MOVIMIENTO ---
    def can_move(self, from_pos, to_pos):
        """
        Comprueba si es legal mover desde from_pos hasta to_pos
        """
        fx, fy = from_pos
        tx, ty = to_pos
        dx = tx - fx
        dy = ty - fy

        # Deben ser adyacentes (Manhattan)
        if abs(dx) + abs(dy) != 1:
            return False

        # Mapear movimiento a dir_idx según convención: 0=Up,1=Left,2=Down,3=Right
        # Consideramos que to_pos está arriba si ty == fy - 1
        if dy == -1 and dx == 0:
            dir_idx = 0  # mover hacia arriba
        elif dx == -1 and dy == 0:
            dir_idx = 1  # moverse izquierda
        elif dy == 1 and dx == 0:
            dir_idx = 2  # moverse abajo
        elif dx == 1 and dy == 0:
            dir_idx = 3  # moverse derecha
        else:
            return False

        # Si hay pared, no puede pasar
        if self.has_wall(fx, fy, dir_idx):
            return False

        # Si existe puerta entre ambas celdas y está cerrada -> no puede pasar
        d_idx = self.get_door_index(from_pos, to_pos)
        if d_idx != -1:
            status = self.doors[d_idx][2]
            if status == 'Closed':
                return False

        return True

    # --- LÓGICA DE FUEGO ---
    def advance_fire(self):
        red_die = self.random.randint(1, 6)
        black_die = self.random.randint(1, 8)
        x = black_die - 1
        y = self.grid.height - red_die
        
        pos = (x, y)
        status = self.get_cell_status(pos)
        
        if self.printable:
            print(f"      🎲 Fuego en {pos}: {status}")
        
        if status == 'Empty':
            self.add_fire_or_smoke(pos, 1)
        elif status == 'Smoke':
            self.add_fire_or_smoke(pos, 2)
        elif status == 'Fire': 
            if self.printable:
                print("      💥 EXPLOSIÓN")
            self.resolve_explosion(pos)
        
        self.resolve_flashover()
        self.check_victims_and_pois_in_fire()

    def add_fire_or_smoke(self, pos, intensity):
        x, y = pos
        if intensity == 1:
            neighbors = self.grid.get_neighborhood((x, y), moore=False, include_center=False)
            for n in neighbors:
                if self.get_cell_status(n) == 'Fire':
                    intensity = 2
                    break

        if intensity == 2:
            self.check_poi_on_fire(x, y)
            cell_contents = self.grid.get_cell_list_contents(pos)
            for obj in cell_contents:
                if isinstance(obj, AgentBaseModel): 
                    self.send_to_ambulance(obj)
        found = False
        for f in self.fires:
            if f[0] == y and f[1] == x:
                f[2] = intensity
                found = True
                break
        if not found: 
            self.fires.append([y, x, intensity])

    def resolve_explosion(self, center_pos):
        cx, cy = center_pos
        directions = [(0, 1, 0), (-1, 0, 1), (0, -1, 2), (1, 0, 3)] 
        
        for dx, dy, widx in directions:
            dist = 1
            active = True
            while active:
                nx, ny = cx + (dx*dist), cy + (dy*dist)
                if not (0 <= ny < self.grid.height and 0 <= nx < self.grid.width): 
                    break
                
                px, py = cx + (dx*(dist-1)), cy + (dy*(dist-1))
                
                # Choca con Pared
                if self.has_wall(px, py, widx):
                    self.remove_wall(px, py, widx)
                    self.damage_taken += 1
                    active = False
                    break
                
                # Choca con Puerta Cerrada
                d_idx = self.get_door_index((px,py), (nx,ny))
                if d_idx != -1 and self.doors[d_idx][2] == 'Closed':
                    self.doors.pop(d_idx) # La puerta vuela
                    active = False
                    break

                # 3. Verifica contenido de la celda destino
                status = self.get_cell_status((nx, ny))
                if status != 'Fire':
                    self.add_fire_or_smoke((nx, ny), 2)
                    active = False
                else:
                    dist += 1

    def resolve_flashover(self):
        """
        Convierte humo adyacente a fuego en fuego (segunda línea de defensa).
        """
        fire_locs = {(f[1], f[0]) for f in self.fires if f[2] == 2}
        # Recorremos y acumulamos conversiones para no interferir con la iteración
        to_convert = []
        for i, f in enumerate(self.fires):
            if f[2] == 1:
                fy, fx = f[0], f[1]
                # Neighborhood devuelve (x,y)
                neighbors = self.grid.get_neighborhood((fx, fy), moore=False, include_center=False)
                if any(n in fire_locs for n in neighbors):
                    to_convert.append(i)
        for idx in to_convert:
            # reconfirmar que sigue siendo humo (no fue modificado)
            if 0 <= idx < len(self.fires) and self.fires[idx][2] == 1:
                self.fires[idx][2] = 2
                fx, fy = self.fires[idx][1], self.fires[idx][0]
                self.check_poi_on_fire(fx, fy)

    def send_to_ambulance(self, agent):
        if self.printable:
            print(f"      🚑 Agente {agent.id} herido -> Buscando Ambulancia.")
        
        if agent.carrying_victim:
            self.victims_lost += 1
            agent.carrying_victim = False
            if self.printable:
                print(f"      💀 La víctima que cargaba el Agente {agent.id} ha muerto.")

        width, height = self.grid.width, self.grid.height
        perimeter = []
        for x in range(width):
            perimeter.append((x, 0))            
            perimeter.append((x, height - 1)) 
        for y in range(1, height - 1):
            perimeter.append((0, y))            
            perimeter.append((width - 1, y))   
            
        target = None
        for pos in perimeter:
            if not self.is_fire(pos):
                target = pos
                break
        if target:
            self.grid.move_agent(agent, target)
        else:
            self.grid.move_agent(agent, (0,0))

    def get_cell_status(self, pos):
        x, y = pos
        for f in self.fires:
            if f[0] == y and f[1] == x: return 'Smoke' if f[2]==1 else 'Fire'
        return 'Empty'
    
    def is_fire(self, pos):
        return self.get_cell_status(pos) == 'Fire'

    def is_outside_building(self, pos):
        x, y = pos
        return (x == 0 or x == self.grid.width - 1 or 
                y == 0 or y == self.grid.height - 1)

    def remove_fire_completely(self, pos):
        x, y = pos
        for i, f in enumerate(self.fires):
            if f[0] == y and f[1] == x:
                self.fires.pop(i)
                if self.printable:
                    print(f"      🧯 Fuego removido completamente de {pos}")
                return

    def remove_smoke(self, pos):
        x, y = pos
        for i, f in enumerate(self.fires):
            if f[0] == y and f[1] == x and f[2] == 1:
                self.fires.pop(i)
                if self.printable:
                    print(f"      💨 Humo removido de {pos}")
                return

    def downgrade_fire(self, pos):
        x, y = pos
        for i, f in enumerate(self.fires):
            if f[0] == y and f[1] == x:
                if f[2] == 2:  # Fuego -> Humo
                    f[2] = 1
                    if self.printable:
                        print(f"      🔥→💨 Fuego convertido a humo en {pos}")
                else:  # Humo -> Remover
                    self.fires.pop(i)
                    if self.printable:
                        print(f"      💨 Humo removido de {pos}")
                return
            
    def check_game_over(self):
        if self.victims_saved >= 7: 
            self.running = False
            if self.printable:
                print("🏆 GANASTE")
        if self.victims_lost >= 4:
            self.running = False
            if self.printable:
                print("💀 PERDISTE")
        if self.damage_taken >= 24:
            self.running = False
            if self.printable:
                print("🏚️ DERRUMBE")

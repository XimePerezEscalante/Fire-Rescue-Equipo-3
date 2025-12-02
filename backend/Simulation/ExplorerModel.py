import random
import numpy as np
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
        
        self.replenish_pois()

        self.steps = 0
        self.pa = pa
        self.victims_saved = 0
        self.victims_lost = 0
        self.damage_taken = 0
        self.running = True
        self.printable = printable
        self.strategy = strategy

        self.agents_list = []
        
        # === POSICIONES DE AMBULANCIAS ===
        ambulance_positions = [(ep[1], ep[0]) for ep in self.entryPoints]
        
        # Dividir ambulancias: 2 para bomberos, 2 para rescatistas
        firefighter_spots = [ambulance_positions[0], ambulance_positions[1]]
        rescuer_spots = [ambulance_positions[2], ambulance_positions[3]]
        
        # === CREAR Y COLOCAR AGENTES ===
        firefighter_count = 0
        rescuer_count = 0
        
        for i in range(agents):
            if self.strategy == "intelligent":
                if i % 2 == 0:
                    # Bombero
                    pos = firefighter_spots[firefighter_count % len(firefighter_spots)]
                    a = AgentFireFighter(self, pa, i, printable=self.printable)
                    firefighter_count += 1
                else:
                    # Rescatista
                    pos = rescuer_spots[rescuer_count % len(rescuer_spots)]
                    a = AgenteRescuer(self, pa, i, printable=self.printable)
                    rescuer_count += 1
            else:
                # Random: usar cualquier ambulancia
                pos = ambulance_positions[i % len(ambulance_positions)]
                a = AgentBaseModel(self, pa, i, printable=self.printable)
            
            self.grid.place_agent(a, pos)
            self.agents_list.append(a)
            
            if self.printable:
                print(f"🚒 Agente {i} ({a.role}) en {pos}")

    def notify_observer(self):
        """ Método para que los agentes avisen que hicieron una acción """
        if self.on_step_callback:
            self.on_step_callback()

    def step(self):
        # --- VERIFICAR RESCATE EN ESQUINAS ---
        w, h = self.grid.width, self.grid.height
        corners = [(0, 0), (0, h-1), (w-1, 0), (w-1, h-1)]
        for agent in self.agents_list:
            if agent.carrying_victim and agent.pos in corners:
                # Lógica de salvar víctima
                agent.carrying_victim = False
                self.victims_saved += 1
                if self.printable:
                    print(f"¡Víctima salvada por Agente {agent.id} en {agent.pos}!")
        
        if not self.running: return

        for agent in self.agents_list:
            if not self.running: break
            agent.step()
            
            self.advance_fire()
            self.replenish_pois()
            self.notify_observer()
            self.check_game_over()
        
        self.steps += 1

    # --- PUERTAS ---
    def get_door_index(self, pos1, pos2):
        """
        Busca si hay una puerta entre pos1 y pos2.
        pos1 y pos2 son tuplas (x, y) en formato Mesa.
        Las puertas están guardadas como [(y1, x1), (y2, x2), status]
        """
        # Convertir a (y, x) para buscar
        y1, x1 = pos1[1], pos1[0]
        y2, x2 = pos2[1], pos2[0]
        
        for i, d in enumerate(self.doors):
            door_p1 = d[0]  # (y, x)
            door_p2 = d[1]  # (y, x)
            
            # Verificar ambas direcciones
            if ((door_p1 == (y1, x1) and door_p2 == (y2, x2)) or
                (door_p1 == (y2, x2) and door_p2 == (y1, x1))):
                return i
        
        return -1

    # --- POIS ---
    def replenish_pois(self):
        while len(self.pois) < 3:
            valid_spots = []
            for x in range(self.grid.width):
                for y in range(self.grid.height):
                    pos = (x, y)
                    if not self.is_fire(pos) and not self.is_poi(pos):
                        valid_spots.append(pos)
            if valid_spots:
                pos = self.random.choice(valid_spots)
                ptype = 'v' if random.random() > 0.5 else 'f'
                self.pois.append([pos[1], pos[0], ptype, False]) 
            else: break

    def is_poi(self, pos):
        x, y = pos
        return any(p[0] == y and p[1] == x for p in self.pois)

    def reveal_poi(self, pos):
        x, y = pos
        for p in self.pois:
            if p[0] == y and p[1] == x:
                if len(p) == 3: p.append(True)
                else: p[3] = True
                return 'Victim' if p[2] in ['v','Victim'] else 'FalseAlarm'
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
        """
        Verifica si hay un POI en la celda (x, y) que acaba de prenderse fuego.
        No importa si está revelado u oculto, el fuego lo afecta igual.
        """
        poi_removed = False
        # Iteramos hacia atrás para poder hacer pop sin romper el índice
        for i in range(len(self.pois) - 1, -1, -1):
            p = self.pois[i]
            py, px = p[0], p[1] 
            
            if px == x and py == y:
                p_type = p[2]
                
                # Caso: Es una víctima
                if p_type in ['Victim', 'v', 'V']:
                    self.victims_lost += 1
                    if self.printable:
                        print(f"💀 ¡Víctima perdida en el fuego en ({x}, {y})! Total perdidas: {self.victims_lost}")
                
                # Caso: Falsa alarma
                elif p_type in ['False Alarm', 'f', 'F']:
                    if self.printable:
                        print(f"🔥 Falsa alarma consumida por el fuego en ({x}, {y})")
                
                # Eliminamos el POI
                self.pois.pop(i)
                poi_removed = True
        
        # Si se quemó un POI, hay que reponerlo en otro lado (según reglas)
        if poi_removed and len(self.pois) < 3:
            self.replenish_pois()

    # --- PAREDES ---
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
            
            if dir_idx == 0: ny += 1; opp = 2 # Arriba -> Vecino Abajo
            elif dir_idx == 1: nx -= 1; opp = 3 # Izq -> Vecino Der
            elif dir_idx == 2: ny -= 1; opp = 0 # Abajo -> Vecino Arriba
            elif dir_idx == 3: nx += 1; opp = 1 # Der -> Vecino Izq
            
            if 0 <= ny < len(self.walls) and 0 <= nx < len(self.walls[0]):
                w2 = list(self.walls[ny][nx])
                w2[opp] = '0'
                self.walls[ny][nx] = "".join(w2)

    # --- LÓGICA DE FUEGO ---
    def advance_fire(self):
        red_die = self.random.randint(1, 6)    # Filas (1-6)
        black_die = self.random.randint(1, 8)  # Columnas (1-8)
        x = black_die - 1  # Columna
        y = self.grid.height - red_die  # Fila (invertida)
        
        pos = (x, y)
        status = self.get_cell_status(pos)
        
        if self.printable:
            print(f"      🎲 Fuego en {pos}: {status}")
        
        if status == 'Empty':
            self.add_fire_or_smoke(pos, 1) # Humo
        elif status == 'Smoke':
            self.add_fire_or_smoke(pos, 2) # Fuego
        elif status == 'Fire': 
            if self.printable:
                print("      💥 EXPLOSIÓN")
            self.resolve_explosion(pos)
        
        self.resolve_flashover()
        self.check_victims_and_pois_in_fire()

    def add_fire_or_smoke(self, pos, intensity):
        x, y = pos
        
        # Lógica simplificada: Si es fuego (2), verificamos POIs inmediatamente
        if intensity == 2:
            self.check_poi_on_fire(x, y)

        # Si hay agentes sobre el fuego, hay que sacarlos (regla opcional: enviar a ambulancia)
        if intensity == 2:
            cell_contents = self.grid.get_cell_list_contents(pos)
            for obj in cell_contents:
                if isinstance(obj, AgentBaseModel): 
                    self.send_to_ambulance(obj)
        
        # Actualizar lista de fuegos
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
        # Direcciones (dx, dy, wall_index)
        directions = [(0, 1, 0), (-1, 0, 1), (0, -1, 2), (1, 0, 3)] 
        
        for dx, dy, widx in directions:
            dist = 1
            active = True
            while active:
                nx, ny = cx + (dx*dist), cy + (dy*dist)
                
                # Fuera del mapa
                if not (0 <= ny < self.grid.height and 0 <= nx < self.grid.width): 
                    break
                
                px, py = cx + (dx*(dist-1)), cy + (dy*(dist-1))
                
                # 1. Choca con Pared
                if self.has_wall(px, py, widx):
                    self.remove_wall(px, py, widx)
                    self.damage_taken += 1
                    active = False
                    break
                
                # 2. Choca con Puerta Cerrada
                d_idx = self.get_door_index((px,py), (nx,ny))
                if d_idx != -1 and self.doors[d_idx][2] == 'Closed':
                    self.doors.pop(d_idx) # La puerta vuela
                    active = False
                    break

                # 3. Verifica contenido de la celda destino
                status = self.get_cell_status((nx, ny))
                if status != 'Fire':
                    # Si no es fuego, se convierte en fuego (la onda de choque para aquí)
                    self.add_fire_or_smoke((nx, ny), 2)
                    active = False
                else:
                    # Si YA es fuego, la onda sigue viajando
                    dist += 1

    def resolve_flashover(self):
        """
        Convierte humo adyacente a fuego en fuego.
        """
        fire_locs = {(f[1], f[0]) for f in self.fires if f[2] == 2}
        
        for f in self.fires:
            if f[2] == 1: # Si es humo
                fy, fx = f[0], f[1]
                neighbors = self.grid.get_neighborhood((fx, fy), moore=False, include_center=False)
                
                # Si tiene algún vecino que sea Fuego
                if any(n in fire_locs for n in neighbors):
                    f[2] = 2 # Se convierte en fuego
                    # IMPORTANTE: Verificar si había una víctima escondida en el humo
                    self.check_poi_on_fire(fx, fy)

    def send_to_ambulance(self, agent):
        if self.printable:
            print(f"      🚑 Agente {agent.id} herido -> Buscando Ambulancia.")
        
        # Si llevaba una víctima, esta muere al caer el bombero
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
        """Verifica si una posición está fuera del edificio (perímetro)"""
        x, y = pos
        return (x == 0 or x == self.grid.width - 1 or 
                y == 0 or y == self.grid.height - 1)

    def remove_fire_completely(self, pos):
        """Remueve fuego completamente del tablero (costo: 2 AP)"""
        x, y = pos
        for i, f in enumerate(self.fires):
            if f[0] == y and f[1] == x:
                self.fires.pop(i)
                if self.printable:
                    print(f"      🧯 Fuego removido completamente de {pos}")
                return

    def remove_smoke(self, pos):
        """Remueve humo del tablero (costo: 1 AP)"""
        x, y = pos
        for i, f in enumerate(self.fires):
            if f[0] == y and f[1] == x and f[2] == 1:
                self.fires.pop(i)
                if self.printable:
                    print(f"      💨 Humo removido de {pos}")
                return

    def downgrade_fire(self, pos):
        """Convierte fuego a humo (1 AP) o remueve humo existente"""
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

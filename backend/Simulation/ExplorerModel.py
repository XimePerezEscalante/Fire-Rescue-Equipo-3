from mesa import Model
from mesa.space import MultiGrid
from Simulation.AgentBaseModel import AgentBaseModel
from Simulation.AgentFireFighter import AgentFireFighter
from Simulation.AgentRescuer import AgenteRescuer
from Simulation.AuxFunctions import readMap
import random

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
        
        for i in range(agents):
            pos = (0, 0) # O tu lógica de posición inicial
            
            if self.strategy == "intelligent":
                # Ejemplo: Mitad apagadores, mitad rescate
                if i % 2 == 0:
                    a = AgentFireFighter(self, pa, i)
                else:
                    a = AgenteRescuer(self, pa, i)
            else:
                # Estrategia base (Random)
                a = AgentBaseModel(self, pa, i)
                
            self.grid.place_agent(a, pos)
            self.agents_list.append(a)

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
            self.check_game_over()
            
            if self.running:
                self.advance_fire()
                self.notify_observer()
                self.check_game_over()
        
        self.steps += 1

    # --- PUERTAS ---
    def get_door_index(self, pos1, pos2):
        p1 = (pos1[1], pos1[0]) 
        p2 = (pos2[1], pos2[0])
        for i, d in enumerate(self.doors):
            if (d[0] == p1 and d[1] == p2) or (d[0] == p2 and d[1] == p1):
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
                ptype = 'v' if random.random() > 0.4 else 'f'
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

    def check_poi_on_fire(self, x, y):
        """
        [CORREGIDO]
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
        if poi_removed:
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
        rx = self.random.randint(0, self.grid.width - 1)
        ry = self.random.randint(0, self.grid.height - 1)
        pos = (rx, ry)
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

    def add_fire_or_smoke(self, pos, intensity):
        x, y = pos
        
        # [CORREGIDO] Lógica simplificada: Si es fuego (2), verificamos POIs inmediatamente
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

    def downgrade_fire(self, pos):
        x, y = pos
        for i, f in enumerate(self.fires):
            if f[0] == y and f[1] == x:
                if f[2] == 2: f[2] = 1
                else: self.fires.pop(i)
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
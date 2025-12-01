from mesa import Model
from mesa.space import MultiGrid 
from mesa.datacollection import DataCollector
from Simulation.AuxFunctions import readMap, get_grid 
from Simulation.AgentBaseModel import AgentBaseModel
import numpy as np

# Grid general
# 0 -> vacio
# 1 -> fuego
# 2 -> comida 
# 3 -> agente

# Matriz de paredes
# 0 -> No hay
# 1 -> Daño 
# 2 -> Pared 

class ExplorerModel(Model):
    def __init__(self, width, height, agents, pa, random_fires=None, random_pois=None):
        super().__init__()
        
        self.grid = MultiGrid(width, height, torus=False)
        self.steps = 0 
        self.pa = pa 
        
        # 1. (Paredes y Puertas)
        mapData = readMap()
        self.walls = mapData['walls'] 
        self.doors = mapData['doors'] 
        self.entry_points = mapData['entryPoints']
        
        # 2. Configurar Fuegos (Carga desde el mapa o genera aleatoriamente)
        if random_fires is not None:
            self.fires = []
            self.spawn_random_items(amount=int(random_fires), item_type="fire")
        else:
            self.fires = mapData['fires']

        # 3. Configurar POIs (Carga desde el mapa o genera aleatoriamente)
        if random_pois is not None:
            self.pois = []
            self.spawn_random_items(amount=int(random_pois), item_type="poi")
        else:
            self.pois = mapData['pois']

        self.smoke = []  # Lista de posiciones con humo.
        self.victims_rescued = 0 # Víctimas rescatadas (Meta: 7).
        self.victims_lost = 0 # Víctimas perdidas (Límite de derrota: 4).
        self.damage_markers = 0 # Daño total al mapa (Límite de colapso: 24).
        self.false_alarms_found = 0 
        self.running = True 
        
        # Cálculo del ratio de víctimas para determinar si un POI es víctima o falsa alarma.
        total_victims = sum(1 for p in self.pois if p[2] == 'v')
        total_false = sum(1 for p in self.pois if p[2] == 'f')
        total_initial = total_victims + total_false
        self.victim_ratio = total_victims / total_initial if total_initial > 0 else 0.67
        
        # Estado de las puertas {door_key: True/False} (False = Cerrada, True = Abierta).
        self.door_states = {tuple(sorted(d)): False for d in self.doors}
        
        # Tracking de POIs revelados.
        self.revealed_pois = []  # [(y, x,)]
        
        # Control de fin de juego.
        self.game_over = False
        self.victory = False
        
        # Tracking de posiciones de agentes para recolección de datos.
        self.agents_positions = {}
        
        # Inicialización de Agentes: En los entry_points.
        initial_positions = self.random.sample(self.entry_points, min(agents, len(self.entry_points)))
        self.agent_list = [] 
        
        for i, entry in enumerate(initial_positions):
            pos = (entry[1], entry[0]) 
            agent = AgentBaseModel(self, pa, i)
            agent.carrying_victim = False
            agent.current_ap = pa # Inicializa AP.
            agent.dazed_in_prev_turn = False # (Dazed).
            self.grid.place_agent(agent, pos)
            self.agent_list.append(agent)
            self.agents_positions[i] = [pos]

        # Data Collector
        self.datacollector = DataCollector(
            model_reporters={
                "Grid": get_grid,
                "Steps": lambda m: m.steps,
                "Rescued": lambda m: m.victims_rescued,
                "Lost": lambda m: m.victims_lost,
                "Damage": lambda m: m.damage_markers
            }
        )

    def spawn_random_items(self, amount, item_type):
        """Genera items (fuego o POI) en celdas vacías disponibles."""
        empties = list(self.grid.empties)
        safe_amount = min(amount, len(empties))
        chosen_positions = self.random.sample(empties, safe_amount)
        
        for pos in chosen_positions:
            if item_type == "fire":
                # [y, x].
                self.fires.append([pos[1], pos[0]]) 
            elif item_type == "poi":
                # [y, x, tipo].
                self.pois.append([pos[1], pos[0], 'v'])

    # Funciones Auxiliares de Consulta
    def is_inside_map(self, y, x): # 
        """Checa si las coordenadas están dentro del límite del mapa y no son un entry point."""
        is_in_bounds = 0 <= x < self.grid.width and 0 <= y < self.grid.height
        is_entry = [y, x] in self.entry_points
        return is_in_bounds and not is_entry

    def get_fire_at(self, y, x):
        """Da True si hay fuego en (y, x)."""
        return [y, x] in self.fires

    def get_smoke_at(self, y, x):
        """Da True si hay humo en (y, x)."""
        return [y, x] in self.smoke

    def get_poi_at(self, y, x):
        """Da el POI no revelado si existe, de lo contrariosino None."""
        return next((poi for poi in self.pois if poi[0] == y and poi[1] == x), None)

    def is_adjacent_to_fire(self, y, x):
        """Checa si una celda es adyacente (Vecindad Von Neumann) a Fuego o Humo."""
        for dy, dx in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            ny, nx = y + dy, x + dx
            if self.get_fire_at(ny, nx) or self.get_smoke_at(ny, nx):
                return True
        return False

    def has_wall_between(self, y1, x1, y2, x2):
        """Checa si hay una pared sólida o una puerta CERRADA entre las dos celdas."""
        # Comprueba la existencia de una pared sólida
        wall_exists = any(set(w) == set([y1, x1, y2, x2]) for w in self.walls)
        # Comprueba la existencia de una puerta cerrada
        door_key = tuple(sorted([y1, x1, y2, x2]))
        door_exists = door_key in self.door_states
        is_door_closed = door_exists and not self.door_states.get(door_key, False)
        
        return wall_exists or is_door_closed

    def find_closest_entry_point(self, y, x):
        """
        Encuentra el punto de entrada [y, x] más cercano (distancia Manhattan).
        Solo en la parte de 'Dazed' (teletransporte instantáneo).
        """
        if not self.entry_points:
            return None
        current_pos = np.array([y, x])
        # Distancia Manhattan para elegir el Entry Point de reaparición.
        distances = [np.sum(np.abs(current_pos - np.array(ep))) for ep in self.entry_points]
        closest_index = np.argmin(distances)
        return self.entry_points[closest_index]
    
    # Funciones Auxiliares de Modificación de Estado
    def reveal_poi(self, y, x):
        """Revela un POI, determinando si es víctima o falsa alarma y actualizando listas."""
        poi = self.get_poi_at(y, x)
        if poi:
            self.pois.remove(poi)
            # Determina el tipo basado en el ratio de víctimas.
            poi_type = 'v' if self.random.random() <= self.victim_ratio else 'f'
            
            if poi_type == 'f':
                self.false_alarms_found += 1
            else:
                self.revealed_pois.append([y, x, 'v']) # Se añade a las víctimas en riesgo.

    def rescue_victim(self, y, x):
        """Sube el contador de rescate."""
        self.victims_rescued += 1
    
    def lose_victim(self, y, x):
        """Maneja la pérdida de una víctima (ya sea revelada o no) en un espacio con fuego."""
        # Intenta remover de víctimas reveladas
        victim_to_lose = next((v for v in self.revealed_pois if v[0] == y and v[1] == x and v[2] == 'v'), None)
        if victim_to_lose:
            self.revealed_pois.remove(victim_to_lose)
        else:
            # Si no es revelada, intenta remover de POIs no revelados.
            poi_to_lose = next((p for p in self.pois if p[0] == y and p[1] == x and p[2] == 'v'), None)
            if poi_to_lose:
                self.pois.remove(poi_to_lose)
                
        self.victims_lost += 1 # Sube el contador de víctimas perdidas.

    def add_damage_marker(self, y1, x1, y2, x2):
        """Añade un marcador de daño al contador global (límite 24)."""
        self.damage_markers += 1

    # --- Lógica de Daze Ambiental ---
    def check_daze_after_propagation(self):
        """
        FASE 2.5: Chequea si algún agente terminó en Fuego/Humo después de la propagación 
        y lo marca como Dazed para el siguiente turno.
        """
        for agent in self.agent_list:
            x, y = agent.pos
            is_fire = self.get_fire_at(y, x)
            is_smoke = self.get_smoke_at(y, x)
            
            # Si está en peligro y NO lleva víctima.
            if (is_fire or is_smoke) and not agent.carrying_victim:
                agent.dazedTimes += 1
                agent.dazed_in_prev_turn = True
                # No se toca el AP actual para que mantenga sus PA en el próximo turno.

    # Lógica de Fuego/Explosión
    def check_lost_pois_at(self, y, x):
        """Función para perder víctima en una celda (por Explosión)."""
        poi = self.get_poi_at(y, x)
        if poi and poi[2] == 'v':
            self.lose_victim(y, x)
            return
            
        victim_to_lose = next((v for v in self.revealed_pois if v[0] == y and v[1] == x and v[2] == 'v'), None)
        if victim_to_lose:
            self.revealed_pois.remove(victim_to_lose)
            self.victims_lost += 1

    # --- Función de Explosión ---
    def resolve_explosion(self, y, x):

        neighbors_coords = [(0, 1), (0, -1), (1, 0), (-1, 0)] # 4 direcciones: Derecha, Izquierda, Abajo, Arriba.

        for dy, dx in neighbors_coords:
            ny, nx = y + dy, x + dx
            
            # Ignora si el vecino está fuera del mapa.
            if not self.is_inside_map(ny, nx): continue 

            has_wall = self.has_wall_between(y, x, ny, nx)
            # Busca si hay una puerta entre las celdas.
            door_key = None
            for d in self.doors:
                if set(d) == set([y, x, ny, nx]): 
                    door_key = tuple(sorted(d)) 
                    break
            
            outcome = self.random.randint(1, 3) # Resultado aleatorio de la onda de choque (1, 2 o 3).

            if has_wall and outcome == 2:
                # Resultado 2: Añadir Daño (si hay pared)
                self.damage_markers += 1
                continue
            
            elif door_key and outcome == 3:
                # Resultado 3: Quitar Puerta Cerrada
                if door_key in self.door_states:
                    del self.door_states[door_key]
                self.doors = [d for d in self.doors if tuple(sorted(d)) != door_key]
                continue
            
            # Resultado 1: Poner Fuego (por default)
            if [ny, nx] in self.smoke:
                # Si hay humo, lo convierte en fuego.
                self.smoke.remove([ny, nx])
                if [ny, nx] not in self.fires:
                    self.fires.append([ny, nx])
            elif [ny, nx] not in self.fires:
                # Si no hay fuego ni humo, añade fuego.
                self.fires.append([ny, nx])

            # Pierde cualquier víctima/POI en la celda afectada por el fuego.
            self.check_lost_pois_at(ny, nx)

    def place_smoke(self, y, x):
        """Aplica la regla de propagación: Humo->Fuego, Fuego->Explosión, Vacío->Humo."""
        if not self.is_inside_map(y, x): return 
        
        # Si ya hay humo, se convierte en fuego (Humo -> Fuego).
        if self.get_smoke_at(y, x):
            self.smoke.remove([y, x])
            if [y, x] not in self.fires:
                self.fires.append([y, x])
            return
        
        # Si hay fuego, ocurre una EXPLOSION.
        if self.get_fire_at(y, x):
            self.resolve_explosion(y, x)
            return
        
        # Caso normal: poner humo (Vacío -> Humo).
        if [y, x] not in self.smoke:
            self.smoke.append([y, x])

    def resolve_flashover(self):
        """Implementa la regla de Flashover: el humo adyacente a fuego se convierte en fuego."""
        newly_fired = []
        for y, x in self.smoke[:]:
            if self.is_adjacent_to_fire(y, x):
                self.smoke.remove([y, x])
                if [y, x] not in self.fires:
                    newly_fired.append([y, x])
        
        self.fires.extend(newly_fired) # Añade los nuevos fuegos.


    def check_lost_pois(self):
        """Revisa POIs/víctimas perdidas en fuego."""
        # Revisa POIs sin revelar y víctimas reveladas.
        for poi in self.pois[:]:
            y, x = poi[0], poi[1]
            if self.get_fire_at(y, x) and poi[2] == 'v': self.lose_victim(y, x)
        
        for victim in self.revealed_pois[:]:
            y, x = victim[0], victim[1]
            if self.get_fire_at(y, x): self.lose_victim(y, x)


    def advance_fire(self):
        """Implementa la fase de Advance Fire (Tirar Dados, Colocar Humo/Fuego/Explosión, Flashover, Chequeo de Pérdidas)."""
        # 1. Roll Dice (simulación de tirar dados para poder tener una coordenada aleatoria).
        rand_y = self.random.randint(0, self.grid.height - 1)
        rand_x = self.random.randint(0, self.grid.width - 1)
        
        # 2. Place Smoke (o fuego, o explosión) en la celda aleatoria.
        self.place_smoke(rand_y, rand_x)
        
        # 3. Resolve Flashover
        self.resolve_flashover()
        
        # 4. Check Lost POIs
        self.check_lost_pois()


    def replenish_poi(self):
        """Implementa la regla de Replenish POI: asegurar que haya al menos 3 POIs en el tablero."""
        total_pois_on_board = len(self.pois) + len(self.revealed_pois)
        
        if total_pois_on_board < 3:
            
            # Buscar una celda vacía y segura al azar que esté dentro del mapa.
            while True:
                rand_y = self.random.randint(0, self.grid.height - 1)
                rand_x = self.random.randint(0, self.grid.width - 1)
                
                # Criterios: dentro del mapa y sin fuego/humo/POI.
                if (self.is_inside_map(rand_y, rand_x) and 
                    not self.get_fire_at(rand_y, rand_x) and
                    not self.get_smoke_at(rand_y, rand_x) and
                    not self.get_poi_at(rand_y, rand_x)):
                    break
            
            # El POI se añade como no revelado ('v' para el replenish).
            self.pois.append([rand_y, rand_x, 'v'])


    def check_game_end(self):
        """Checa las condiciones de victoria o derrota."""
        # Condición de Victoria: 7 Víctimas rescatadas.
        if self.victims_rescued >= 7:
            self.game_over = True
            self.victory = True
            return

        # Condición de Derrota: 4 Víctimas perdidas.
        if self.victims_lost >= 4:
            self.game_over = True
            self.victory = False
            return

        # Condición de Derrota: Colapso del mapa (24 marcadores de daño).
        if self.damage_markers >= 24:
            self.game_over = True
            self.victory = False
            return
            

    def step(self):
        if self.game_over:
            self.running = False
            return
        
        self.steps += 1
        self.datacollector.collect(self)
        
        # FASE 1: Agentes actúan (Orden aleatorio)
        self.random.shuffle(self.agent_list)
        
        for agent in self.agent_list:
            # Resetea el PA al inicio del turno.
            agent.current_ap = self.pa
            
            # DAZE: Si fue aturdido, se mueve a la base y mantiene sus AP.
            agent.resolve_daze_movement()
            
            # Revelar POI si el agente está en la celda (antes de que actúe, 0 AP).
            x, y = agent.pos
            poi = self.get_poi_at(y, x)
            if poi: self.reveal_poi(y, x)
            
            # El agente ejecuta su lógica de acciones.
            agent.step()
            
            self.agents_positions[agent.id].append(agent.pos)
        
        # FASE 2: Advance Fire
        self.advance_fire()
        
        # FASE 2.5: Check Daze after fire propagation
        self.check_daze_after_propagation() 
        
        # FASE 3: Replenish POI
        self.replenish_poi()
        
        # FASE 4: Check Game End
        self.check_game_end()
        
    def is_all_clean(self):
        """Checa si el juego ha terminado."""
        return self.game_over
from mesa import Model
from mesa.space import SingleGrid
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
        
        self.grid = SingleGrid(width, height, torus=False)
        self.steps = 0
        self.pa = pa
        
        # 1. Cargar Estructura Fija (Paredes y Puertas siempre del TXT)
        mapData = readMap()
        self.walls = mapData['walls']
        self.doors = mapData['doors']
        
        # 2. Configurar Fuegos (Híbrido)
        if random_fires is not None:
            self.fires = []
            self.spawn_random_items(amount=int(random_fires), item_type="fire")
        else:
            self.fires = mapData['fires']

        # 3. Configurar POIs (Híbrido)
        if random_pois is not None:
            self.pois = []
            self.spawn_random_items(amount=int(random_pois), item_type="poi")
        else:
            self.pois = mapData['pois']

        self.agents_positions = {}
        
        # Inicialización de Agentes
        self.agents = self.random.sample(self.grid.empties, agents)
        for i, pos in enumerate(self.agents):
            agent = AgentBaseModel(self, pa, i)
            self.grid.place_agent(agent, pos)
            self.agents_positions[i] = [pos]

        self.datacollector = DataCollector(
            model_reporters={
                "Grid": get_grid,
                "Steps": lambda m: m.steps}
        )

    def spawn_random_items(self, amount, item_type):
        """Genera items en celdas vacías (respetando paredes implícitas en grid)"""
        # Obtenemos celdas vacías disponibles
        empties = list(self.grid.empties)
        
        # Seleccionamos N posiciones aleatorias
        # Nota: Si pides más items que celdas vacías, esto dará error.
        safe_amount = min(amount, len(empties))
        chosen_positions = self.random.sample(empties, safe_amount)
        
        for pos in chosen_positions:
            x, y = pos # Mesa devuelve (x, y) o (y, x) según config, SingleGrid usa (x,y) normalmente
            
            if item_type == "fire":
                # Guardamos como lista [y, x] para compatibilidad con tu código legacy
                self.fires.append([pos[1], pos[0]]) 
            elif item_type == "poi":
                self.pois.append([pos[1], pos[0], 'v'])

    def step(self):
        self.datacollector.collect(self)
        # self.schedule.step() # Si usaras scheduler
        # Tu lógica manual de movimiento:
        agents_list = list(self.grid.get_all_cell_contents())
        # Filtrar solo agentes
        agents_list = [a for a in agents_list if isinstance(a, AgentBaseModel)]
        self.random.shuffle(agents_list)
        
        for agent in agents_list:
            agent.step()
            self.agents_positions[agent.id].append(agent.pos)
            
        self.steps += 1

    def is_all_clean(self):
        return self.steps >= 50 # Tu condición de parada
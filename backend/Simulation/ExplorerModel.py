from mesa import Model
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
from AuxFunctions import get_grid
from AgentBaseModel import AgenteBaseModel
from AuxFunctions import readMap
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
    def __init__(self, width=8, height=6, agents=5, pa=100):
        super().__init__()

        # Parámetros del sistema
        self.grid = SingleGrid(width, height, torus=False)
        self.steps = 0
        self.pa = pa
        
        mapData = readMap()
        self.walls = mapData['walls']
        self.fires = mapData['fires'] # Lista de coordenadas de fuego
        self.pois = mapData['pois']   # Lista de coordenadas de POIs
        self.doors = mapData['doors'] # <--- AGREGAR ESTA LÍNEA

        # Crear matriz de recursos -> Sustituir valores de pois
        self.cells = np.zeros((width, height), dtype=int)
        # count = int(resources)
        # while count > 0:
        #     x = self.random.randrange(width)
        #     y = self.random.randrange(height)
        #     if self.grid.is_cell_empty((x, y)) and (x,y) != self.center:
        #         self.cells[x][y] = 1
        #         count -= 1

        self.center = (0, 0)  # Define dónde está la base (coordenada x, y)
        self.cells = np.zeros((width, height), dtype=int) # Matriz para comida/fuego
        # ----------------------------

        # Crear agentes exploradores
        i = 0
        while i < agents:
            x = self.random.randrange(width) 
            
            if x > 0:
                y = 0
            else:
                # CORRECCIÓN: Usar randrange(height)
                y = self.random.randrange(height)
            if self.grid.is_cell_empty((x, y)):
                agent = AgenteBaseModel(self, pa)
                self.grid.place_agent(agent, (x, y))
                self.agents.add(agent)
                i += 1

        # Recolector de datos
        self.datacollector = DataCollector(
            model_reporters={
                "Grid": get_grid,
                "Steps": lambda m: m.steps,
            }
        )

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")
        self.steps += 1

    def is_all_clean(self):
        return self.steps >= 50

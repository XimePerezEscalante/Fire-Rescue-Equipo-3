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
        self.doors = mapData['doors'] # Puertas
        self.agents_positions = {}

        # Crear matriz de recursos -> Sustituir valores de pois
        self.cells = np.zeros((width, height), dtype=int)

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
                agent = AgentBaseModel(self, pa, i)
                self.grid.place_agent(agent, (x, y))
                self.agents.add(agent)
                i += 1

        for agent in self.agents:
            self.agents_positions[agent.unique_id] = [agent.pos]
        # Recolector de datos
        self.datacollector = DataCollector(
            model_reporters={
                "Grid": get_grid,
                "StepsPerAgent": lambda m: m.agents_positions,
                "Steps": lambda m: m.steps,
            },
            # agent_reporters={"Efficiency":lambda agent : })
        )

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")
        # print(self.agents_positions)
        for agent in self.agents:
            self.agents_positions[agent.unique_id].append(agent.pos)
        self.steps += 1

    def is_all_clean(self):
        return self.steps >= 50


if __name__ == '__main__':
    expM = ExplorerModel()
    print(f'walls: \n{expM.walls}\n')
    print(f'POIS: \n{expM.pois}\n')
    print(f'Fires: \n{expM.fires}\n')
    print(f'Doors: \n{expM.doors}\n')


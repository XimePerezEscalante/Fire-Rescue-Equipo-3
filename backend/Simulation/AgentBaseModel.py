from mesa import Agent
import numpy as np

class AgenteBaseModel(Agent):
    def __init__(self, model, pa):
        super().__init__(model)
        self.model = model
        #Atributos del agente
        self.pa = pa
        self.extraPA = 0
        self.totalPA = self.pa + self.extraPA
        self.hasFood = False
        #Para estadisticas
        self.timeToSavePOI = None # Lista con tiempos en los que salva a POIs
        self.fireExtinguish = 0
        self.dazedTimes = 0
        self.cellsVisited = 0

    def move(self):
        possiblePositions = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
        while True:
            choice = np.random.choice(possiblePositions)
            index = possiblePositions.index(choice)
            if self.model.walls[self.pos[0]][self.pos[1]][index] == 0:
                self.model.grid.move_agent(self, choice)
                self.pa -= 1
                break
            else:
                possiblePositions.remove(choice)

    def step(self):
        self.move()
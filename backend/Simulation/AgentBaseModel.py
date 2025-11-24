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

    def check_door(self, next_pos):
        curr_x, curr_y = self.pos
        next_x, next_y = next_pos
        
        # Creamos los pares de coordenadas numéricas
        # Opción 1: Paso de Actual -> Siguiente
        pair1 = [curr_y, curr_x, next_y, next_x]
        # Opción 2: Paso de Siguiente -> Actual (Bidireccional)
        pair2 = [next_y, next_x, curr_y, curr_x]
        
        if hasattr(self.model, 'doors'):
            for door in self.model.doors:
                # 'door' ahora es una lista de 4 enteros [r1, c1, r2, c2]
                if door == pair1 or door == pair2:
                    return True
        return False

    def move(self):
        # (El resto de tu función move se queda igual, 
        # asegúrate de llamar a self.check_door(choice) donde lo pusimos antes)
        possible_steps = list(self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False
        ))
        np.random.shuffle(possible_steps)

        for step in possible_steps:
            curr_x, curr_y = self.pos
            next_x, next_y = step
            dx = next_x - curr_x
            dy = next_y - curr_y

            wall_index = -1
            if dy == -1: wall_index = 0
            elif dx == -1: wall_index = 1
            elif dy == 1: wall_index = 2
            elif dx == 1: wall_index = 3
            
            # Verificación de pared
            has_wall = False
            if 0 <= curr_y < len(self.model.walls) and 0 <= curr_x < len(self.model.walls[0]):
                current_walls = self.model.walls[curr_y][curr_x]
                if current_walls[wall_index] == '1':
                    has_wall = True
            
            # Chequeo de Puertas
            if has_wall and self.check_door(step):
                has_wall = False

            if not has_wall and self.model.grid.is_cell_empty(step):
                self.model.grid.move_agent(self, step)
                self.pa -= 1
                break

    def step(self):
        self.move()
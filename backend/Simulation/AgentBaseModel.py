from mesa import Agent
import numpy as np

class AgentBaseModel(Agent):
    """
    Clase base para los agentes (bomberos) en la simulación,
    implementando la lógica de movimiento y aturdimiento personalizada.
    """
    def __init__(self, model, pa, unique_id):
        super().__init__(unique_id, model)
        
        # Propiedades del agente
        self.pa = pa
        self.current_ap = pa
        self.carrying_victim = False
        self.dazedTimes = 0
        self.dazed_in_prev_turn = False 
    
    # --- Métodos de Ayuda ---
    
    def get_movement_cost(self, y, x):

        is_fire = self.model.get_fire_at(y, x)
        is_poi = self.model.get_poi_at(y, x)
        
        if is_fire or is_poi:
            return 2
        elif self.model.get_smoke_at(y, x):
            return 1
        else:
            return 1

    def get_neighbors(self):
        return self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)

    # --- Lógica de Acciones ---

    def resolve_daze_movement(self):
        if self.dazed_in_prev_turn:
            
            # Mover al Entry Point más cercano
            entry = self.model.find_closest_entry_point(self.pos[1], self.pos[0])
            if entry:
                new_pos = (entry[1], entry[0]) 
                self.model.grid.move_agent(self, new_pos)
            
            self.dazed_in_prev_turn = False 
            return True
        return False

    def move(self, new_pos):
        """
        Mueve el agente a una nueva posición.
        """
        x, y = self.pos # Posición actual (x, y)
        nx, ny = new_pos 
        
        # 1. Chequeo de Barreras
        if self.model.has_wall_between(y, x, ny, nx):
            return False
            
        # 2. Determinar Costo de AP 
        cost = self.get_movement_cost(ny, nx)
        
        # 3. Mover si hay suficiente AP
        if self.current_ap >= cost:
            self.current_ap -= cost
            self.model.grid.move_agent(self, new_pos)
            
            return True
            
        return False
        
    def extinguish_hazard(self, y, x):
        if self.model.get_fire_at(y, x):
            cost = 2
            if self.current_ap < cost: return False
            
            self.model.fires.remove([y, x])
            self.current_ap -= cost
            return True
            
        elif self.model.get_smoke_at(y, x):
            cost = 1
            if self.current_ap < cost: return False
            
            self.model.smoke.remove([y, x])
            self.current_ap -= cost
            return True
        
        return False

    
    def step(self):

        while self.current_ap > 0:
            current_y, current_x = self.pos[1], self.pos[0]
            actions = [] 

            if self.model.get_fire_at(current_y, current_x) or self.model.get_smoke_at(current_y, current_x):
                if self.current_ap >= 1: 
                    actions.append(('extinguish', (current_y, current_x)))

            
            neighbors = self.get_neighbors()
            
            for nx, ny in neighbors:
                
                if self.model.get_fire_at(ny, nx) or self.model.get_smoke_at(ny, nx):
                    if self.current_ap >= 1:
                        actions.append(('extinguish', (ny, nx)))

                cost = self.get_movement_cost(ny, nx)
                if self.current_ap >= cost:
                    actions.append(('move', ((nx, ny), cost)))
            
            
            
            if not actions:
                break 

            action_type, args = self.model.random.choice(actions)
            
            if action_type == 'extinguish':
                self.extinguish_hazard(args[0], args[1]) 
            
            elif action_type == 'move':
                new_pos, cost = args
                self.move(new_pos)
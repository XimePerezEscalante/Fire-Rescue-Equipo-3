from mesa import Agent
import random

class AgentBaseModel(Agent):
    def __init__(self, model, pa, id, printable=False):
        super().__init__(model)
        self.model = model
        self.id = id
        self.printable = printable
        self.pa = pa
        self.totalPA = pa 
        self.carrying_victim = False
        self.role = "Base"
        
        # Estadísticas simples
        self.steps_taken = 0

    def step(self):
        self.pa = self.totalPA 

        while self.pa > 0:
            neighbors = self.get_valid_neighbors()
            if not neighbors:
                break

            target_pos = self.decision_choose_movement(neighbors)
            action_taken = self.attempt_action(target_pos)
            
            if action_taken:
                # Si hizo algo, avisamos al modelo para registrar el "micro-paso"
                self.model.notify_observer()
            else:
                break

    # --- DECISIONES ---
    def decision_choose_movement(self, possible_steps):
        return random.choice(possible_steps)

    def decision_extinguish_fire(self):
        return random.choice([True, False])

    def decision_chop_wall(self):
        return random.choice([True, False])
    
    def decision_open_door(self):
        return random.choice([True, False])

    def decision_reveal_poi(self):
        return random.choice([True, False])

    def decision_rescue_victim(self):
        return random.choice([True, False])

    # --- ACCIONES ---
    def get_valid_neighbors(self):
        # MultiGrid permite obtener vecindad igual que SingleGrid
        return self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)

    def attempt_action(self, target_pos):
        curr_pos = self.pos
        cx, cy = curr_pos
        tx, ty = target_pos
        
        # Dirección
        wall_dir = -1
        if ty > cy: wall_dir = 0 
        elif tx > cx: wall_dir = 1 
        elif ty < cy: wall_dir = 2 
        elif tx < cx: wall_dir = 3 

        # 1. OBSTÁCULOS (Paredes y Puertas)
        if self.model.has_wall(cx, cy, wall_dir):
            if self.printable:
                print(f"   🧱 Agente {self.id}: Pared detectada hacia {target_pos}.")
            if self.pa >= 2 and self.decision_chop_wall():
                if self.printable:
                    print(f"   🪓 Agente {self.id}: Rompiendo pared (-2 PA).")
                self.model.remove_wall(cx, cy, wall_dir)
                self.model.damage_taken += 1
                self.pa -= 2
                return True
            return False

        door_idx = self.model.get_door_index(curr_pos, target_pos)
        if door_idx != -1:
            if self.model.doors[door_idx][2] == 'Closed':    
                if self.printable:
                    print(f"   🚪 Agente {self.id}: Puerta cerrada hacia {target_pos}.")
                if self.pa >= 1 and self.decision_open_door():
                    if self.printable:
                        print(f"   👐 Agente {self.id}: Abriendo puerta (-1 PA).")
                    self.model.doors[door_idx][2] = 'Open'
                    self.pa -= 1
                    return True 
                else:
                    return False 

        # 2. PELIGROS (Fuego) - Regla: Debe apagar para entrar
        cell_status = self.model.get_cell_status(target_pos)
        if cell_status in ['Fire', 'Smoke']:
            if self.printable:
                print(f"   🔥 Agente {self.id}: {cell_status} en destino {target_pos}.")
            if self.pa >= 1:
                if self.decision_extinguish_fire():
                    if self.printable:
                        print(f"   💦 Agente {self.id}: Extinguiendo desde fuera (-1 PA).")
                    self.model.downgrade_fire(target_pos)
                    self.pa -= 1
                    return True 
                else:
                    return False
            else:
                return False

        # 3. MOVIMIENTO
        if self.pa >= 1:
            if self.printable:
                print(f"   🦶 Agente {self.id}: Moviéndose a {target_pos}.")
            self.model.grid.move_agent(self, target_pos)
            self.pa -= 1
            
            # Interacción con POI
            if self.model.is_poi(target_pos):
                if self.printable:
                    print(f"   ❓ Agente {self.id}: POI encontrado en {target_pos}.")
                if self.decision_reveal_poi():
                    poi_type = self.model.reveal_poi(target_pos)
                    if self.printable:
                        print(f"   👀 Agente {self.id}: Revelado -> {poi_type}")
                    
                    if poi_type == 'Victim':
                        # Lógica de rescate
                        if not self.carrying_victim and self.decision_rescue_victim():
                            if self.printable:
                                print(f"   🚑 Agente {self.id}: ¡Víctima recogida! Llévala a la ambulancia.")
                            self.carrying_victim = True
                            self.model.remove_poi(target_pos)
                            self.model.replenish_pois() 
                            
                        else:
                            pass # La deja ahí si decide no rescatar
                    else:
                        if self.printable:
                            print(f"   💨 Agente {self.id}: Falsa alarma.")
                        self.model.remove_poi(target_pos)
                        self.model.replenish_pois()
            return True
        
        return False
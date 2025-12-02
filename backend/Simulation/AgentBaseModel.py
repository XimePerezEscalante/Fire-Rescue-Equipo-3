from mesa import Agent
import random

class AgentBaseModel(Agent):
    def __init__(self, model, pa, id, printable=False):
        super().__init__(model)
        self.model = model
        self.id = id
        self.printable = printable
        
        # Gestión de Puntos de Acción (PA)
        # CORRECCIÓN: Inicializamos en 0. El step() añade los PA del turno.
        # Esto evita que en el turno 1 tengan el doble de PA (Inicial + Recarga).
        self.pa = 0 
        self.totalPA = pa 
        self.max_pa_savings = 4 
        
        self.carrying_victim = False
        self.role = "Base"
        
        # Estadísticas simples
        self.steps_taken = 0
    
    def step(self):
        # Regla: Recargar PA (maximo pa del turno + guardados)
        self.pa = min(self.pa + self.totalPA, self.totalPA + self.max_pa_savings)

        while self.pa > 0:
            neighbors = self.get_valid_neighbors()
            if not neighbors:
                break

            target_pos = self.decision_choose_movement(neighbors)
            
            # Predecimos costo
            cost = self.predict_action_cost(self.pos, target_pos)
            
            if self.pa < cost:
                if self.printable:
                    print(f"   🛑 Agente {self.id}: Guarda {self.pa} PA (Requiere {cost}).")
                break
            
            action_taken = self.attempt_action(target_pos)
            
            if action_taken:
                self.model.notify_observer()
            else:
                # Si action_taken es False, significa que intentó algo pero falló (ej. no quiso romper pared)
                # Rompemos el bucle para evitar bucles infinitos intentando la misma acción fallida
                break
        if self.model.get_cell_status(self.pos) == 'Fire':
            # Enviar a ambulancia (knocked down)
            self.model.send_to_ambulance(self)
    
    def predict_action_cost(self, curr_pos, target_pos):
        cx, cy = curr_pos
        tx, ty = target_pos
        
        wall_dir = self._get_direction_index(cx, cy, tx, ty)

        # 1. Costo de Pared
        if self.model.has_wall(cx, cy, wall_dir):
            return 2 
            
        # 2. Costo de Puerta Cerrada
        door_idx = self.model.get_door_index(curr_pos, target_pos)
        if door_idx != -1 and self.model.doors[door_idx][2] == 'Closed':
            return 1 
            
        # 3. Costo de Peligros
        cell_status = self.model.get_cell_status(target_pos)
        if cell_status in ['Fire', 'Smoke']:
            return 1
            
        # 4. Costo de Movimiento
        return 2 if self.carrying_victim else 1

    # --- DECISIONES ---
    def decision_choose_movement(self, possible_steps):
        return random.choice(possible_steps)

    def decision_extinguish_fire(self):
        return random.choice([True, False])
    
    def decision_complete_extinguish(self):
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
        return self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
    
    def _get_direction_index(self, cx, cy, tx, ty):
        """ Helper para obtener el índice de dirección (0:Up, 1:Right, 2:Down, 3:Left) """
        if ty > cy: return 0 
        elif tx > cx: return 1 
        elif ty < cy: return 2 
        elif tx < cx: return 3 
        return -1
    
    def is_outside_building(self, pos):
        x, y = pos
        return (x == 0 or x == self.grid.width - 1 or 
                y == 0 or y == self.grid.height - 1)

    # --- ACCIONES ---
    def attempt_action(self, target_pos):
        curr_pos = self.pos
        cx, cy = curr_pos
        tx, ty = target_pos
        
        wall_dir = self._get_direction_index(cx, cy, tx, ty)

        # 1. OBSTÁCULOS: PAREDES
        if self.model.has_wall(cx, cy, wall_dir):
            if self.printable: print(f"   🧱 Agente {self.id}: Pared hacia {target_pos}.")
            
            if self.pa >= 2 and self.decision_chop_wall():
                if self.printable: print(f"   🪓 Agente {self.id}: Rompiendo pared (-2 PA).")
                self.model.remove_wall(cx, cy, wall_dir)
                self.model.damage_taken += 1
                self.pa -= 2
                return True
            
            return False

        # 1.1 OBSTÁCULOS: PUERTAS
        door_idx = self.model.get_door_index(curr_pos, target_pos)
        if door_idx != -1:
            if self.model.doors[door_idx][2] == 'Closed':    
                if self.printable: print(f"   🚪 Agente {self.id}: Puerta cerrada.")
                if self.pa >= 1 and self.decision_open_door():
                    if self.printable: print(f"   👍 Agente {self.id}: Abriendo puerta (-1 PA).")
                    self.model.doors[door_idx][2] = 'Open'
                    self.pa -= 1
                    return True
                else:
                    return False

        # 2. PELIGROS (Fuego/Humo)
        cell_status = self.model.get_cell_status(target_pos)
        
        if cell_status == 'Fire':
            if self.printable: print(f"   🔥 Agente {self.id}: Fuego detectado.")
            
            if not self.decision_extinguish_fire():
                return False
            
            # Decidir si extinguir completamente o solo convertir a humo
            if self.decision_complete_extinguish() and self.pa >= 2:
                if self.printable: print(f"   💦 Agente {self.id}: Extinguiendo completamente (-2 PA).")
                self.model.remove_fire_completely(target_pos)
                self.pa -= 2
                return True
            elif self.pa >= 1:
                if self.printable: print(f"   💦 Agente {self.id}: Convirtiendo fuego a humo (-1 PA).")
                self.model.downgrade_fire(target_pos)
                self.pa -= 1
                return True
            else:
                return False
        
        elif cell_status == 'Smoke':
            if self.printable: print(f"   💨 Agente {self.id}: Humo detectado.")
            
            if self.pa >= 1 and self.decision_extinguish_fire():
                if self.printable: print(f"   💦 Agente {self.id}: Removiendo humo (-1 PA).")
                self.model.remove_smoke(target_pos)
                self.pa -= 1
                return True
            else:
                return False

        # 3. MOVIMIENTO FINAL
        move_cost = 2 if self.carrying_victim else 1

        if self.pa >= move_cost:
            if self.printable: print(f"   🦶 Agente {self.id}: Moviéndose a {target_pos} (Costo: {move_cost}).")
            self.model.grid.move_agent(self, target_pos)
            self.pa -= move_cost
            self.steps_taken += 1
            
            # --- SALVAMENTO (REGLAS FAMILIARES) ---
            # En reglas familiares: llevar víctima FUERA del edificio
            if self.carrying_victim and self.model.is_outside_building(target_pos):
                if self.printable: print(f"   🎉 Agente {self.id}: ¡VÍCTIMA SALVADA!")
                self.carrying_victim = False
                self.model.victims_saved += 1
            
            # --- POI ---
            if self.model.is_poi(target_pos):
                if self.printable: print(f"   ❓ Agente {self.id}: POI encontrado.")
                if self.decision_reveal_poi():
                    poi_type = self.model.reveal_poi(target_pos)
                    if self.printable: print(f"   👀 Agente {self.id}: Revelado -> {poi_type}")
                    
                    if poi_type == 'Victim':
                        if not self.carrying_victim and self.decision_rescue_victim():
                            if self.printable: print(f"   🚑 Agente {self.id}: ¡Víctima recogida!")
                            self.carrying_victim = True
                            self.model.remove_poi(target_pos)
                            # No reponer POI aquí, se hace al final del turno
                    else:
                        if self.printable: print(f"   👻 Agente {self.id}: Falsa alarma.")
                        self.model.remove_poi(target_pos)
            
            return True
        
        return False
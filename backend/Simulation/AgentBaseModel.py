from mesa import Agent
import random

class AgentBaseModel(Agent):
    def __init__(self, model, pa, id, printable=False):
        """
        Constructor del agente base. Inicializa sus atributos principales, puntos de acción (PA) y estadísticas.
        
        Parámetros:
            model (Model): Referencia al modelo de simulación principal.
            pa (int): Cantidad máxima de Puntos de Acción que recibe por turno.
            id (int): Identificador único del agente.
            printable (bool): Bandera para habilitar impresiones de depuración en consola.
        Retorna:
            None
        """
        super().__init__(model)
        self.model = model
        self.id = id
        self.printable = printable
        self.pa = 0 
        self.totalPA = pa 
        self.max_pa_savings = 4 
        self.carrying_victim = False
        self.role = "Base"
        self.steps_taken = 0
        self.movement_count = 0
    
    def step(self):
        """
        Ejecuta el ciclo de vida del agente durante un turno. Recarga PA y ejecuta un bucle de acciones hasta agotar los puntos o no tener movimientos válidos.
        
        Parámetros:
            Ninguno.
        Retorna:
            None
        """
        self.pa = min(self.pa + self.totalPA, self.totalPA + self.max_pa_savings)
        while self.pa > 0:
            neighbors = self.get_valid_neighbors()
            if not neighbors:
                break
            target_pos = self.decision_choose_movement(neighbors)
            cost = self.predict_action_cost(self.pos, target_pos)
            if self.pa < cost:
                if self.printable:
                    print(f"   🛑 Agente {self.id}: Guarda {self.pa} PA (Requiere {cost}).")
                break
            action_taken = self.attempt_action(target_pos)
            if action_taken:
                self.model.notify_observer()
            else:
                break
        if self.model.get_cell_status(self.pos) == 'Fire':
            self.model.send_to_ambulance(self)
    
    def predict_action_cost(self, curr_pos, target_pos):
        """
        Calcula el costo estimado de PA necesario para moverse a una casilla adyacente, considerando obstáculos (paredes, puertas) y peligros (fuego, humo).
        
        Parámetros:
            curr_pos (tuple): Coordenadas actuales (x, y).
            target_pos (tuple): Coordenadas objetivo (x, y).
        Retorna:
            int: El costo en Puntos de Acción para realizar el movimiento.
        """
        cx, cy = curr_pos
        tx, ty = target_pos
        
        wall_dir = self._get_direction_index(cx, cy, tx, ty)

        # Costo de Pared
        if self.model.has_wall(cx, cy, wall_dir):
            return 2 
            
        # Costo de Puerta Cerrada
        door_idx = self.model.get_door_index(curr_pos, target_pos)
        if door_idx != -1 and self.model.doors[door_idx][2] == 'Closed':
            return 1 
            
        # Costo de Peligros
        cell_status = self.model.get_cell_status(target_pos)
        if cell_status in ['Fire', 'Smoke']:
            return 1
            
        # Costo de Movimiento
        return 2 if self.carrying_victim else 1

    # --- DECISIONES ---
    def decision_choose_movement(self, possible_steps):
        """
        Decide cuál será el siguiente movimiento entre las casillas disponibles.
        En la clase base, esta decisión es puramente estocástica (aleatoria).
        
        Parámetros:
            possible_steps (list): Lista de tuplas con las coordenadas adyacentes válidas.
        Retorna:
            tuple: Coordenada (x, y) elegida para moverse.
        """
        return random.choice(possible_steps)

    def decision_extinguish_fire(self):
        """
        Decide si el agente intentará extinguir el fuego presente en la casilla objetivo.
        En la clase base, retorna una decisión aleatoria.
        
        Parámetros:
            Ninguno.
        Retorna:
            bool: True si decide extinguir, False en caso contrario.
        """
        return random.choice([True, False])
    
    def decision_complete_extinguish(self):
        """
        Decide si el agente gastará puntos extra para extinguir el fuego completamente o solo reducirlo a humo.
        En la clase base, retorna una decisión aleatoria.
        
        Parámetros:
            Ninguno.
        Retorna:
            bool: True si decide extinguir completamente, False si solo reduce a humo.
        """
        return random.choice([True, False])

    def decision_chop_wall(self):
        """
        Decide si el agente romperá una pared que bloquea su camino.
        En la clase base, retorna una decisión aleatoria.
        
        Parámetros:
            Ninguno.
        Retorna:
            bool: True si decide romper la pared, False si decide no hacerlo.
        """
        return random.choice([True, False])
    
    def decision_open_door(self):
        """
        Decide si el agente abrirá una puerta cerrada.
        En la clase base, retorna una decisión aleatoria.
        
        Parámetros:
            Ninguno.
        Retorna:
            bool: True si decide abrir la puerta, False en caso contrario.
        """
        return random.choice([True, False])

    def decision_reveal_poi(self):
        """
        Decide si el agente revelará un Punto de Interés (POI) en su posición.
        En la clase base, retorna una decisión aleatoria.
        
        Parámetros:
            Ninguno.
        Retorna:
            bool: True si decide revelar el POI, False en caso contrario.
        """
        return random.choice([True, False])

    def decision_rescue_victim(self):
        """
        Decide si el agente recogerá a una víctima descubierta.
        En la clase base, retorna una decisión aleatoria.
        
        Parámetros:
            Ninguno.
        Retorna:
            bool: True si decide rescatar (cargar) a la víctima, False en caso contrario.
        """
        return random.choice([True, False])


    # --- ACCIONES ---
    def get_valid_neighbors(self):
        """
        Obtiene las coordenadas de las celdas adyacentes (vecindad de Von Neumann) válidas dentro de la cuadrícula.
        
        Parámetros:
            Ninguno.
        Retorna:
            list: Lista de tuplas (x, y) con los vecinos.
        """
        return self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
    
    def _get_direction_index(self, cx, cy, tx, ty):
        """
        Calcula el índice numérico que representa la dirección cardinal del movimiento.
        0: Arriba, 1: Derecha, 2: Abajo, 3: Izquierda.
        
        Parámetros:
            cx (int): X actual.
            cy (int): Y actual.
            tx (int): X objetivo.
            ty (int): Y objetivo.
        Retorna:
            int: Índice de dirección (0-3) o -1 si no es adyacente ortogonalmente.
        """
        if ty > cy: return 0 
        elif tx > cx: return 1 
        elif ty < cy: return 2 
        elif tx < cx: return 3 
        return -1
    
    def is_outside_building(self, pos):
        """
        Verifica si una posición dada corresponde a los bordes exteriores del mapa (zona segura).
        
        Parámetros:
            pos (tuple): Coordenadas (x, y) a verificar.
        Retorna:
            bool: True si está en el borde, False si está dentro del edificio.
        """
        x, y = pos
        return (x == 0 or x == self.grid.width - 1 or 
                y == 0 or y == self.grid.height - 1)

    # --- ACCIONES ---
    def attempt_action(self, target_pos):
        """
        Intenta ejecutar una acción compleja hacia una posición objetivo. 
        Gestiona la interacción con paredes, puertas, fuego, humo y POIs, deduciendo los PA correspondientes.
        
        Parámetros:
            target_pos (tuple): Coordenadas (x, y) hacia donde se quiere interactuar o mover.
        Retorna:
            bool: True si se realizó alguna acción (movimiento o interacción), False si la acción fue bloqueada o cancelada.
        """
        curr_pos = self.pos
        cx, cy = curr_pos
        tx, ty = target_pos
        
        wall_dir = self._get_direction_index(cx, cy, tx, ty)

        # 1. OBSTÁCULOS: PAREDES
        if self.model.has_wall(cx, cy, wall_dir):
            if self.printable: print(f"   🧱 Agente {self.id}: Pared hacia {target_pos}.")
            
            if self.pa >= 2 and self.decision_chop_wall():
                if self.printable:
                    print(f"   🪓 Agente {self.id}: Rompiendo pared (-2 PA).")
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

        if not self.model.can_move(curr_pos, target_pos):
            if self.printable:
                print(f"   ❗ Agente {self.id}: Movimiento bloqueado hacia {target_pos} (pared/puerta cerrada).")
            return False

        if self.pa >= move_cost:
            if self.printable: print(f"   🦶 Agente {self.id}: Moviéndose a {target_pos} (Costo: {move_cost}).")
            self.model.grid.move_agent(self, target_pos)
            self.pa -= move_cost
            self.steps_taken += 1
            self.movement_count += 1
            
            # --- SALVAMIENTO ---
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
                    else:
                        if self.printable: print(f"   👻 Agente {self.id}: Falsa alarma.")
                        self.model.remove_poi(target_pos)
            
            return True
        
        return False
from Simulation.AgentBaseModel import AgentBaseModel
from Simulation.AuxFunctions import dijkstra_search

class AgentFireFighter(AgentBaseModel):
    def __init__(self, model, pa, id):
        super().__init__(model, pa, id)
        self.role = "Firefighter"

    def decision_choose_movement(self, possible_steps):
        """
        Sobrescribe la decisión de movimiento para usar Dijkstra hacia el fuego.
        """
        # 1. Identificar objetivos (Celdas con Fuego o Humo)
        fire_targets = []
        for x in range(self.model.grid.width):
            for y in range(self.model.grid.height):
                pos = (x, y)
                if self.model.get_cell_status(pos) in ['Fire', 'Smoke']:
                    fire_targets.append(pos)
        
        if not fire_targets:
            # Si no hay fuego, movimiento aleatorio o patrulla
            return super().decision_choose_movement(possible_steps)

        # 2. Usar Dijkstra para encontrar el siguiente paso hacia el fuego más cercano
        # avoid_fire=False porque su trabajo es ir hacia él
        next_step = dijkstra_search(self, fire_targets, avoid_fire=False)
        
        if next_step and next_step in possible_steps:
            return next_step
        
        # Fallback si no hay ruta clara
        return super().decision_choose_movement(possible_steps)

    def decision_extinguish_fire(self):
        # Siempre quiere apagar fuego si se encuentra con él
        return True

    def decision_chop_wall(self):
        # Decide romper pared si Dijkstra determinó que era el camino más corto
        return True
        
    def decision_open_door(self):
        return True
    
    def decision_reveal_poi(self):
        return True
    
    def decision_rescue_victim(self):
        return False
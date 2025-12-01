from Simulation.AgentBaseModel import AgentBaseModel
from Simulation.AuxFunctions import dijkstra_search

class AgenteRescuer(AgentBaseModel):
    def __init__(self, model, pa, id):
        super().__init__(model, pa, id)
        self.role = "Rescue"

    def decision_choose_movement(self, possible_steps):
        targets = []
        
        # ESTRATEGIA:
        # Si lleva víctima -> Ir a las salidas (Bordes del mapa o Ambulancia)
        # Si NO lleva víctima -> Ir a los POI (Puntos de interés)
        
        if self.carrying_victim:
            # --- MODIFICACIÓN: OBJETIVO ESQUINAS ---
            w, h = self.model.grid.width, self.model.grid.height
            # Definir las 4 esquinas como objetivos de salida
            targets = [
                (0, 0),         # Esquina inferior izquierda
                (0, h-1),       # Esquina superior izquierda
                (w-1, 0),       # Esquina inferior derecha
                (w-1, h-1)      # Esquina superior derecha
            ]
        else:
            # Buscar POIs
            targets = [poi_pos for poi_pos in self.model.pois]

        if not targets:
            return super().decision_choose_movement(possible_steps)

        # Usar Dijkstra evitando fuego (avoid_fire=True)
        # Esto hará que prefiera dar la vuelta a cruzar una habitación en llamas,
        # a menos que sea el único camino.
        next_step = dijkstra_search(self, targets, avoid_fire=True)

        if next_step and next_step in possible_steps:
            return next_step
            
        return super().decision_choose_movement(possible_steps)

    def decision_rescue_victim(self):
        return True

    def decision_reveal_poi(self):
        return True
        
    def decision_extinguish_fire(self):
        # Solo apaga si Dijkstra le dijo que pasara por ahí (es decir, está bloqueando su ruta óptima)
        return True
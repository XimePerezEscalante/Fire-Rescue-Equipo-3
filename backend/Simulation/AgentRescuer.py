from Simulation.AgentBaseModel import AgentBaseModel
from Simulation.AuxFunctions import dijkstra_search

class AgenteRescuer(AgentBaseModel):
    def __init__(self, model, pa, id, printable=False):
        """
        Constructor del Agente Rescatista. Hereda de AgentBaseModel y configura su rol y capacidad de ahorro de PA.
        
        Parámetros:
            model (Model): Referencia al modelo.
            pa (int): Puntos de acción.
            id (int): Identificador.
            printable (bool): Bandera de depuración.
        Retorna:
            None
        """
        super().__init__(model, pa, id, printable=printable)
        self.role = "Rescue"
        self.max_pa_savings = 2

    def decision_choose_movement(self, possible_steps):
        """
        Determina el movimiento del rescatista. Si carga una víctima, busca la salida; si no, busca POIs.
        Implementa el algoritmo de Dijkstra para trazar la ruta hacia el objetivo más cercano (POI o Salida), evitando casillas con fuego.
        
        Parámetros:
            possible_steps (list): Lista de movimientos válidos.
        Retorna:
            tuple: La coordenada (x, y) del siguiente paso óptimo.
        """
        targets = []
        if self.carrying_victim:
            if hasattr(self.model, 'entryPoints'):
                for ep in self.model.entryPoints:
                    targets.append((ep[1], ep[0]))
        else:
            targets = [(p[1], p[0]) for p in self.model.pois]
        if not targets:
            return super().decision_choose_movement(possible_steps)
        cx, cy = self.pos
        targets.sort(key=lambda t: abs(t[0] - cx) + abs(t[1] - cy))
        closest_targets = targets[:3]
        next_step = dijkstra_search(self, closest_targets, avoid_fire=True)
        if next_step and next_step in possible_steps:
            return next_step
        return super().decision_choose_movement(possible_steps)
    
    def decision_rescue_victim(self):
        """
        Sobrescribe la decisión base. El rescatista siempre recoge a las víctimas encontradas.
        
        Parámetros:
            Ninguno.
        Retorna:
            bool: Siempre True.
        """
        return True

    def decision_reveal_poi(self):
        """
        Sobrescribe la decisión base. El rescatista siempre revela los POIs.
        
        Parámetros:
            Ninguno.
        Retorna:
            bool: Siempre True.
        """
        return True
        
    def decision_extinguish_fire(self):
        """
        Sobrescribe la decisión base. El rescatista intenta apagar fuego si se interpone en su camino.
        
        Parámetros:
            Ninguno.
        Retorna:
            bool: Siempre True.
        """
        return True
    
    def decision_open_door(self):
        """
        Sobrescribe la decisión base. El rescatista siempre abre puertas.
        
        Parámetros:
            Ninguno.
        Retorna:
            bool: Siempre True.
        """
        return True
    
    def decision_chop_wall(self):
        """
        Sobrescribe la decisión base. El rescatista rompe paredes si es necesario para el rescate.
        
        Parámetros:
            Ninguno.
        Retorna:
            bool: Siempre True.
        """
        return True
    
    def decision_complete_extinguish(self):
        """
        Sobrescribe la decisión base. El rescatista solo extingue completamente el fuego si tiene suficientes PA de sobra (>= 3), priorizando el movimiento.
        
        Parámetros:
            Ninguno.
        Retorna:
            bool: True si tiene PA >= 3, False en caso contrario.
        """
        return self.pa >= 3
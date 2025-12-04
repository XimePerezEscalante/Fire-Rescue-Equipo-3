from Simulation.AgentBaseModel import AgentBaseModel
from Simulation.AuxFunctions import dijkstra_search

class AgentFireFighter(AgentBaseModel):
    def __init__(self, model, pa, id, printable=False):
        """
        Constructor del Agente "Bombero". Hereda de AgentBaseModel y establece su rol específico.
        
        Parámetros:
            model (Model): Referencia al modelo.
            pa (int): Puntos de acción por turno.
            id (int): Identificador.
            printable (bool): Bandera de depuración.
        Retorna:
            None
        """
        super().__init__(model, pa, id, printable=printable)
        self.role = "Firefighter"

    def decision_choose_movement(self, possible_steps):
        """
        Determina el movimiento del bombero priorizando la ubicación de fuegos activos.
        Implementa el algoritmo de Dijkstra para encontrar la ruta más corta hacia el fuego más cercano. Si no hay fuego, se mueve aleatoriamente.
        
        Parámetros:
            possible_steps (list): Lista de movimientos válidos adyacentes.
        Retorna:
            tuple: La coordenada (x, y) del siguiente paso óptimo.
        """
        fire_targets = [(f[1], f[0]) for f in self.model.fires]
        
        if self.printable:
            print(f"🚒 Agente {self.id} (Bombero): Buscando fuego...")
            print(f"   🔥 Objetivos activos: {fire_targets}")
        
        if not fire_targets:
            if self.printable:
                print(f"   🤷‍♂️ No hay fuego en el mapa. Patrullando.")
            return super().decision_choose_movement(possible_steps)

        next_step = dijkstra_search(self, fire_targets, avoid_fire=False)
        
        if self.printable:
            print(f"   🗺️ Dijkstra sugiere ir a: {next_step}")

        if next_step and next_step in possible_steps:
            return next_step
        
        if self.printable:
            print(f"   ⚠️ No se encontró ruta directa o el paso no es válido. Movimiento aleatorio.")
        return super().decision_choose_movement(possible_steps)

    def decision_extinguish_fire(self):
        """
        Sobrescribe la decisión base. El bombero siempre decide extinguir el fuego si es posible.

        Parámetros:
            Ninguno.
        Retorna:
            bool: Siempre True.
        """
        return True

    def decision_chop_wall(self):
        """
        Sobrescribe la decisión base. El bombero siempre decide romper paredes si es necesario para llegar a su objetivo.
        
        Parámetros:
            Ninguno.
        Retorna:
            bool: Siempre True.
        """
        return True
        
    def decision_open_door(self):
        """
        Sobrescribe la decisión base. El bombero siempre abre puertas cerradas.
        
        Parámetros:
            Ninguno.
        Retorna:
            bool: Siempre True.
        """
        return True
    
    def decision_reveal_poi(self):
        """
        Sobrescribe la decisión base. El bombero siempre revela POIs si se encuentra sobre ellos.
        
        Parámetros:
            Ninguno.
        Retorna:
            bool: Siempre True.
        """
        return True
    
    def decision_rescue_victim(self):
        """
        Sobrescribe la decisión base. El bombero nunca carga víctimas (su prioridad es el fuego).
        
        Parámetros:
            Ninguno.
        Retorna:
            bool: Siempre False.
        """
        return False
    
    def decision_complete_extinguish(self):
        """
        Sobrescribe la decisión base. El bombero siempre intenta extinguir el fuego completamente en lugar de solo reducirlo.
        
        Parámetros:
            Ninguno.
        Retorna:
            bool: Siempre True.
        """
        return True
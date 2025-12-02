from Simulation.AgentBaseModel import AgentBaseModel
from Simulation.AuxFunctions import dijkstra_search

class AgentFireFighter(AgentBaseModel):
    def __init__(self, model, pa, id, printable=False):
        super().__init__(model, pa, id, printable=printable)
        self.role = "Firefighter"

    def decision_choose_movement(self, possible_steps):
        # 1. Identificar objetivos
        fire_targets = [(f[1], f[0]) for f in self.model.fires]
        
        if self.printable:
            print(f"🚒 Agente {self.id} (Bombero): Buscando fuego...")
            print(f"   🔥 Objetivos activos: {fire_targets}")
        
        if not fire_targets:
            if self.printable:
                print(f"   🤷‍♂️ No hay fuego en el mapa. Patrullando.")
            # Si no hay fuego, patrulla aleatoria
            return super().decision_choose_movement(possible_steps)

        # 2. Ir hacia el fuego
        next_step = dijkstra_search(self, fire_targets, avoid_fire=False)
        
        if self.printable:
            print(f"   🗺️ Dijkstra sugiere ir a: {next_step}")

        if next_step and next_step in possible_steps:
            return next_step
        
        # Fallback
        if self.printable:
            print(f"   ⚠️ No se encontró ruta directa o el paso no es válido. Movimiento aleatorio.")
        return super().decision_choose_movement(possible_steps)

    def decision_extinguish_fire(self):
        return True

    def decision_chop_wall(self):
        return True # El bombero SÍ rompe paredes si es necesario
        
    def decision_open_door(self):
        return True
    
    def decision_reveal_poi(self):
        return True
    
    def decision_rescue_victim(self):
        return False
    
    def decision_complete_extinguish(self):
        return True
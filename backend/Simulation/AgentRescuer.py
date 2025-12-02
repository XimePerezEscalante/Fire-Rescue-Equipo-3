from Simulation.AgentBaseModel import AgentBaseModel
from Simulation.AuxFunctions import dijkstra_search

class AgenteRescuer(AgentBaseModel):
    def __init__(self, model, pa, id, printable=False):
        super().__init__(model, pa, id, printable=printable)
        self.role = "Rescue"

    def decision_choose_movement(self, possible_steps):
        targets = []
        
        # 1. Si lleva víctima -> Ir a ENTRY POINTS (Ambulancia)
        if self.carrying_victim:
            if self.printable:
                print(f"🚑 Agente {self.id} (Rescate): 🆘 Llevando víctima. Buscando salida...")
            
            if hasattr(self.model, 'entryPoints'):
                for ep in self.model.entryPoints:
                    targets.append((ep[1], ep[0]))
            
            # Fallback
            if not targets:
                targets = [(0,0), (0, self.model.grid.height-1)]

        # 2. Si NO lleva víctima -> Ir a POIs
        else:
            if self.printable:
                print(f"🚑 Agente {self.id} (Rescate): 🔎 Buscando víctimas (POIs)...")
            
            targets = [(p[1], p[0]) for p in self.model.pois]

        if self.printable:
            print(f"   📍 Objetivos actuales: {targets}")

        # Si no hay objetivos, movimiento aleatorio
        if not targets:
            if self.printable:
                print(f"   🤷‍♂️ No hay objetivos visibles. Patrullando.")
            return super().decision_choose_movement(possible_steps)

        # Usar Dijkstra (avoid_fire=True)
        next_step = dijkstra_search(self, targets, avoid_fire=True)

        if self.printable:
            print(f"   🗺️ Dijkstra sugiere ir a: {next_step}")

        if next_step and next_step in possible_steps:
            return next_step
            
        if self.printable:
            print(f"   ⚠️ Ruta bloqueada o no encontrada. Movimiento aleatorio.")
        return super().decision_choose_movement(possible_steps)

    def decision_rescue_victim(self):
        return True

    def decision_reveal_poi(self):
        return True
        
    def decision_extinguish_fire(self):
        return True
    
    def decision_open_door(self):
        return True
    
    def decision_chop_wall(self):
        return False
    
    def decision_complete_extinguish(self):
        return self.pa >= 3
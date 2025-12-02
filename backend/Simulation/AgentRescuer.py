from Simulation.AgentBaseModel import AgentBaseModel
from Simulation.AuxFunctions import dijkstra_search

class AgenteRescuer(AgentBaseModel):
    def __init__(self, model, pa, id, printable=False):
        super().__init__(model, pa, id, printable=printable)
        self.role = "Rescue"
        self.max_pa_savings = 2

    def decision_choose_movement(self, possible_steps):
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
        return True

    def decision_reveal_poi(self):
        return True
        
    def decision_extinguish_fire(self):
        return True
    
    def decision_open_door(self):
        return True
    
    def decision_chop_wall(self):
        return True
    
    def decision_complete_extinguish(self):
        return self.pa >= 3
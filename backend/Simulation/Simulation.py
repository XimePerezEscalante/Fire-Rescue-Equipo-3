# Simulation/Simulation.py
import random
import json
from Simulation.ExplorerModel import ExplorerModel

class Simulation:
    def __init__(self, width, height, agents, pa, seed=None, strategy="random"):
        self.seed = seed if seed is not None else random.randint(0, 100000)
        random.seed(self.seed)
        
        self.model = ExplorerModel(width, height, agents, pa, strategy=strategy, on_step_callback=self.record_frame, printable=False)
        self.simulation_data = {
            "metadata": {
                "width": width, "height": height, "agents": agents, "seed": self.seed
            },
            "frames": []
        }
        # Variable para saber por qué terminó
        self.end_reason = "NOT_FINISHED" 

    def run(self):
        while self.model.running:
            self.record_frame()
            self.model.step()
            self.check_game_status()
        
        self.record_frame()

    def check_game_status(self):
        """ Revisa el estado del modelo para actualizar end_reason """
        if not self.model.running:
            if self.model.victims_saved >= 7:
                self.end_reason = "WIN"
            elif self.model.victims_lost >= 4:
                self.end_reason = "LOSS_VICTIMS"
            elif self.model.damage_taken >= 24:
                self.end_reason = "LOSS_COLLAPSE"

    def record_frame(self):
        frame = {
            "step": self.model.steps,
            "agents": [{"id": a.id, "x": a.pos[0], "y": a.pos[1], "carrying": a.carrying_victim, "role": getattr(a, "role", "Base")} for a in self.model.agents_list],
            "fires": [{"y": f[0], "x": f[1], "state": f[2]} for f in self.model.fires],
            "pois": [{"y": p[0], "x": p[1], "type": p[2], "revealed": (p[3] if len(p)>3 else False)} for p in self.model.pois],
            "walls": [row[:] for row in self.model.walls],
            "doors": [{"p1": d[0], "p2": d[1], "status": d[2]} for d in self.model.doors],
            "stats": {"saved": self.model.victims_saved, "lost": self.model.victims_lost, "damage": self.model.damage_taken}
        }
        self.simulation_data["frames"].append(frame)

    def evaluate(self):
        """ Puntaje para rankear la simulación """
        # Sistema de puntaje para diferenciar claramente el éxito del fracaso
        score = 0
        
        # Base fuerte según resultado
        if self.end_reason == "WIN": score += 10000
        elif self.end_reason == "LOSS_VICTIMS": score -= 5000
        elif self.end_reason == "LOSS_COLLAPSE": score -= 5000
        elif self.end_reason == "TIMEOUT": score -= 1000

        # Ajustes finos
        score += (self.model.victims_saved * 500)  # Salvar es bueno
        score -= (self.model.victims_lost * 500)   # Perder víctimas es muy malo
        score -= (self.model.damage_taken * 10)    # El daño baja puntos
        score -= (self.model.steps * 5)            # Mientras más rápido, mejor

        return score
    
    # Dentro de tu clase Simulation o Model
    def calculate_final_score(self):
        """
        Calcula un puntaje numérico para determinar la calidad de la partida.
        Fórmula: (Salvados * 100) - (Muertos * 50) - (Daño * 10) - (Pasos * 0.5)
        """
        # Pesos (puedes ajustarlos según prefieras)
        W_SAVED = 100      # Premio por salvar
        W_LOST = -50       # Castigo por perder vidas
        W_DAMAGE = -10     # Castigo moderado por destruir el edificio
        W_STEPS = -0.5     # Pequeño castigo por tardar mucho (eficiencia)

        score = (self.model.victims_saved * W_SAVED) + \
                (self.model.victims_lost * W_LOST) + \
                (self.model.damage_taken * W_DAMAGE) + \
                (self.model.steps * W_STEPS)
                
        # Bonificación extra si se ganó la partida para separarlo de derrotas "honrosas"
        if self.end_reason == "WIN":
            score += 200
            
        return score

    def get_results_json(self):
        return {
            "score": self.evaluate(),
            "end_reason": self.end_reason,
            "steps_total": self.model.steps,
            "data": self.simulation_data
        }
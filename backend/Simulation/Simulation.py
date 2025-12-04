import random
import json
from Simulation.ExplorerModel import ExplorerModel

class Simulation:
    """
    Controlador de simulación que ejecuta y registra una partida completa del juego de rescate.
    Gestiona la ejecución del modelo, el registro de frames y el cálculo de puntajes.
    """
    
    def __init__(self, width, height, agents, pa, seed=None, strategy="random"):
        """
        Inicializa una nueva simulación con los parámetros especificados.
        
        Parámetros:
            width (int): Ancho del grid de simulación
            height (int): Alto del grid de simulación
            agents (int): Número de agentes a desplegar
            pa (int): Puntos de acción (energía máxima) de cada agente
            seed (int): Semilla para reproducibilidad (si es None, se genera aleatoria)
            strategy (str): Estrategia de despliegue de agentes ('random' o 'intelligent')
        """
        # Establece semilla para reproducibilidad de la simulación
        self.seed = seed if seed is not None else random.randint(0, 100000)
        random.seed(self.seed)
        
        # Crea el modelo con callback para registrar cada cambio de estado
        self.model = ExplorerModel(width, height, agents, pa, strategy=strategy, 
                                   on_step_callback=self.record_frame, printable=False)
        
        # Estructura para almacenar todos los frames de la simulación
        self.simulation_data = {
            "metadata": {
                "width": width, 
                "height": height, 
                "agents": agents, 
                "seed": self.seed
            },
            "frames": []
        }
        
        # Estado final de la simulación (WIN, LOSS_VICTIMS, LOSS_COLLAPSE, TIMEOUT)
        self.end_reason = "NOT_FINISHED" 

    def run(self):
        """
        Ejecuta la simulación completa hasta que termine por victoria, derrota o timeout.
        Registra un frame después de cada paso del modelo.
        """
        while self.model.running:
            self.record_frame()
            self.model.step()
            self.check_game_status()
        
        # Registra el frame final después de que termine la simulación
        self.record_frame()

    def check_game_status(self):
        """
        Actualiza la razón de finalización según el estado actual del modelo.
        Se ejecuta después de cada paso para determinar cómo terminó la partida.
        """
        if not self.model.running:
            if self.model.victims_saved >= 7:
                self.end_reason = "WIN"
            elif self.model.victims_lost >= 4:
                self.end_reason = "LOSS_VICTIMS"
            elif self.model.damage_taken >= 24:
                self.end_reason = "LOSS_COLLAPSE"

    def record_frame(self):
        """
        Captura el estado completo del modelo en el paso actual.
        Registra posiciones de agentes, fuegos, POIs, paredes, puertas y estadísticas.
        Cada frame permite reconstruir visualmente el estado de la simulación.
        """
        frame = {
            "step": self.model.steps,
            "agents": [
                {
                    "id": a.id, 
                    "x": a.pos[0], 
                    "y": a.pos[1], 
                    "carrying": a.carrying_victim, 
                    "role": getattr(a, "role", "Base")
                } 
                for a in self.model.agents_list
            ],
            "fires": [
                {
                    "y": f[0], 
                    "x": f[1], 
                    "state": f[2]  # 1=humo, 2=fuego
                } 
                for f in self.model.fires
            ],
            "pois": [
                {
                    "y": p[0], 
                    "x": p[1], 
                    "type": p[2], 
                    "revealed": (p[3] if len(p) > 3 else False)
                } 
                for p in self.model.pois
            ],
            "walls": [row[:] for row in self.model.walls],
            "doors": [
                {
                    "p1": d[0], 
                    "p2": d[1], 
                    "status": d[2]
                } 
                for d in self.model.doors
            ],
            "stats": {
                "saved": self.model.victims_saved, 
                "lost": self.model.victims_lost, 
                "damage": self.model.damage_taken
            }
        }
        self.simulation_data["frames"].append(frame)

    def evaluate(self):
        """
        Calcula un puntaje para rankear la calidad de la simulación.
        Considera el resultado final, víctimas salvadas/perdidas, daño estructural y eficiencia.
        
        Retorna:
            int: Puntaje total de la simulación (valores más altos indican mejor desempeño)
        """
        score = 0
        
        # Bonificación/penalización base según resultado final
        if self.end_reason == "WIN": 
            score += 10000
        elif self.end_reason == "LOSS_VICTIMS": 
            score -= 5000
        elif self.end_reason == "LOSS_COLLAPSE": 
            score -= 5000
        elif self.end_reason == "TIMEOUT": 
            score -= 1000
        
        # Factores de desempeño durante la partida
        score += (self.model.victims_saved * 500)   # Recompensa por salvar víctimas
        score -= (self.model.victims_lost * 500)    # Penalización fuerte por perder víctimas
        score -= (self.model.damage_taken * 10)     # Penalización por daño estructural
        score -= (self.model.steps * 5)             # Penalización leve por ineficiencia temporal

        return score
    
    def calculate_final_score(self):
        """
        Calcula un puntaje alternativo con pesos diferentes para evaluar calidad de la partida.
        Enfocado en minimizar pérdidas y maximizar eficiencia.
        
        Retorna:
            float: Puntaje final considerando víctimas, daño y pasos ejecutados
        """
        # Definición de pesos para cada métrica
        W_SAVED = 100       # Premio alto por cada víctima salvada
        W_LOST = -50        # Castigo por cada víctima perdida
        W_DAMAGE = -10      # Castigo moderado por cada punto de daño estructural
        W_STEPS = -0.5      # Castigo pequeño por cada paso (incentiva eficiencia)

        score = (self.model.victims_saved * W_SAVED) + \
                (self.model.victims_lost * W_LOST) + \
                (self.model.damage_taken * W_DAMAGE) + \
                (self.model.steps * W_STEPS)
        
        # Bonificación adicional por victoria
        if self.end_reason == "WIN":
            score += 200
            
        return score

    def get_results_json(self):
        """
        Genera un diccionario con todos los resultados de la simulación para serialización.
        Incluye puntaje, razón de finalización, pasos totales y datos completos de frames.
        
        Retorna:
            dict: Diccionario con estructura completa de resultados en formato JSON-compatible
        """
        return {
            "score": self.evaluate(),
            "end_reason": self.end_reason,
            "steps_total": self.model.steps,
            "data": self.simulation_data
        }
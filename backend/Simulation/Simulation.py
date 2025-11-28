from Simulation.ExplorerModel import ExplorerModel
import random
import numpy as np
import pandas as pd

class Simulation:
    def __init__(self, width, height, agents, maxEnergy, seed=None, random_fires=None, random_pois=None):
        self.width = width
        self.height = height
        self.agents = agents
        self.maxEnergy = maxEnergy
        
        # Configuración de Semilla (Crucial para reproducibilidad)
        self.seed = seed if seed is not None else random.randint(0, 10000)
        random.seed(self.seed)
        np.random.seed(self.seed)
        self.random_fires = random_fires
        self.random_pois = random_pois
        self.model = None

    def runSimulation(self):
        self.model = ExplorerModel(
            self.width, self.height, self.agents, self.maxEnergy,
            random_fires=self.random_fires,
            random_pois=self.random_pois
        )

        while not self.model.is_all_clean():
            self.model.step()

        df_positions = pd.DataFrame(self.model.agents_positions)
        df_positions.index.name = 'Step'
        self.model.agents_positions = df_positions

    def get_score(self):
        #TODO: El siguiente código lo ha propuesto gemini
        #TODO: pero realmente tenemos que revisar cómo vamos a
        #TODO: medir el fuego a extinguir
        # # Lógica de puntaje. Ejemplo: (Fuegos apagados * 10) - (Pasos totales)
        # # Ajusta esto a tus métricas reales del ExplorerModel
        # extinguished = sum([a.fireExtinguish for a in self.model.agents])
        # return extinguished
        pass

    def get_results_json(self):
        # Genera el JSON compatible con Unity
        results = []
        if hasattr(self.model.agents_positions, 'columns'):
            for agent_id in self.model.agents_positions.columns:
                path_list = []
                for step_pos in self.model.agents_positions[agent_id]:
                    # Unity: X=x, Y=0.5, Z=y
                    pos_obj = {"x": float(step_pos[0]), "y": 0.5, "z": float(step_pos[1])}
                    path_list.append(pos_obj)
                results.append({"id": int(agent_id), "path": path_list})
        return {"results": results}
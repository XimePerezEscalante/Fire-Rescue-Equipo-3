from multiprocessing import Pool, cpu_count
from Simulation.Simulation import Simulation
import numpy as np
import time

# Función worker (debe estar fuera de la clase para multiprocessing)
def worker_simulation(args):
    width, height, agents, energy, strategy, seed, r_fires, r_pois = args
    
    # Instanciar modelo con semilla fija
    sim = Simulation(width, height, agents, energy, seed=seed, random_fires=r_fires, random_pois=r_pois)
    sim.runSimulation()
    
    score = sim.get_score()
    return (score, seed)

class SimulationManager:
    def run_parallel_experiment(self, width, height, agents, energy, 
                                iterations=100, strategy="random",
                                random_fires=None, random_pois=None):
        
        start_time = time.time()
        print(f"⚡ Corriendo {iterations} simulaciones en paralelo...")

        # 1. Generar semillas únicas
        seeds = np.random.randint(0, 1000000, size=iterations)

        # 2. Preparar argumentos (tuplas)
        tasks = [
            (width, height, agents, energy, strategy, int(s), random_fires, random_pois)
            for s in seeds
        ]

        # 3. Ejecutar en paralelo
        with Pool(processes=cpu_count()) as pool:
            results = pool.map(worker_simulation, tasks)

        # 4. Procesar estadísticas
        scores = [r[0] for r in results]
        best_result = max(results, key=lambda x: x[0]) # Asumimos que Mayor score es mejor
        best_score = best_result[0]
        best_seed = best_result[1]
        
        elapsed = time.time() - start_time
        print(f"✅ Terminado en {elapsed:.2f}s. Mejor Score: {best_score}")

        # 5. Re-ejecutar la ganadora para obtener el JSON visual
        print("🎥 Generando replay de la mejor simulación...")
        winner_sim = Simulation(width, height, agents, energy, 
                                seed=best_seed, random_fires=random_fires, random_pois=random_pois)
        winner_sim.runSimulation()
        
        return {
            "meta": {
                "total_time": elapsed,
                "iterations": iterations,
                "best_seed": best_seed
            },
            "stats": {
                "max_score": best_score,
                "avg_score": sum(scores) / len(scores),
                "min_score": min(scores)
            },
            "best_run_data": winner_sim.get_results_json()
        }
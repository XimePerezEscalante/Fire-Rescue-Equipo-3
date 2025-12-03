import multiprocessing
import random
from Simulation.Simulation import Simulation

def _worker_simulation(args):
    """
    Función que ejecuta un núcleo de CPU.
    """
    width, height, agents, pa, seed, strategy = args
    
    # Ejecutar la simulación
    sim = Simulation(width, height, agents, pa, seed=seed, strategy=strategy)
    sim.run()
    
    # Obtener los datos para el GIF
    full_replay_data = sim.get_results_json()
    
    # Calcular Scores
    final_score = sim.calculate_final_score()

    # Calcular la suma de pasos individuales de todos los agentes
    total_movements = sum(agent.movement_count for agent in sim.model.agents_list)

    return {
        "seed": seed,
        "score": final_score,
        "end_reason": sim.end_reason,
        "steps": sim.model.steps,
        "damage": sim.model.damage_taken,
        "saved": sim.model.victims_saved,
        "replay_data": full_replay_data,
        "total_distance": total_movements,
    }


class SimulationManager:
    def run_batch_experiment(self, width, height, agents, pa, iterations, strategy_name):
        
        print(f"🔄 Preparando {iterations} simulaciones en paralelo para: {strategy_name}...")

        # Preparar argumentos
        tasks_args = []
        for i in range(iterations):
            seed = random.randint(0, 1000000)
            tasks_args.append((width, height, agents, pa, seed, strategy_name))

        # Ejecucion paralela
        num_cores = multiprocessing.cpu_count()
        results = []
        if iterations > 0:
            with multiprocessing.Pool(processes=num_cores) as pool:
                raw_results = pool.map(_worker_simulation, tasks_args)
                # Asignamos IDs y guardamos
                for i, res in enumerate(raw_results):
                    res["id"] = i
                    results.append(res)

        # 3. Calcular Estadísticas Globales
        stats = {
            "wins": 0,
            "loss_victims": 0,
            "loss_collapse": 0
        }

        for res in results:
            if res["end_reason"] == "WIN":
                stats["wins"] += 1
            elif res["end_reason"] == "LOSS_VICTIMS":
                stats["loss_victims"] += 1
            elif res["end_reason"] == "LOSS_COLLAPSE":
                stats["loss_collapse"] += 1

        # Ordenar por puntaje (Mejor primero)
        sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)

        return {
            "stats": stats,
            "sorted_runs": sorted_results
        }
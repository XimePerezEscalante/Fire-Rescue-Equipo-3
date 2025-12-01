# Simulation/SimulationManager.py
import multiprocessing
import random
from Simulation.Simulation import Simulation

def _worker_simulation(args):
    """
    Función que ejecuta un núcleo de CPU.
    """
    width, height, agents, pa, seed, strategy = args
    
    # 1. Ejecutar la simulación
    sim = Simulation(width, height, agents, pa, seed=seed, strategy=strategy)
    sim.run()
    
    # 2. Obtener los datos completos para el GIF
    # (Asumiendo que sim.get_results_json() devuelve {'data': {...}, ...})
    full_replay_data = sim.get_results_json()
    
    # 3. Calcular Score (Asegúrate que Simulation.py tenga este método, si no, usa la fórmula aquí)
    if hasattr(sim, 'calculate_final_score'):
        final_score = sim.calculate_final_score()
    else:
        # Fallback por si acaso
        final_score = (sim.model.victims_saved * 100) - (sim.model.victims_lost * 50)

    # 4. RETORNAR DICCIONARIO PLANO (Aquí estaba el error antes)
    # VisualSimulation espera encontrar 'saved', 'damage', 'steps' directamente aquí.
    return {
        "seed": seed,
        "score": final_score,
        "end_reason": sim.end_reason,
        
        # --- LLAVES CRÍTICAS ---
        "steps": sim.model.steps,
        "damage": sim.model.damage_taken,
        "saved": sim.model.victims_saved,
        # -----------------------
        
        "replay_data": full_replay_data
    }


class SimulationManager:
    def run_batch_experiment(self, width, height, agents, pa, iterations, strategy_name):
        
        print(f"🔄 Preparando {iterations} simulaciones en paralelo para: {strategy_name}...")

        # 1. Preparar argumentos
        tasks_args = []
        for i in range(iterations):
            seed = random.randint(0, 1000000)
            tasks_args.append((width, height, agents, pa, seed, strategy_name))

        # 2. EJECUCIÓN PARALELA
        num_cores = multiprocessing.cpu_count()
        results = []
        
        # Usamos 'with' para gestionar correctamente el Pool
        if iterations > 0:
            with multiprocessing.Pool(processes=num_cores) as pool:
                # Mapeamos la función worker a los argumentos
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

        # 4. Ordenar por puntaje (Mejor primero)
        sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)

        return {
            "stats": stats,
            "sorted_runs": sorted_results
        }
import random
import multiprocessing
from tqdm import tqdm
from Simulation.Simulation import Simulation

def _worker_simulation(args):
    """
    Función ejecutada por cada proceso worker para realizar una simulación independiente.
    Se ejecuta en paralelo en diferentes núcleos de CPU para optimizar el rendimiento.
    
    Parámetros:
        args (tuple): Tupla con (width, height, agents, pa, )
    
    Retorna:
        dict: Diccionario con métricas de la simulación y datos completos de reproducción
    """
    width, height, agents, pa, strategy = args
    
    # Ejecuta la simulación completa con los parámetros especificados
    sim = Simulation(width, height, agents, pa, strategy=strategy)
    sim.run()
    
    # Obtiene los datos completos de reproducción (todos los frames)
    full_replay_data = sim.get_results_json()
    
    # Calcula el puntaje final considerando víctimas, daño y eficiencia
    final_score = sim.calculate_final_score()

    # Calcula la distancia total recorrida por todos los agentes (suma de movimientos individuales)
    total_movements = sum(agent.movement_count for agent in sim.model.agents_list)

    return {
        "score": final_score,
        "end_reason": sim.end_reason,
        "steps": sim.model.steps,
        "damage": sim.model.damage_taken,
        "saved": sim.model.victims_saved,
        "replay_data": full_replay_data,
        "total_distance": total_movements,
    }


class SimulationManager:
    """
    Gestor de simulaciones que coordina la ejecución paralela de múltiples partidas.
    Utiliza multiprocessing para ejecutar simulaciones simultáneas en todos los núcleos disponibles.
    """

    def run_batch_experiment(self, width, height, agents, pa, iterations, strategy_name):
        """
        Ejecuta un lote de simulaciones en paralelo y recopila estadísticas agregadas.
        Utiliza todos los núcleos de CPU disponibles para maximizar el rendimiento.
        
        Parámetros:
            width (int): Ancho del grid de simulación
            height (int): Alto del grid de simulación
            agents (int): Número de agentes por simulación
            pa (int): Puntos de acción de cada agente
            iterations (int): Cantidad de simulaciones a ejecutar
            strategy_name (str): Nombre de la estrategia ('random' o 'intelligent')
        
        Retorna:
            dict: Diccionario con estadísticas globales y lista de simulaciones ordenadas por puntaje
        """
        print(f"Preparando {iterations} simulaciones en paralelo para: {strategy_name}...")
        
        # Prepara los argumentos para cada simulación con semillas únicas
        tasks_args = []
        for i in range(iterations):
            tasks_args.append((width, height, agents, pa, strategy_name))
        
        # Ejecuta simulaciones en paralelo usando todos los núcleos disponibles
        num_cores = multiprocessing.cpu_count()
        results = []
        
        if iterations > 0:
            # Enviamos tareas en grupos para reducir overhead de llamadas
            chunk_size = max(1, iterations // (num_cores * 4))

            with multiprocessing.Pool(processes=num_cores) as pool:
                # Usamos chunksize para mejorar el paso de tareas
                iterator = pool.imap_unordered(_worker_simulation, tasks_args, chunksize=chunk_size)
                for res in tqdm(iterator, total=iterations, desc=f"🚀 Ejecutando ({strategy_name})", unit="sim"):
                    results.append(res)
                
                # Asignar IDs post-procesamiento
                for i, res in enumerate(results):
                    res["id"] = i
        
        # Calcula estadísticas agregadas de todos los resultados
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
        
        # Ordena resultados por puntaje descendente (mejores primero)
        sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
        
        return {
            "stats": stats,
            "sorted_runs": sorted_results
        }
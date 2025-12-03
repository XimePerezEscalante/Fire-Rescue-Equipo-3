import numpy as np

def calculate_summary_stats(strategy_name, all_runs):
    """
    Calcula un diccionario de métricas agregadas a partir de los resultados de un lote.
    
    Args:
        strategy_name (str): Nombre de la estrategia ('random' o 'intelligent').
        all_runs (list): Lista de diccionarios con los resultados de cada simulación.
        
    Returns:
        dict: Diccionario con estadísticas resumidas.
    """
    total_runs = len(all_runs)
    if total_runs == 0:
        return {
            "strategy": strategy_name, "total_runs": 0, "win_rate": 0, "avg_score": 0,
            "avg_steps": 0, "avg_saved": 0, "avg_damage": 0, "best_score": 0, "fastest_win_steps": -1
        }

    scores = [run["score"] for run in all_runs]
    steps = [run["steps"] for run in all_runs]
    saved = [run["saved"] for run in all_runs]
    damage = [run["damage"] for run in all_runs]
    
    wins = sum(1 for run in all_runs if run["end_reason"] == "WIN")
    # Pérdidas específicas que mencionaste:
    losses_victims = sum(1 for run in all_runs if run["end_reason"] == "LOSS_VICTIMS")
    losses_collapse = sum(1 for run in all_runs if run["end_reason"] == "LOSS_COLLAPSE")
    
    # Identificar la mejor corrida (basada en el puntaje)
    best_run = max(all_runs, key=lambda x: x["score"])
    
    # Identificar la corrida con victoria más rápida (si existe)
    winning_runs = [run for run in all_runs if run["end_reason"] == "WIN"]
    fastest_win_steps = min([run["steps"] for run in winning_runs]) if winning_runs else -1

    return {
        "strategy": strategy_name,
        "total_runs": total_runs,
        "win_rate": (wins / total_runs) * 100,
        "loss_victims_rate": (losses_victims / total_runs) * 100,
        "loss_collapse_rate": (losses_collapse / total_runs) * 100,
        "avg_score": np.mean(scores),
        "avg_steps": np.mean(steps),
        "avg_saved": np.mean(saved),
        "avg_damage": np.mean(damage),
        "best_score": best_run["score"],
        "fastest_win_steps": fastest_win_steps,
        "best_run": best_run
    }

def print_comparison_table(stats_random, stats_intelligent):
    """
    Imprime la tabla comparativa de las dos estrategias en formato Markdown.
    
    Args:
        stats_random (dict): Estadísticas resumidas para la estrategia 'random'.
        stats_intelligent (dict): Estadísticas resumidas para la estrategia 'intelligent'.
    """
    print("\n\n" + "="*80)
    print("🏆 RESULTADOS COMPARATIVOS DEL EXPERIMENTO DE LOTE")
    print("="*80)
    
    print("| Métrica | Estrategia Random | Estrategia Intelligent |")
    print("| :--- | :---: | :---: |")
    print(f"| **Iteraciones Totales** | {stats_random['total_runs']} | {stats_intelligent['total_runs']} |")
    print(f"| **Tasa de Victoria (%)** | {stats_random['win_rate']:.2f} % | {stats_intelligent['win_rate']:.2f} % |")
    print(f"| Tasa de Derrota (Vict.) (%) | {stats_random['loss_victims_rate']:.2f} % | {stats_intelligent['loss_victims_rate']:.2f} % |")
    print(f"| Tasa de Derrota (Colap.) (%) | {stats_random['loss_collapse_rate']:.2f} % | {stats_intelligent['loss_collapse_rate']:.2f} % |")
    print(f"| **Puntaje Promedio** | {stats_random['avg_score']:.2f} | **{stats_intelligent['avg_score']:.2f}** |")
    print(f"| Promedio de Pasos | {stats_random['avg_steps']:.1f} | {stats_intelligent['avg_steps']:.1f} |")
    print(f"| Promedio Víctimas Salvadas | {stats_random['avg_saved']:.2f} | **{stats_intelligent['avg_saved']:.2f}** |")
    print(f"| Promedio Daño Estructural | {stats_random['avg_damage']:.2f} | {stats_intelligent['avg_damage']:.2f} |")
    print(f"| Mejor Puntaje Obtenido | {stats_random['best_score']:.2f} | **{stats_intelligent['best_score']:.2f}** |")
    
    fastest_random = f"{stats_random['fastest_win_steps']}" if stats_random['fastest_win_steps'] != -1 else "N/A"
    fastest_intelligent = f"{stats_intelligent['fastest_win_steps']}" if stats_intelligent['fastest_win_steps'] != -1 else "N/A"

    print(f"| Pasos Victoria más Rápida | {fastest_random} | {fastest_intelligent} |")
    
    print("\n" + "="*80)
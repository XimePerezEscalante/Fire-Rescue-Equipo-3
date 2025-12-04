import matplotlib.pyplot as plt
import numpy as np

def calculate_summary_stats(strategy_name, all_runs):
    """
    Calcula estadísticas agregadas a partir de los resultados de múltiples simulaciones.
    Procesa métricas de desempeño, victorias, derrotas y eficiencia operacional.
    
    Parámetros:
        strategy_name (str): Nombre de la estrategia analizada ('random' o 'intelligent')
        all_runs (list): Lista de diccionarios con resultados individuales de cada simulación
        
    Retorna:
        dict: Diccionario con estadísticas resumidas incluyendo promedios, tasas y mejores resultados
    """
    total_runs = len(all_runs)
    
    # Manejo de caso sin simulaciones ejecutadas
    if total_runs == 0:
        return {
            "strategy": strategy_name, "total_runs": 0, "win_rate": 0, "avg_score": 0,
            "avg_steps": 0, "avg_saved": 0, "avg_damage": 0, "best_score": 0, "fastest_win_steps": -1
        }

    # Extrae métricas individuales de todas las simulaciones
    scores = [run["score"] for run in all_runs]
    steps = [run["steps"] for run in all_runs]
    saved = [run["saved"] for run in all_runs]
    damage = [run["damage"] for run in all_runs]
    distances = [run.get("total_distance", 0) for run in all_runs]
    
    # Contabiliza resultados finales por tipo
    wins = sum(1 for run in all_runs if run["end_reason"] == "WIN")
    losses_victims = sum(1 for run in all_runs if run["end_reason"] == "LOSS_VICTIMS")
    losses_collapse = sum(1 for run in all_runs if run["end_reason"] == "LOSS_COLLAPSE")
    
    # Identifica la simulación con mejor puntaje global
    best_run = max(all_runs, key=lambda x: x["score"])
    
    # Identifica la victoria más eficiente en términos de pasos
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
        "avg_distance": np.mean(distances),
        "best_score": best_run["score"],
        "fastest_win_steps": fastest_win_steps,
        "best_run": best_run
    }

def print_comparison_table(stats_random, stats_intelligent):
    """
    Imprime una tabla comparativa detallada entre dos estrategias en formato Markdown.
    Facilita la visualización rápida de diferencias de desempeño.
    
    Parámetros:
        stats_random (dict): Estadísticas resumidas de la estrategia aleatoria
        stats_intelligent (dict): Estadísticas resumidas de la estrategia inteligente
    """
    print("\n\n" + "="*80)
    print("RESULTADOS COMPARATIVOS DEL EXPERIMENTO")
    print("="*80)
    
    # Encabezado de tabla Markdown
    print("| Métrica | Estrategia Random | Estrategia Intelligent |")
    print("| :--- | :---: | :---: |")
    
    # Filas de métricas principales
    print(f"| **Iteraciones Totales** | {stats_random['total_runs']} | {stats_intelligent['total_runs']} |")
    print(f"| **Tasa de Victoria (%)** | {stats_random['win_rate']:.2f} % | {stats_intelligent['win_rate']:.2f} % |")
    print(f"| Tasa de Derrota (Vict.) (%) | {stats_random['loss_victims_rate']:.2f} % | {stats_intelligent['loss_victims_rate']:.2f} % |")
    print(f"| Tasa de Derrota (Colap.) (%) | {stats_random['loss_collapse_rate']:.2f} % | {stats_intelligent['loss_collapse_rate']:.2f} % |")
    print(f"| **Puntaje Promedio** | {stats_random['avg_score']:.2f} | **{stats_intelligent['avg_score']:.2f}** |")
    print(f"| Promedio de Pasos | {stats_random['avg_steps']:.1f} | {stats_intelligent['avg_steps']:.1f} |")
    print(f"| Promedio Víctimas Salvadas | {stats_random['avg_saved']:.2f} | **{stats_intelligent['avg_saved']:.2f}** |")
    print(f"| Promedio Daño Estructural | {stats_random['avg_damage']:.2f} | {stats_intelligent['avg_damage']:.2f} |")
    print(f"| Mejor Puntaje Obtenido | {stats_random['best_score']:.2f} | **{stats_intelligent['best_score']:.2f}** |")
    
    # Manejo de victorias más rápidas (puede no existir si no hubo victorias)
    fastest_random = f"{stats_random['fastest_win_steps']}" if stats_random['fastest_win_steps'] != -1 else "N/A"
    fastest_intelligent = f"{stats_intelligent['fastest_win_steps']}" if stats_intelligent['fastest_win_steps'] != -1 else "N/A"

    print(f"| Pasos Victoria más Rápida | {fastest_random} | {fastest_intelligent} |")
    
    print("\n" + "="*80)

def save_single_plot(strategies, values, colors, title, ylabel, filename):
    """
    Función auxiliar para crear, guardar y cerrar una gráfica individual.

    Args:
        strategies (list of str): Lista con los nombres de las estrategias (eje X). Ej: ['Aleatoria', 'Inteligente'].
        values (list of float): Lista de valores numéricos correspondientes a cada estrategia.
        colors (list of str): Lista de códigos de color (hex o nombres) para las barras.
        title (str): Título principal que aparecerá arriba de la gráfica.
        ylabel (str): Etiqueta descriptiva para el eje Y (ej: 'Puntos', 'Pasos', 'Unidades').
        filename (str): Nombre del archivo (incluyendo extensión .png) donde se guardará la imagen.

    Returns:
        None: La función no retorna ningún valor. Su efecto es crear un archivo de imagen en el disco
              y liberar la memoria utilizada por la figura de matplotlib.
    """
    plt.figure(figsize=(6, 6))
    bars = plt.bar(strategies, values, color=colors, edgecolor='grey', width=0.6)
    
    plt.title(title, fontsize=12, fontweight='bold', pad=15)
    plt.ylabel(ylabel, fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Etiquetas sobre las barras
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + (height*0.01),
                 f'{height:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=11)

    plt.tight_layout()
    plt.savefig(filename, dpi=100)
    plt.close()
    print(f"   -> Guardado: {filename}")

def plot_simulation_results(stats_random, stats_intelligent):
    """
    Genera y guarda un conjunto de gráficas comparativas visuales entre las dos estrategias.
    Genera 1 imagen general de distribución de resultados y 6 imágenes individuales 
    para métricas específicas.

    Args:
        stats_random (dict): Diccionario que contiene las estadísticas resumidas (promedios, tasas, etc.)
                             calculadas para la estrategia 'Random'.
        stats_intelligent (dict): Diccionario que contiene las estadísticas resumidas calculadas 
                                  para la estrategia 'Intelligent'.

    Returns:
        None: La función no retorna datos. Genera múltiples archivos .png en el directorio de ejecución.
    """
    # Traducción de nombres de estrategias para el Eje X
    strategies = ['Aleatoria', 'Inteligente']
    colors = ['#FF9999', '#66B2FF'] 
    
    print("📊 Generando gráficas...")

    # --- Distribución de los resultados ---
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    
    # Traducción de métricas
    metrics = ['Tasa Victoria', 'Derrota (Víctimas)', 'Derrota (Colapso)']
    random_vals = [stats_random['win_rate'], stats_random['loss_victims_rate'], stats_random['loss_collapse_rate']]
    intelligent_vals = [stats_intelligent['win_rate'], stats_intelligent['loss_victims_rate'], stats_intelligent['loss_collapse_rate']]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    rects1 = ax1.bar(x - width/2, random_vals, width, label='Aleatoria', color=colors[0], edgecolor='grey')
    rects2 = ax1.bar(x + width/2, intelligent_vals, width, label='Inteligente', color=colors[1], edgecolor='grey')
    
    ax1.set_ylabel('Porcentaje (%)')
    ax1.set_title('Distribución de Resultados por Estrategia')
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics)
    ax1.legend()
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax1.annotate(f'{height:.1f}%', xy=(rect.get_x() + rect.get_width() / 2, height),
                         xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)

    autolabel(rects1)
    autolabel(rects2)
    plt.tight_layout()
    plt.savefig('comparison_outcomes.png')
    plt.close()
    print("   -> Guardado: comparison_outcomes.png")
    
    # --- Métricas de Desempeño (Individuales) ---
    
    # A. Score (Puntaje)
    save_single_plot(strategies, 
                     [stats_random['avg_score'], stats_intelligent['avg_score']], 
                     colors, 
                     'Puntaje Promedio (Mayor es mejor)', 
                     'Puntos', 
                     'metric_score.png')

    # B. Saved Victims (Víctimas Salvadas)
    save_single_plot(strategies, 
                     [stats_random['avg_saved'], stats_intelligent['avg_saved']], 
                     colors, 
                     'Promedio Víctimas Salvadas (Mayor es mejor)', 
                     'Cantidad', 
                     'metric_saved.png')

    # C. Steps (Duración/Pasos Globales)
    save_single_plot(strategies, 
                     [stats_random['avg_steps'], stats_intelligent['avg_steps']], 
                     colors, 
                     'Duración Promedio (Ticks Globales)', 
                     'Rondas', 
                     'metric_steps.png')

    # D. Damage (Daño)
    save_single_plot(strategies, 
                     [stats_random['avg_damage'], stats_intelligent['avg_damage']], 
                     colors, 
                     'Daño Estructural Promedio', 
                     'Unidades de Daño', 
                     'metric_damage.png')

    # E. Distance (Esfuerzo Total)
    save_single_plot(strategies, 
                     [stats_random['avg_distance'], stats_intelligent['avg_distance']], 
                     colors, 
                     'Movimiento Total Promedio (Esfuerzo)', 
                     'Pasos Totales', 
                     'metric_distance.png')

    # F. Efficiency (Eficiencia - Derivada)
    eff_random = stats_random['avg_distance'] / stats_random['avg_saved'] if stats_random['avg_saved'] > 0 else 0
    eff_intel = stats_intelligent['avg_distance'] / stats_intelligent['avg_saved'] if stats_intelligent['avg_saved'] > 0 else 0
    
    save_single_plot(strategies, 
                     [eff_random, eff_intel], 
                     colors, 
                     'Costo de Rescate (Movimiento por Víctima)', 
                     'Pasos / Víctima', 
                     'metric_efficiency.png')
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
    print("RESULTADOS COMPARATIVOS DEL EXPERIMENTO DE LOTE")
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

def plot_simulation_results(stats_random, stats_intelligent):
    """
    Genera gráficas comparativas visuales entre dos estrategias.
    Crea dos archivos PNG: uno con distribución de resultados y otro con métricas de desempeño.
    
    Parámetros:
        stats_random (dict): Estadísticas resumidas de la estrategia aleatoria
        stats_intelligent (dict): Estadísticas resumidas de la estrategia inteligente
    """
    strategies = ['Random', 'Intelligent']
    colors = ['#FF9999', '#66B2FF']  # Colores diferenciados para cada estrategia
    
    # --- Gráfica 1: Distribución de Resultados Finales ---
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    metrics = ['Win Rate', 'Loss (Victims)', 'Loss (Collapse)']
    random_vals = [stats_random['win_rate'], stats_random['loss_victims_rate'], stats_random['loss_collapse_rate']]
    intelligent_vals = [stats_intelligent['win_rate'], stats_intelligent['loss_victims_rate'], stats_intelligent['loss_collapse_rate']]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    # Barras comparativas para cada estrategia
    rects1 = ax1.bar(x - width/2, random_vals, width, label='Random', color=colors[0], edgecolor='grey')
    rects2 = ax1.bar(x + width/2, intelligent_vals, width, label='Intelligent', color=colors[1], edgecolor='grey')
    
    ax1.set_ylabel('Percentage (%)')
    ax1.set_title('Outcome Distribution by Strategy')
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics)
    ax1.legend()
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    
    def autolabel(rects):
        """
        Función auxiliar que agrega etiquetas de valor sobre cada barra.
        
        Parámetros:
            rects: Conjunto de rectángulos (barras) a etiquetar
        """
        for rect in rects:
            height = rect.get_height()
            ax1.annotate(f'{height:.1f}%', xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)

    autolabel(rects1)
    autolabel(rects2)
    plt.tight_layout()
    plt.savefig('comparison_outcomes.png')
    print("Graph saved: comparison_outcomes.png")
    
    # --- Gráfica 2: Métricas de Desempeño y Eficiencia (6 paneles) ---
    fig2, axs = plt.subplots(3, 2, figsize=(12, 14))
    fig2.suptitle('Performance Metrics & Efficiency', fontsize=16)
    
    def plot_metric(ax, key, title, ylabel, is_derived=False, derived_vals=None):
        """
        Función auxiliar para graficar una métrica individual en un panel.
        
        Parámetros:
            ax: Eje de matplotlib donde se dibujará
            key (str): Clave de la métrica en el diccionario de estadísticas
            title (str): Título del panel
            ylabel (str): Etiqueta del eje Y
            is_derived (bool): Si True, usa valores calculados en lugar de extraer del dict
            derived_vals (list): Lista con valores calculados para métricas derivadas
        """
        if is_derived:
            vals = derived_vals
        else:
            vals = [stats_random[key], stats_intelligent[key]]
            
        bars = ax.bar(strategies, vals, color=colors, edgecolor='grey', width=0.6)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=9)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        
        # Etiquetas de valor sobre cada barra
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + (height*0.01),
                    f'{height:.1f}', ha='center', va='bottom', fontweight='bold')

    # Fila 1: Métricas principales de éxito
    plot_metric(axs[0, 0], 'avg_score', 'Avg Score (Higher is better)', 'Points')
    plot_metric(axs[0, 1], 'avg_saved', 'Avg Victims Saved (Higher is better)', 'Count')
    
    # Fila 2: Eficiencia temporal y daño estructural
    plot_metric(axs[1, 0], 'avg_steps', 'Avg Duration (Global Ticks)', 'Rounds')
    plot_metric(axs[1, 1], 'avg_damage', 'Avg Structural Damage', 'Damage Units')
    
    # Fila 3: Esfuerzo operacional y eficiencia de rescate
    plot_metric(axs[2, 0], 'avg_distance', 'Avg Total Agent Movement', 'Total Steps')
    
    # Calcula métrica derivada de eficiencia: movimientos necesarios por víctima salvada
    eff_random = stats_random['avg_distance'] / stats_random['avg_saved'] if stats_random['avg_saved'] > 0 else 0
    eff_intel = stats_intelligent['avg_distance'] / stats_intelligent['avg_saved'] if stats_intelligent['avg_saved'] > 0 else 0
    
    plot_metric(axs[2, 1], None, 'Cost of Rescue (Movement per Saved Victim)', 'Steps / Victim', 
                is_derived=True, derived_vals=[eff_random, eff_intel])
    
    # Nota explicativa para la métrica de eficiencia
    axs[2, 1].text(0.5, -0.25, "(Lower is better: Less walking per rescue)", 
                   transform=axs[2, 1].transAxes, ha='center', color='darkred', fontsize=8)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('comparison_metrics.png')
    print("Graph saved: comparison_metrics.png")
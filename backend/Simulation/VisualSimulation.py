# VisualSimulation.py
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
import numpy as np
from multiprocessing import Pool, cpu_count
import time

from Simulation.SimulationManager import SimulationManager
from Simulation.SimulationAnalysis import calculate_summary_stats, print_comparison_table, plot_simulation_results

# CONFIGURACIÓN
WIDTH = 8
HEIGHT = 6
AGENTS = 6
PA = 4
BATCH_SIZE = 1000
MAX_ATTEMPTS = 10  # Aumentado para encontrar victorias
FPS = 15

def generate_gif(sim_data, filename, title_suffix=""):
    """ 
    Generador de GIF visual mejorado para coincidir con el tablero real.
    """
    print(f"🎬 Iniciando renderizado de: {filename}...")
    frames = sim_data["data"]["frames"]
    
    ROLE_COLORS = {
        "Firefighter": "red",     
        "Rescue": "cyan",         
        "Base": "black"           
    }
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 7.5))
    cmap = ListedColormap(['#f0f0f0', '#ffcc00', "#ff2a00"])  # Vacío, Humo (amarillo), Fuego (rojo)
    
    def update(frame_idx):
        ax.clear()
        current = frames[frame_idx]
        
        # === 1. MAPA DE FUEGO ===
        grid = np.zeros((HEIGHT, WIDTH))
        for f in current["fires"]: 
            grid[f["y"], f["x"]] = 2 if f["state"]==2 else 1
        
        # CRÍTICO: origin='upper' para que (0,0) esté arriba-izquierda
        ax.imshow(grid, cmap=cmap, vmin=0, vmax=2, origin='upper', extent=[-0.5, WIDTH-0.5, HEIGHT-0.5, -0.5])
        
        # === 2. GRID ===
        ax.set_xlim(-0.5, WIDTH-0.5)
        ax.set_ylim(HEIGHT-0.5, -0.5)  # Invertido para que Y crezca hacia abajo
        ax.set_xticks(np.arange(-0.5, WIDTH, 1))
        ax.set_yticks(np.arange(-0.5, HEIGHT, 1))
        ax.grid(color='gray', alpha=0.3, linewidth=0.5)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_aspect('equal')

        # === 3. PAREDES INTERNAS ===
        walls = current["walls"]
        
        for y in range(HEIGHT):
            for x in range(WIDTH):
                w = walls[y][x]
                
                # w[0] = Up, w[1] = Left, w[2] = Down, w[3] = Right
                if w[0] != '0':  # Pared arriba
                    ax.plot([x-0.5, x+0.5], [y-0.5, y-0.5], 'k-', lw=3)
                if w[1] != '0':  # Pared izquierda
                    ax.plot([x-0.5, x-0.5], [y-0.5, y+0.5], 'k-', lw=3)
                if w[2] != '0':  # Pared abajo
                    ax.plot([x-0.5, x+0.5], [y+0.5, y+0.5], 'k-', lw=3)
                if w[3] != '0':  # Pared derecha
                    ax.plot([x+0.5, x+0.5], [y-0.5, y+0.5], 'k-', lw=3)

        # === 4. PERÍMETRO DEL EDIFICIO (PAREDES EXTERIORES) ===
        # Arriba
        ax.plot([-0.5, WIDTH-0.5], [-0.5, -0.5], 'k-', lw=5)
        # Abajo
        ax.plot([-0.5, WIDTH-0.5], [HEIGHT-0.5, HEIGHT-0.5], 'k-', lw=5)
        # Izquierda
        ax.plot([-0.5, -0.5], [-0.5, HEIGHT-0.5], 'k-', lw=5)
        # Derecha
        ax.plot([WIDTH-0.5, WIDTH-0.5], [-0.5, HEIGHT-0.5], 'k-', lw=5)

        # === 5. PUERTAS INTERNAS ===
        for d in current["doors"]:
            p1, p2 = d["p1"], d["p2"]
            status = d["status"]
            
            # Color según estado
            if status == 'Closed':
                color = 'saddlebrown'
                style = '-'
                lw = 4
            elif status == 'Open':
                color = 'green'
                style = ':'
                lw = 3
            else:  # Destroyed
                color = 'red'
                style = ':'
                lw = 2
            
            # p1 y p2 son tuplas (y, x) según AuxFunctions
            y1, x1 = p1
            y2, x2 = p2
            
            # Puerta horizontal (misma Y)
            if y1 == y2:
                y_pos = y1 - 0.5 if y2 > y1 else y1 + 0.5
                x_center = (x1 + x2) / 2
                ax.plot([x_center - 0.4, x_center + 0.4], [y_pos, y_pos], 
                       color=color, ls=style, lw=lw)
            
            # Puerta vertical (misma X)
            elif x1 == x2:
                x_pos = x1 - 0.5 if x2 > x1 else x1 + 0.5
                y_center = (y1 + y2) / 2
                ax.plot([x_pos, x_pos], [y_center - 0.4, y_center + 0.4], 
                       color=color, ls=style, lw=lw)

        # === 6. PUERTAS EXTERIORES (Entry Points) ===
        entry_points = [
            (1, 6),  # Fila 1, Columna 6 -> y=0, x=5 (arriba)
            (3, 1),  # Fila 3, Columna 1 -> y=2, x=0 (izquierda)
            (4, 8),  # Fila 4, Columna 8 -> y=3, x=7 (derecha)
            (6, 3),  # Fila 6, Columna 3 -> y=5, x=2 (abajo)
        ]

        for row, col in entry_points:
            y = row - 1  # Convertir a 0-indexed
            x = col - 1
            
            # Determinar posición de la puerta exterior
            if y == 0:  # Pared superior
                ax.plot([x-0.3, x+0.3], [-0.5, -0.5], 'lime', lw=6, solid_capstyle='round')
                # REEMPLAZAR EMOJI por texto
                ax.text(x, -0.9, 'AMB', ha='center', va='center', fontsize=8, 
                    fontweight='bold', color='white',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='green', alpha=0.8))
            elif y == HEIGHT-1:  # Pared inferior
                ax.plot([x-0.3, x+0.3], [HEIGHT-0.5, HEIGHT-0.5], 'lime', lw=6, solid_capstyle='round')
                ax.text(x, HEIGHT-0.1, 'AMB', ha='center', va='center', fontsize=8,
                    fontweight='bold', color='white',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='green', alpha=0.8))
            elif x == 0:  # Pared izquierda
                ax.plot([-0.5, -0.5], [y-0.3, y+0.3], 'lime', lw=6, solid_capstyle='round')
                ax.text(-0.9, y, 'AMB', ha='center', va='center', fontsize=8, rotation=90,
                    fontweight='bold', color='white',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='green', alpha=0.8))
            elif x == WIDTH-1:  # Pared derecha
                ax.plot([WIDTH-0.5, WIDTH-0.5], [y-0.3, y+0.3], 'lime', lw=6, solid_capstyle='round')
                ax.text(WIDTH-0.1, y, 'AMB', ha='center', va='center', fontsize=8, rotation=90,
                    fontweight='bold', color='white',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='green', alpha=0.8))

        # === 7. POIs ===
        for p in current["pois"]:
            x, y = p["x"], p["y"]
            txt = "?"
            col = "blue"
            
            if p["revealed"]:
                if p["type"] in ['v', 'Victim', 'V']:
                    txt = "V"
                    col = "green"
                else:
                    txt = "F"
                    col = "purple"
            
            ax.text(x, y, txt, color=col, ha='center', va='center', 
                   fontweight='bold', fontsize=14, 
                   bbox=dict(boxstyle='circle', facecolor='white', alpha=0.8))

        # === 8. AGENTES ===
        counts = {}
        for a in current["agents"]: 
            pos = (a["x"], a["y"])
            counts[pos] = counts.get(pos, 0) + 1

        offsets = {}
        for a in current["agents"]:
            x, y = a["x"], a["y"]
            pos = (x, y)
            
            # Offset para múltiples agentes en la misma celda
            ox, oy = 0, 0
            if counts[pos] > 1:
                idx = offsets.get(pos, 0)
                if idx == 0: ox, oy = -0.15, 0
                elif idx == 1: ox, oy = 0.15, 0
                elif idx == 2: ox, oy = 0, -0.15
                elif idx == 3: ox, oy = 0, 0.15
                offsets[pos] = idx + 1
            
            role = a.get("role", "Base")
            color = ROLE_COLORS.get(role, "black")
            
            # Dibujar agente
            ax.scatter(x + ox, y + oy, c=color, s=250, zorder=10, 
                    edgecolors='white', linewidths=2)
            ax.text(x + ox, y + oy, str(a["id"]), color='white', 
                ha='center', va='center', fontweight='bold', fontsize=10)
            
            # Indicador de víctima cargada - REEMPLAZAR EMOJI
            if a["carrying"]:
                # Dibujar un círculo verde pequeño con "V"
                ax.scatter(x + ox + 0.3, y + oy - 0.3, c='lime', s=80, 
                        zorder=11, edgecolors='darkgreen', linewidths=1.5)
                ax.text(x + ox + 0.3, y + oy - 0.3, "V", 
                    color='darkgreen', fontsize=7, fontweight='bold',
                    ha='center', va='center', zorder=12)

        # === 9. TÍTULO Y STATS ===
        st = current["stats"]
        title = f"{title_suffix}\n"
        title += f"Paso {current['step']} | "
        title += f"Salvados: {st['saved']} | "
        title += f"Perdidos: {st['lost']} | "
        title += f"Daño: {st['damage']}/24"
        ax.set_title(title, fontsize=12, fontweight='bold')

        # Leyenda - SIN EMOJIS
        legend_text = "Rojo: Bombero | Cyan: Rescatista | Negro: Base\n"
        legend_text += "Rojo: Fuego | Amarillo: Humo | Gris: Vacio\n"
        legend_text += "Verde: Ambulancia | V: Victima | ?: POI"
        ax.text(0.5, -0.05, legend_text, transform=ax.transAxes,
            ha='center', va='top', fontsize=8, 
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ani = animation.FuncAnimation(fig, update, frames=len(frames), 
                                 interval=1000/FPS, repeat=True)
    ani.save(filename, writer='pillow', fps=FPS)
    plt.close(fig)
    print(f"✅ Guardado: {filename}")
    return filename

def find_winning_simulation(manager, strategy_name, max_attempts=50):
    """
    Busca simulaciones victoriosas.
    Retorna lista de tareas para GIF.
    """
    print(f"\n🔎 BUSCANDO VICTORIA PARA: {strategy_name.upper()}")
    
    winning_runs = []
    total_sims = 0
    
    for attempt in range(1, max_attempts + 1):
        batch_results = manager.run_batch_experiment(
            WIDTH, HEIGHT, AGENTS, PA, 
            iterations=BATCH_SIZE, 
            strategy_name=strategy_name
        )
        
        total_sims += BATCH_SIZE
        sorted_runs = batch_results["sorted_runs"]
        stats = batch_results["stats"]

        print(f"📊 Lote {attempt}: Victorias={stats['wins']} | "
              f"Perdidos={stats['loss_victims']} | Colapsos={stats['loss_collapse']}")
        
        # Recolectar TODAS las victorias
        for run in sorted_runs:
            if run["end_reason"] == "WIN":
                winning_runs.append(run)
        
        # Si encontramos al menos 2 victorias, podemos parar
        if len(winning_runs) >= 2:
            print(f"\n✨ ¡Encontradas {len(winning_runs)} VICTORIAS!")
            break
    
    if not winning_runs:
        print("⚠️ No se encontraron victorias.")
        return []
    
    # Ordenar por score
    winning_runs.sort(key=lambda x: x["score"], reverse=True)
    
    # Preparar tareas para GIF
    tasks = []
    
    # Mejor victoria
    best_win = winning_runs[0]
    title_best = f"{strategy_name.upper()} - MEJOR VICTORIA " \
                f"(Salvados: {best_win['saved']}, Pasos: {best_win['steps']})"
    tasks.append((best_win['replay_data'], f"{strategy_name}_Victoria_Mejor.gif", title_best))
    
    # Si hay más victorias, mostrar la más rápida
    if len(winning_runs) > 1:
        fastest = min(winning_runs, key=lambda x: x['steps'])
        title_fast = f"{strategy_name.upper()} - VICTORIA MÁS RÁPIDA " \
                    f"({fastest['steps']} pasos)"
        tasks.append((fastest['replay_data'], f"{strategy_name}_Victoria_Rapida.gif", title_fast))
    
    return tasks

def analyze_strategy(manager, strategy_name):
    """
    Ejecuta simulaciones y retorna tareas para GIF.
    """
    print(f"\n\n🔵 ESTRATEGIA: {strategy_name.upper()}")
    
    experiment_data = manager.run_batch_experiment(
        WIDTH, HEIGHT, AGENTS, PA, 
        iterations=BATCH_SIZE, 
        strategy_name=strategy_name
    )
    
    stats = experiment_data["stats"]
    ranked_runs = experiment_data["sorted_runs"]
    
    print(f"📊 Victorias: {stats['wins']} | "
          f"Perdidos: {stats['loss_victims']} | "
          f"Colapsos: {stats['loss_collapse']}")
    
    # Asegurar que hay datos para seleccionar el mejor/peor
    if not ranked_runs:
        return [], []

    best_run = ranked_runs[0]
    worst_run = ranked_runs[-1]

    tasks = []
    
    # Mejor caso
    title_best = f"{strategy_name.upper()} - MEJOR " \
                f"(Salvados: {best_run['saved']}, Daño: {best_run['damage']})"
    tasks.append((best_run['replay_data'], f"{strategy_name}_Mejor.gif", title_best))

    # Peor caso
    title_worst = f"{strategy_name.upper()} - PEOR ({worst_run['end_reason']})"
    tasks.append((worst_run['replay_data'], f"{strategy_name}_Peor.gif", title_worst))

    return tasks, ranked_runs

if __name__ == "__main__":
    manager = SimulationManager()
    gif_tasks_queue = []

    # Variables para almacenar los resultados del lote estadístico
    results_random = []
    results_intelligent = []

    start_time = time.time()

    # --- ANALIZAR ESTRATEGIA RANDOM (Lote Estadístico y Mejores GIFs) ---
    print("\n" + "="*60)
    print("🎲 ANALIZANDO ESTRATEGIA RANDOM (Base)")
    print("="*60)
    tasks_random_batch, results_random = analyze_strategy(manager, "random")
    gif_tasks_queue.extend(tasks_random_batch)


    # --- ANALIZAR ESTRATEGIA INTELLIGENT ---
    print("\n" + "="*60)
    print("🧠 ANALIZANDO ESTRATEGIA INTELLIGENT (Especializados)")
    print("="*60)
    tasks_intelligent_batch, results_intelligent = analyze_strategy(manager, "intelligent")
    gif_tasks_queue.extend(tasks_intelligent_batch)

    # --- 3. GENERAR Y MOSTRAR ESTADÍSTICAS COMPARATIVAS ---
    if results_random and results_intelligent:
        stats_random = calculate_summary_stats("random", results_random)
        stats_intelligent = calculate_summary_stats("intelligent", results_intelligent)
        print_comparison_table(stats_random, stats_intelligent)
        print("\n📈 Generando gráficas comparativas (PNG)...")
        plot_simulation_results(stats_random, stats_intelligent)
    else:
        print("\n❌ No se pudieron generar suficientes resultados para la tabla de comparación.")

    # --- GENERAR TODOS LOS GIFs e Imagenes ---
    print("\n" + "="*60)
    if gif_tasks_queue:
        print(f"🚀 GENERANDO {len(gif_tasks_queue)} GIFs EN PARALELO")
        print("="*60)

        num_cores = cpu_count()
        with Pool(processes=num_cores) as pool:
            pool.starmap(generate_gif, gif_tasks_queue)
    else:
        print("❌ No hay GIFs para generar.")

    elapsed = time.time() - start_time
    print(f"\n✨ COMPLETADO EN {elapsed:.2f} SEGUNDOS ✨")
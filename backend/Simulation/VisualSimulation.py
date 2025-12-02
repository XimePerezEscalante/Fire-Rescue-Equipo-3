# VisualSimulation.py
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
import numpy as np
from multiprocessing import Pool, cpu_count
import time

from Simulation.SimulationManager import SimulationManager

# CONFIGURACIÓN
WIDTH = 8
HEIGHT = 6
AGENTS = 6
PA = 4
BATCH_SIZE = 5000
MAX_ATTEMPTS = 1
FPS = 2

def generate_gif(sim_data, filename, title_suffix=""):
    """ 
    Generador de GIF visual. 
    Esta función debe ser 'top-level' para funcionar con multiprocessing.
    """
    print(f"🎬 Iniciando renderizado de: {filename}...")
    frames = sim_data["data"]["frames"]
    
    # Intentar obtener metadata, si falla no pasa nada
    meta = sim_data.get("data", {}).get("metadata", {})

    ROLE_COLORS = {
        "Firefighter": "red",     
        "Rescue": "cyan",         
        "Base": "black"           
    }
    
    # Crear figura nueva para este proceso
    fig, ax = plt.subplots(figsize=(8, 6))
    cmap = ListedColormap(['#f0f0f0', '#888888', '#ff4400']) 
    
    def update(frame_idx):
        ax.clear()
        current = frames[frame_idx]
        
        # Mapa Fuego
        grid = np.zeros((HEIGHT, WIDTH))
        for f in current["fires"]: grid[f["y"], f["x"]] = 2 if f["state"]==2 else 1
        ax.imshow(grid, cmap=cmap, vmin=0, vmax=2, origin='lower')
        
        # Grid
        ax.set_xticks(np.arange(-0.5, WIDTH, 1)); ax.set_yticks(np.arange(-0.5, HEIGHT, 1))
        ax.grid(color='gray', alpha=0.3); ax.set_xticklabels([]); ax.set_yticklabels([])

        # Paredes
        walls = current["walls"]
        for y in range(HEIGHT):
            for x in range(WIDTH):
                w = walls[y][x]
                if w[0]!='0': ax.plot([x-0.5, x+0.5], [y+0.5, y+0.5], 'k-', lw=3)
                if w[1]!='0': ax.plot([x-0.5, x-0.5], [y-0.5, y+0.5], 'k-', lw=3)
                if w[2]!='0': ax.plot([x-0.5, x+0.5], [y-0.5, y-0.5], 'k-', lw=3)
                if w[3]!='0': ax.plot([x+0.5, x+0.5], [y-0.5, y+0.5], 'k-', lw=3)

        # Puertas
        for d in current["doors"]:
            p1, p2 = d["p1"], d["p2"]
            color = 'saddlebrown'; style = '-' if d["status"]=='Closed' else ':'
            if p1[1]==p2[1]: # H
                yb = max(p1[0], p2[0])-0.5
                ax.plot([p1[1]-0.5, p1[1]+0.5], [yb, yb], color=color, ls=style, lw=3)
            elif p1[0]==p2[0]: # V
                xb = max(p1[1], p2[1])-0.5
                ax.plot([xb, xb], [p1[0]-0.5, p1[0]+0.5], color=color, ls=style, lw=3)

        # POIs
        for p in current["pois"]:
            txt = "?"; col = "blue"
            if p["revealed"]:
                txt = "V" if p["type"] in ['v','Victim'] else "F"
                col = "green" if txt=="V" else "purple"
            ax.text(p["x"], p["y"], txt, color=col, ha='center', va='center', fontweight='bold', fontsize=12)

        # Agentes
        counts = {}
        for a in current["agents"]: counts[(a["x"], a["y"])] = counts.get((a["x"], a["y"]), 0) + 1
        offsets = {}
        for a in current["agents"]:
            pos = (a["x"], a["y"])
            ox = 0
            if counts[pos] > 1:
                idx = offsets.get(pos, 0); ox = (idx*0.3)-0.15; offsets[pos] = idx+1
            
            role = a.get("role", "Base")
            color = ROLE_COLORS.get(role, "black")
            
            ax.scatter(pos[0]+ox, pos[1], c=color, s=200, zorder=10, edgecolors='white')
            ax.text(pos[0]+ox, pos[1], str(a["id"]), color='white', ha='center', va='center', fontweight='bold')
            if a["carrying"]: ax.text(pos[0]+ox+0.3, pos[1]-0.3, "✚", color='lime', fontsize=12, fontweight='bold')

        st = current["stats"]
        ax.set_title(f"{title_suffix}\nPaso {current['step']} | Salvados: {st['saved']} | Perdidos: {st['lost']} | Daño: {st['damage']}")

    ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=1000/FPS, repeat=True)
    ani.save(filename, writer='pillow', fps=FPS)
    plt.close(fig) # Importante cerrar la figura para liberar memoria
    print(f"✅ Guardado: {filename}")
    return filename

def find_winning_simulation(manager, strategy_name):
    """
    Ejecuta lotes de simulaciones en bucle hasta encontrar una victoria (WIN).
    Retorna una lista de tareas para generar GIF (Mejor Victoria y Peor Derrota global).
    """
    print(f"\n🔎 BUSCANDO VICTORIA PARA: {strategy_name.upper()}")
    
    global_worst_run = None
    winning_run = None
    
    total_sims_count = 0
    
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"   ↳ Lote {attempt}/{MAX_ATTEMPTS} (Simulaciones {total_sims_count} - {total_sims_count + BATCH_SIZE})...", end="\r")
        
        # 1. Ejecutar Lote
        batch_results = manager.run_batch_experiment(
            WIDTH, HEIGHT, AGENTS, PA, 
            iterations=BATCH_SIZE, 
            strategy_name=strategy_name
        )
        
        total_sims_count += BATCH_SIZE
        sorted_runs = batch_results["sorted_runs"]
        stats = batch_results["stats"]

        print(f"📊 REPORTE LOTE {attempt} ({strategy_name})")
        print(f"🏆 Victorias: {stats['wins']} | 💀 Muerte Víctimas: {stats['loss_victims']} | 🏚️ Colapsos: {stats['loss_collapse']}")
        print("-" * 20)
        
        # 2. Actualizar el Peor Caso Global (para comparar al final)
        current_worst = sorted_runs[-1]
        if global_worst_run is None or current_worst["score"] < global_worst_run["score"]:
            global_worst_run = current_worst
            
        # 3. Buscar Victoria
        # Como sorted_runs está ordenado por score descendente, si hay victorias, estarán al principio.
        # Asumimos que una victoria tiene score positivo alto o checkeamos end_reason
        if batch_results["stats"]["wins"] > 0:
            # Encontramos al menos una victoria
            for run in sorted_runs:
                if run["end_reason"] == "WIN":
                    winning_run = run
                    break
            
            if winning_run:
                print(f"\n✨ ¡VICTORIA ENCONTRADA en la simulación #{total_sims_count - BATCH_SIZE + winning_run['id']}!")
                print(f"   (Intentos totales: {total_sims_count})")
                break
        
        # Si no encontramos victoria, el bucle continúa
    
    print("-" * 40)
    
    tasks = []
    
    # Preparar Tarea: MEJOR CASO (Victoria o lo mejor que se haya encontrado si se agotaron intentos)
    if winning_run:
        title_best = f"{strategy_name.upper()} - VICTORIA (Salvados: {winning_run['saved']} en {winning_run['steps']} pasos)"
        tasks.append((winning_run['replay_data'], f"{strategy_name}_WIN.gif", title_best))
    else:
        print("⚠️ No se encontró ninguna victoria en el límite de intentos.")
        # Opcional: Renderizar el mejor intento fallido
        best_fail = sorted_runs[0] # El mejor del último lote
        title_fail = f"{strategy_name.upper()} - MEJOR INTENTO (FALLIDO)"
        tasks.append((best_fail['replay_data'], f"{strategy_name}_BestFail.gif", title_fail))

    # Preparar Tarea: PEOR CASO GLOBAL
    if global_worst_run:
        title_worst = f"{strategy_name.upper()} - PEOR ({global_worst_run['end_reason']})"
        tasks.append((global_worst_run['replay_data'], f"{strategy_name}_Worst.gif", title_worst))

    return tasks

def analyze_strategy(manager, strategy_name):
    """
    Ejecuta las simulaciones y retorna los datos necesarios para visualizar,
    pero NO genera los GIFs todavía.
    """
    print(f"\n\n🔵 INICIANDO CÁLCULOS: ESTRATEGIA {strategy_name.upper()}")
    
    experiment_data = manager.run_batch_experiment(
        WIDTH, HEIGHT, AGENTS, PA, 
        iterations=BATCH_SIZE, 
        strategy_name=strategy_name
    )
    
    stats = experiment_data["stats"]
    ranked_runs = experiment_data["sorted_runs"]
    
    print(f"📊 REPORTE ({strategy_name})")
    print(f"🏆 Victorias: {stats['wins']} | 💀 Muerte Víctimas: {stats['loss_victims']} | 🏚️ Colapsos: {stats['loss_collapse']}")
    print("-" * 20)

    # Preparamos los datos para devolverlos
    best_run = ranked_runs[0]
    worst_run = ranked_runs[-1]

    # Devolvemos una lista de tareas (tuplas) listas para ser procesadas por generate_gif
    # Formato: (datos, nombre_archivo, titulo)
    tasks = []

    # Tarea 1: Mejor Caso
    title_best = f"{strategy_name.upper()} - MEJOR (Salvados: {best_run['saved']}, Daño: {best_run['damage']})"
    tasks.append( (best_run['replay_data'], f"{strategy_name}_Mejor.gif", title_best) )

    # Tarea 2: Peor Caso
    title_worst = f"{strategy_name.upper()} - PEOR ({worst_run['end_reason']})"
    tasks.append( (worst_run['replay_data'], f"{strategy_name}_Peor.gif", title_worst) )

    return tasks

if __name__ == "__main__":
    manager = SimulationManager()
    gif_tasks_queue = []

    start_time = time.time()

    # 1. Buscar Victoria Random
    tasks_random = analyze_strategy(manager, "random")
    gif_tasks_queue.extend(tasks_random)
    
    # 2. Buscar Victoria Intelligent
    tasks_intelligent = find_winning_simulation(manager, "intelligent")
    gif_tasks_queue.extend(tasks_intelligent)

    print("\n" + "="*50)
    if gif_tasks_queue:
        print(f"🚀 GENERANDO {len(gif_tasks_queue)} GIFs EN PARALELO")
        print("="*50)
        
        num_cores = cpu_count()
        with Pool(processes=num_cores) as pool:
            pool.starmap(generate_gif, gif_tasks_queue)
    else:
        print("❌ No hay GIFs para generar.")

    elapsed = time.time() - start_time
    print(f"\n✨ PROCESO COMPLETADO EN {elapsed:.2f} SEGUNDOS ✨")
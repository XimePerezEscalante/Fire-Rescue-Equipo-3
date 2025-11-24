from ExplorerModel import ExplorerModel
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap
import seaborn as sns

# Configuración inicial
sns.set_theme()
GRID_WIDTH = 8
GRID_HEIGHT = 6
AGENTS = 1
MAX_ENERGY = 100

# Inicializar modelo
model = ExplorerModel(GRID_WIDTH, GRID_HEIGHT, AGENTS, MAX_ENERGY)

# Correr simulación
while not model.is_all_clean():
    model.step()

# Obtener datos para animación
all_grids = model.datacollector.get_model_vars_dataframe()

# --- CONFIGURACIÓN VISUAL ---
fig, axs = plt.subplots(figsize=(7, 7))
axs.set_xticks([])
axs.set_yticks([])

# Definir mapa de colores según la lógica de AuxFunctions.get_grid:
# 0: Vacío (Blanco)
# 1: Base (Azul)
# 2: Fuego (Rojo)
# 3: POI (Verde)
# 4: Agente (Negro)
colors = ['#f0f0f0', 'blue', 'red', '#2ecc71', 'black'] # Usé un gris muy claro para vacío para ver mejor las paredes cyan
cmap = ListedColormap(colors)

# Dibujar estado inicial
# Nota: vmin=0, vmax=4 asegura que los números se mapeen fijo a los colores
patch = axs.imshow(all_grids.iloc[0]["Grid"], cmap=cmap, vmin=0, vmax=4)

# --- DIBUJAR PAREDES ---
# Usamos la matriz de paredes del modelo
walls = model.walls
for y in range(len(walls)):
    for x in range(len(walls[y])):
        w = walls[y][x]
        # w es "Arriba Izq Abajo Der"
        
        # Coordenadas visuales: x es columna, y es fila.
        # Arriba (y-0.5), Abajo (y+0.5), Izq (x-0.5), Der (x+0.5)
        
        if w[0] == '1': # Arriba
            axs.plot([x-0.5, x+0.5], [y-0.5, y-0.5], color='cyan', linewidth=2)
        if w[1] == '1': # Izquierda
            axs.plot([x-0.5, x-0.5], [y-0.5, y+0.5], color='cyan', linewidth=2)
        if w[2] == '1': # Abajo
            axs.plot([x-0.5, x+0.5], [y+0.5, y+0.5], color='cyan', linewidth=2)
        if w[3] == '1': # Derecha
            axs.plot([x+0.5, x+0.5], [y-0.5, y+0.5], color='cyan', linewidth=2)

if hasattr(model, 'doors'):
    for d in model.doors:
        # d es ['r1', 'c1', 'r2', 'c2'] (strings)
        r1, c1, r2, c2 = int(d[0]), int(d[1]), int(d[2]), int(d[3])
        
        # Convertir a coordenadas de plot (x=col, y=row)
        # La pared está ENTRE (c1, r1) y (c2, r2)
        
        # Calculamos el punto medio para saber dónde dibujar la línea
        x_mid = (c1 + c2) / 2.0
        y_mid = (r1 + r2) / 2.0
        
        # Si la diferencia es en X (Puerta vertical)
        if c1 != c2:
            # Dibujamos línea vertical en x_mid, desde y-0.5 a y+0.5
            # Como r1 y r2 son iguales, usamos r1
            axs.plot([x_mid, x_mid], [r1-0.5, r1+0.5], color='gray', linewidth=4)
            
        # Si la diferencia es en Y (Puerta horizontal)
        elif r1 != r2:
            # Dibujamos línea horizontal en y_mid, desde x-0.5 a x+0.5
            axs.plot([c1-0.5, c1+0.5], [y_mid, y_mid], color='gray', linewidth=4)

# Actualizar Leyenda para incluir la Puerta

# Leyenda
legend_elements = [
    Patch(facecolor='blue', edgecolor='black', label='Base'),
    Patch(facecolor='red', edgecolor='black', label='Fuego'),
    Patch(facecolor='#2ecc71', edgecolor='black', label='POI'),
    Patch(facecolor='black', edgecolor='black', label='Agente'),
    Patch(facecolor='gray', edgecolor='gray', label='Puerta')
]
axs.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.3, 1))

def animate(i):
    patch.set_data(all_grids.iloc[i]["Grid"])
    axs.set_title(f"Paso: {i}")

# Crear animación
anim = animation.FuncAnimation(fig, animate, frames=len(all_grids))
# Guardar o mostrar
anim.save("bomberos_fixed.gif", writer='pillow', fps=5)
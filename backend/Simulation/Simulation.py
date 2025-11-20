from ExplorerModel import *

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Patch # Para poder añadir las labels en la animación
from matplotlib.colors import ListedColormap # Para mapear los colores
plt.rcParams["animation.html"] = "jshtml"
matplotlib.rcParams['animation.embed_limit'] = 2**128

# Importamos los siguientes paquetes para el mejor manejo de valores numéricos.
import seaborn as sns
sns.set_theme()


GRID_SIZE = 11
AGENTS = 5
# RESOURCES = 20
MAX_ENERGY = 4

model = ExplorerModel(8, 6, AGENTS, MAX_ENERGY)
while not model.is_all_clean():
    model.step()

# model_info = model.datacollector.get_model_vars_dataframe()
# print(model_info.info())

# plt.figure(figsize=(8, 6))
# #Ayuda para el correcto despliegue de información generado con IA - Chat GPT
# sns.lineplot(data=model_info, x='Steps', y='CleanPercentage')
# plt.title('Evolución de la limpieza')
# plt.xlabel('Pasos')
# plt.ylabel('Fracción Limpia')
# plt.grid(True)
# plt.savefig("evolucion.png")

# agents_info = model.datacollector.get_agent_vars_dataframe()
# print(agents_info)



# plt.figure(figsize=(10, 6))
# #Ayuda para el correcto despliegue de información generado con IA - Chat GPT
# sns.barplot(data=agents_info.reset_index(), x='AgentID', y='ResourcesCollected', hue='TimesRecharged')
# plt.title('Recursos Recolectados y Recargas por Agente')
# plt.xlabel('ID del Agente')
# plt.ylabel('Recursos Recolectados')
# plt.legend(title='Veces Recargadas')
# plt.grid(axis='y', linestyle='--', alpha=0.7)
# plt.savefig("recursos.png")


all_grids = model.datacollector.get_model_vars_dataframe()
print(all_grids.info())


fig, axs = plt.subplots(figsize=(6,4))
axs.set_xticks([])
axs.set_yticks([])
# Crear leyenda. Generado con IA (Chat GPT)
colors = ['white', 'red', 'blue', 'black']
cmap = ListedColormap(colors)
patch = plt.imshow(all_grids.iloc[0, 0], cmap=cmap, vmin=0, vmax=3)
legend_elements = [
    Patch(facecolor='red', edgecolor='black', label='Comida'),
    Patch(facecolor='blue', edgecolor='black', label='Base'),
    Patch(facecolor='black', edgecolor='black', label='Agente')
]

def animate(i):
    patch.set_data(all_grids.iloc[i, 0])
    axs.set_title(f"Iteración {i}/{len(all_grids)-1}")
    axs.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1))

anim = animation.FuncAnimation(fig, animate, frames=range(len(all_grids)))

anim.save("animation.gif")
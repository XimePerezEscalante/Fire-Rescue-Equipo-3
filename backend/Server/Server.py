from flask import Flask, request, jsonify
from Simulation.Simulation import Simulation
import json

# Configuración inicial
GRID_WIDTH = 8
GRID_HEIGHT = 6
AGENTS = 6
MAX_ENERGY = 100

app = Flask("FireRescueServer")

class Server():
    def __init__(self):
        self.simulation = None

    # --- RUTA 3: Solo para probar que el servidor vive ---
    @app.route('/init', methods=['POST'])
    def init():
        data = request.json
        num_agents = data.get("agents", AGENTS) if data else AGENTS

    # --- RUTA 1: Ejecutar la simulación principal ---
    # En Unity llamarás a: http://localhost:8585/simulation
    @app.route('/simulation', methods=['POST'])
    def run_simulation():
        # 1. Recibir parámetros de Unity (opcional)
        # Si Unity envía {"agents": 10}, lo usamos. Si no, usamos el default.
        data = request.json
        num_agents = data.get("agents", AGENTS) if data else AGENTS
        print(data)
        print(f"Recibida petición de simulación con {num_agents} agentes.")

        # 2. Correr la lógica (Copiado de tu código original)
        simulation = Simulation(GRID_WIDTH, GRID_HEIGHT, num_agents, MAX_ENERGY)
        simulation.runSimulation()
        
        results = []
        
        # Procesar posiciones (Copiado de tu código original)
        if hasattr(simulation.model.agents_positions, 'columns'):
            for agent_id in simulation.model.agents_positions.columns:
                path_list = []
                for step_pos in simulation.model.agents_positions[agent_id]:
                    x_grid = float(step_pos[0])
                    y_grid = float(step_pos[1])
                    # Unity usa Y como altura, por eso Z es la coordenada Y del grid
                    pos_obj = {"x": x_grid, "y": 0.5, "z": y_grid}
                    path_list.append(pos_obj)
                results.append({"id": int(agent_id), "path": path_list})
                
        final_data = {"results": results}

        # Opcional: Mostrar la gráfica en el servidor (Cuidado: esto abre una ventana en Python)
        # simulation.show() 

        # 3. Responder a Unity
        return jsonify(final_data)

    # --- RUTA 2: Nueva función (Ejemplo: Obtener Mapa) ---
    # En Unity llamarás a: http://localhost:8585/getMap
    @app.route('/getMap', methods=['GET', 'POST'])
    def get_map():
        # Aquí podrías leer tu archivo txt o instanciar el modelo para sacar las paredes
        map_info = {
            "width": GRID_WIDTH,
            "height": GRID_HEIGHT,
            "walls" : 0,
        }
        return jsonify(map_info)

if __name__ == '__main__':
    # debug=True permite que el servidor se reinicie si haces cambios en el código
    app.run(port=8585, debug=True)
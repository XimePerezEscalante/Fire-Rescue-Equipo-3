from flask import Flask, request, jsonify
from Simulation.Simulation import Simulation
from Simulation.SimulationManager import SimulationManager
from Simulation.AuxFunctions import formatMap
import json

DEFAULT_CONFIG = {
    "grid_width": 8,
    "grid_height": 6,
    "agents": 6,
    "max_energy": 4
}

class Server:
    def __init__(self, port=8585):
        self.port = port
        self.app = Flask("FireRescueServer")
        self.simulation_config = DEFAULT_CONFIG.copy()
        self.configure_routes()

    def configure_routes(self):
        self.app.add_url_rule('/init', view_func=self.init_params, methods=['POST'])
        self.app.add_url_rule('/getMap', view_func=self.get_map_data, methods=['GET'])
        
        # Rutas actualizadas
        self.app.add_url_rule('/simulation/random', view_func=self.run_single_simulation_random, methods=['POST'])
        self.app.add_url_rule('/simulation/intelligent', view_func=self.run_single_simulation_intelligent, methods=['POST'])
        
        self.app.add_url_rule('/run_batch', view_func=self.run_batch_experiment, methods=['POST'])

    def run(self):
        print(f"🔥 Servidor iniciado en http://localhost:{self.port}")
        self.app.run(port=self.port, debug=True)

    # --- ENDPOINT 1: Configuración ---
    def init_params(self):
        data = request.json
        if not data:
            self.simulation_config = DEFAULT_CONFIG.copy()
            return jsonify({"msg": "Default config loaded", "config": self.simulation_config})
        
        try:
            self.simulation_config["agents"] = int(data.get("agents", DEFAULT_CONFIG["agents"]))
            self.simulation_config["max_energy"] = int(data.get("maxEnergy", DEFAULT_CONFIG["max_energy"]))
            self.simulation_config["random_fires"] = data.get("num_fires", None) 
            self.simulation_config["random_pois"] = data.get("num_pois", None)
            
            return jsonify({"msg": "Config updated", "config": self.simulation_config})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # --- ENDPOINT 2: Obtener Mapa ---
    def get_map_data(self):
        try:
            map_data = formatMap()
            response = {
                "width": self.simulation_config["grid_width"],
                "height": self.simulation_config["grid_height"]
            }
            response.update(map_data)
            return jsonify(response)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # --- HELPER: Lógica compartida para buscar la mejor simulación ---
    def _run_best_simulation(self, strategy_name, iterations=1000):
        """
        Ejecuta un lote de simulaciones, elige la mejor y retorna 
        su JSON de reproducción (replay_data).
        """
        manager = SimulationManager()
        
        # Ejecutamos el lote en paralelo
        experiment_data = manager.run_batch_experiment(
            self.simulation_config['grid_width'], 
            self.simulation_config['grid_height'], 
            self.simulation_config['agents'], 
            self.simulation_config["max_energy"], 
            iterations=iterations,
            strategy_name=strategy_name
        )
        
        # Obtenemos la lista ordenada (el índice 0 es el mejor puntaje)
        ranked_runs = experiment_data["sorted_runs"]
        
        if not ranked_runs:
            return {"error": "No simulations ran"}

        best_run = ranked_runs[0]
        
        print(f"✅ Mejor simulación encontrada ({strategy_name}): Score {best_run['score']} - ID {best_run['id']}")
        
        # Retornamos DIRECTAMENTE el replay_data que ya calculó el SimulationManager
        return best_run["replay_data"]

    # --- ENDPOINT 3: Simulación Random (Mejor de N intentos) ---
    def run_single_simulation_random(self):
        # Puedes ajustar 'iterations' según qué tan rápido quieras la respuesta.
        # 1000 iteraciones podría tardar mucho en responder a Unity. 
        # 50 o 100 suele ser suficiente para encontrar una buena ruta.
        result_json = self._run_best_simulation(strategy_name="random", iterations=1000)
        return jsonify(result_json)
    
    # --- ENDPOINT 4: Simulación Inteligente (Mejor de N intentos) ---
    def run_single_simulation_intelligent(self):
        # Incluso para la inteligente, a veces el azar (posiciones iniciales) afecta.
        # Corremos un lote pequeño para asegurar el mejor comportamiento.
        result_json = self._run_best_simulation(strategy_name="intelligent")
        print(result_json)
        return jsonify(result_json)

    # --- ENDPOINT 5: Lote Paralelo (Estadístico puro) ---
    def run_batch_experiment(self):
        cfg = self.simulation_config
        data = request.json or {}
        iterations = data.get("iterations", 10)
        strategy = data.get("strategy", "intelligent")

        manager = SimulationManager()
        results = manager.run_batch_experiment(
            cfg["grid_width"], cfg["grid_height"], 
            cfg["agents"], cfg["max_energy"],
            iterations=iterations,
            strategy_name = strategy
        )
        return jsonify(results)
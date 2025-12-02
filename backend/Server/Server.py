from flask import Flask, request, jsonify
from Simulation.Simulation import Simulation
from Simulation.SimulationManager import SimulationManager
from Simulation.AuxFunctions import readMap
import json

DEFAULT_CONFIG = {
    "grid_width": 8,
    "grid_height": 6,
    "agents": 6,
    "max_energy": 4,
    # "random_fires": None,
    # "random_pois": None
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
        self.app.add_url_rule('/simulation', view_func=self.run_single_simulation, methods=['POST'])
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
            # Actualizamos valores
            self.simulation_config["agents"] = int(data.get("agents", DEFAULT_CONFIG["agents"]))
            self.simulation_config["max_energy"] = int(data.get("maxEnergy", DEFAULT_CONFIG["max_energy"]))
            # Si el cliente manda num_fires, activamos modo aleatorio
            self.simulation_config["random_fires"] = data.get("num_fires", None) 
            self.simulation_config["random_pois"] = data.get("num_pois", None)
            
            return jsonify({"msg": "Config updated", "config": self.simulation_config})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # --- ENDPOINT 2: Obtener Mapa ---
    def get_map_data(self):
        try:
            map_data = readMap()
            response = {
                "width": self.simulation_config["grid_width"],
                "height": self.simulation_config["grid_height"]
            }
            response.update(map_data)
            return jsonify(response)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # --- ENDPOINT 3: Simulación Única (Visual) ---
    def run_single_simulation(self):
        # Extraemos configuración
        cfg = self.simulation_config
        data = request.json or {}
        strategy = data.get("strategy", "random")

        
        sim = Simulation(
            cfg["grid_width"], cfg["grid_height"], 
            cfg["agents"], cfg["max_energy"],
            strategy=strategy
        )
        sim.run()
        
        # Formatear para Unity
        return jsonify(sim.get_results_json())

    # --- ENDPOINT 4: Lote Paralelo (Estadístico) ---
    def run_batch_experiment(self):
        cfg = self.simulation_config
        # Si el cliente manda parámetros específicos para el batch, usarlos, si no, usar config
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
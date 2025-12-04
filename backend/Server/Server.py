from flask import Flask, request, jsonify
from Simulation.Simulation import Simulation
from Simulation.SimulationManager import SimulationManager
from Simulation.AuxFunctions import formatMap
import json

# Configuración por defecto utilizada
DEFAULT_CONFIG = {
    "grid_width": 8,
    "grid_height": 6,
    "agents": 6,
    "max_energy": 4
}

class Server:
    """
    Servidor Flask que gestiona simulaciones de rescate en incendios.
    Proporciona endpoints REST para configurar y ejecutar simulaciones con diferentes estrategias.
    """
    
    def __init__(self, port=8585):
        """
        Inicializa el servidor Flask y configura los parámetros básicos.
        
        Parámetros:
            port (int): Puerto en el que se ejecutará el servidor (valor por defecto: 8585)
        """
        self.port = port
        self.app = Flask("FireRescueServer")
        self.simulation_config = DEFAULT_CONFIG.copy()
        self.configure_routes()

    def configure_routes(self):
        """
        Configura todas las rutas (endpoints) disponibles en el servidor.
        Asocia cada URL con su método correspondiente y define los métodos HTTP permitidos.
        """
        self.app.add_url_rule('/init', view_func=self.init_params, methods=['POST'])
        self.app.add_url_rule('/getMap', view_func=self.get_map_data, methods=['GET'])
        
        # Endpoints para ejecutar simulaciones individuales con estrategias específicas
        self.app.add_url_rule('/simulation/random', view_func=self.run_single_simulation_random, methods=['POST'])
        self.app.add_url_rule('/simulation/intelligent', view_func=self.run_single_simulation_intelligent, methods=['POST'])
        
        # Endpoint para ejecutar experimentos con múltiples simulaciones en paralelo
        self.app.add_url_rule('/run_batch', view_func=self.run_batch_experiment, methods=['POST'])

    def run(self):
        """
        Inicia el servidor Flask en el puerto configurado.
        """
        print(f"Servidor iniciado en http://localhost:{self.port}")
        self.app.run(port=self.port, debug=True)

    def init_params(self):
        """
        Configura los parámetros de simulación mediante una petición POST.
        Si no se envían datos, carga la configuración por defecto.
        
        Retorna:
            JSON con mensaje de confirmación y la configuración actual aplicada.
            En caso de error, retorna JSON con descripción del error y código 400.
        """
        data = request.json
        if not data:
            self.simulation_config = DEFAULT_CONFIG.copy()
            return jsonify({"msg": "Default config loaded", "config": self.simulation_config})
        
        try:
            # Actualiza únicamente los parámetros recibidos, manteniendo los demás sin cambios
            self.simulation_config["agents"] = int(data.get("agents", DEFAULT_CONFIG["agents"]))
            self.simulation_config["max_energy"] = int(data.get("maxEnergy", DEFAULT_CONFIG["max_energy"]))
            self.simulation_config["random_fires"] = data.get("num_fires", None) 
            self.simulation_config["random_pois"] = data.get("num_pois", None)
            
            return jsonify({"msg": "Config updated", "config": self.simulation_config})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def get_map_data(self):
        """
        Obtiene los datos del mapa de simulación mediante una petición GET.
        Lee el mapa desde archivo y combina la información con las dimensiones configuradas.
        
        Retorna:
            JSON con las dimensiones del grid y los datos del mapa (muros, fuegos, POIs).
            En caso de error, retorna JSON con descripción del error y código 500.
        """
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

    def _run_best_simulation(self, strategy_name, iterations=1000):
        """
        Ejecuta múltiples simulaciones en paralelo y selecciona la mejor según el puntaje obtenido.
        Este método es auxiliar y no se expone directamente como endpoint.
        
        Parámetros:
            strategy_name (str): Nombre de la estrategia a utilizar ('random' o 'intelligent')
            iterations (int): Número de simulaciones a ejecutar para encontrar la mejor (valor por defecto: 1000)
        
        Retorna:
            dict: Datos de reproducción (replay_data) de la simulación con mejor puntaje.
                  En caso de no ejecutarse ninguna simulación, retorna diccionario con error.
        """
        manager = SimulationManager()
        
        # Ejecuta el lote completo de simulaciones en paralelo para optimizar el tiempo de respuesta
        experiment_data = manager.run_batch_experiment(
            self.simulation_config['grid_width'], 
            self.simulation_config['grid_height'], 
            self.simulation_config['agents'], 
            self.simulation_config["max_energy"], 
            iterations=iterations,
            strategy_name=strategy_name
        )
        
        # Obtiene la lista ordenada descendentemente por puntaje
        ranked_runs = experiment_data["sorted_runs"]
        
        if not ranked_runs:
            return {"error": "No simulations ran"}

        best_run = ranked_runs[0]
        
        print(f"Mejor simulación encontrada ({strategy_name}): Score {best_run['score']} - ID {best_run['id']}")
        
        return best_run["replay_data"]

    def run_single_simulation_random(self):
        """
        Ejecuta múltiples simulaciones con estrategia aleatoria y retorna la mejor.
        Endpoint POST que permite obtener una simulación optimizada para visualización en Unity.
        El número de iteraciones (1000) puede ajustarse según el tiempo de respuesta deseado.
        
        Retorna:
            JSON con los datos de reproducción de la mejor simulación encontrada.
        """
        result_json = self._run_best_simulation(strategy_name="random", iterations=1000)
        return jsonify(result_json)
    
    def run_single_simulation_intelligent(self):
        """
        Ejecuta múltiples simulaciones con estrategia inteligente y retorna la mejor.
        Endpoint POST que garantiza obtener el mejor comportamiento posible considerando
        las variaciones aleatorias en las posiciones iniciales de los elementos.
        
        Retorna:
            JSON con los datos de reproducción de la mejor simulación encontrada.
        """
        result_json = self._run_best_simulation(strategy_name="intelligent")
        print(result_json)
        return jsonify(result_json)

    def run_batch_experiment(self):
        """
        Ejecuta un experimento con múltiples simulaciones en paralelo para análisis estadístico.
        Endpoint POST que permite especificar el número de iteraciones y la estrategia a utilizar.
        Los parámetros se reciben en el body de la petición en formato JSON.
        
        Parámetros esperados en request.json:
            iterations (int): Número de simulaciones a ejecutar (valor por defecto: 10)
            strategy (str): Estrategia a utilizar (valor por defecto: 'intelligent')
        
        Retorna:
            JSON con resultados estadísticos del experimento incluyendo todas las simulaciones ordenadas.
        """
        cfg = self.simulation_config
        data = request.json or {}
        iterations = data.get("iterations", 10)
        strategy = data.get("strategy", "intelligent")

        manager = SimulationManager()
        results = manager.run_batch_experiment(
            cfg["grid_width"], cfg["grid_height"], 
            cfg["agents"], cfg["max_energy"],
            iterations=iterations,
            strategy_name=strategy
        )
        return jsonify(results)
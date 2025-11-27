# TC2008B Modelación de Sistemas Multiagentes con gráficas computacionales
# Python server to interact with Unity via POST
# Sergio Ruiz-Loza, Ph.D. March 2021

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import sys
from Simulation.Simulation import Simulation

GRID_WIDTH = 8
GRID_HEIGHT = 6
AGENTS = 5
MAX_ENERGY = 100

class Server(BaseHTTPRequestHandler):
    
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
    def do_GET(self):
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    # def do_POST(self):
    #     position = {
    #         "x" : 0,
    #         "y" : 0,
    #         "z" : 10
    #     }
    #     self._set_response()
    #     self.wfile.write(str(position).encode('utf-8'))

    def do_POST(self):
        # 1. Correr la simulación
        simulation = Simulation(GRID_WIDTH, GRID_HEIGHT, AGENTS, MAX_ENERGY)
        simulation.runSimulation()
        
        # 2. Obtener el diccionario de posiciones { id: [[y,x], [y,x]...] }
        # Nota: Pandas no es estrictamente necesario aquí si ya tienes el diccionario en simulation.model.agents_positions
        # Pero si usaste simulation.model.agents_positions = df, accede al diccionario original o itera el df.
        
        # Vamos a reconstruir la estructura para Unity
        # Asumiendo que simulation.model.agents_positions es un DataFrame o Dict:
        
        results = []
        
        # Si agents_positions es un DataFrame, iteramos por columnas (Agentes)
        if hasattr(simulation.model.agents_positions, 'columns'):
            for agent_id in simulation.model.agents_positions.columns:
                path_list = []
                # Iteramos las filas (Pasos) para este agente
                for step_pos in simulation.model.agents_positions[agent_id]:
                    # step_pos es [y, x] (renglon, columna)
                    # En Unity: X es columnas, Z es renglones (generalmente)
                    
                    # CUIDADO: Verifica si step_pos es numpy array o lista
                    x_grid = float(step_pos[0])
                    y_grid = float(step_pos[1])
                    # print(step_pos)
                    # print(x_grid, y_grid)
                    
                    # Creamos objeto posición para Unity (x, y, z)
                    # Asumimos Y=0 para el suelo
                    pos_obj = {"x": x_grid, "y": 0.5, "z": y_grid}
                    path_list.append(pos_obj)
                
                results.append({"id": int(agent_id), "path": path_list})
        
        # 3. Empaquetar en un objeto raíz
        final_data = {"results": results}
        
        self._set_response()
        self.wfile.write(json.dumps(final_data).encode('utf-8'))
        simulation.show()


def run(server_class=HTTPServer, handler_class=Server, port=8585):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info("Starting httpd...\n") # HTTPD is HTTP Daemon!
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:   # CTRL+C stops the server
        pass
    httpd.server_close()
    logging.info("Stopping httpd...\n")

if __name__ == '__main__':
    from sys import argv
    
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()




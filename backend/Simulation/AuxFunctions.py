import os
import heapq
import random


def readMap():
    """
    Lee el archivo de texto 'InitialState.txt', parsea la configuración del entorno y estructura los datos del mapa.
    
    Parámetros:
        Ninguno.
    Retorna:
        dict: Diccionario 'mapData' que contiene listas de coordenadas para paredes, POIs, fuego, puertas y entradas.
    """
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "..", "Data", "InitialState.txt")
    file_path = os.path.abspath(file_path)

    if not os.path.exists(file_path):
        return None

    with open(file_path, mode="r") as f:
        text = list(map(lambda x: x.strip(), f.readlines()))
        raw_walls = list(map(lambda x: x.split(" "), text[0:6]))
        walls = raw_walls 

        def parse_coords(line_list, type_data):
            res = []
            for item in line_list:
                vals = item.split(" ")
                row_game = int(vals[0])
                col_game = int(vals[1])
                y = row_game - 1
                x = col_game - 1
                if type_data == 'poi':
                    res.append([y, x, vals[2]])
                elif type_data == 'fire' or type_data == 'entry':
                    res.append([y, x])
                elif type_data == 'door':
                    row2_game = int(vals[2])
                    col2_game = int(vals[3])
                    y2 = row2_game - 1
                    x2 = col2_game - 1
                    res.append([(y, x), (y2, x2), 'Closed'])
            return res
        pois = parse_coords(text[6:9], 'poi')
        fires = parse_coords(text[9:19], 'fire')
        doors = parse_coords(text[19:27], 'door')
        entryPoints = parse_coords(text[27::], 'entry')
    mapData = {
        'walls': walls,
        'pois': pois,
        'fires': fires,
        'doors': doors,
        'entryPoints': entryPoints
    }
    return mapData


def dijkstra_search(agent, targets, avoid_fire=False):
    """
    Determina el siguiente paso óptimo para alcanzar el objetivo más cercano calculando el camino de menor costo.
    Implementa el algoritmo de Dijkstra utilizando una cola de prioridad (heapq) para explorar el grafo de la cuadrícula, considerando costos variables por terreno, fuego, humo, ruptura de paredes y apertura de puertas.
    
    Parámetros:
        agent (Agent): La instancia del agente que realiza la búsqueda (necesario para verificar habilidades y posición).
        targets (list): Lista de coordenadas objetivo (tuplas) a las que el agente desea llegar.
        avoid_fire (bool): Bandera para asignar un costo prohibitivo a las celdas con fuego.
    Retorna:
        tuple | None: Coordenadas (x, y) del primer paso del camino óptimo encontrado, o None si no hay camino.
    """
    start = agent.pos
    
    queue = [(0, start, None)]
    visited = {}
    can_chop = agent.decision_chop_wall()
    while queue:
        cost, current, first_step = heapq.heappop(queue)
        if current in visited and visited[current] <= cost:
            continue
        visited[current] = cost
        if current in targets:
            return first_step if first_step else current
        cx, cy = current
        neighbors = agent.model.grid.get_neighborhood(current, moore=False, include_center=False)
        for next_pos in neighbors:
            nx, ny = next_pos
            step_cost = 2 if agent.carrying_victim else 1
            action_cost = 0
            wall_dir = -1
            if ny > cy: wall_dir = 0
            elif nx > cx: wall_dir = 1
            elif ny < cy: wall_dir = 2
            elif nx < cx: wall_dir = 3
            
            # PAREDES
            if agent.model.has_wall(cx, cy, wall_dir):
                if can_chop:
                    action_cost += 2
                else:
                    action_cost += 9999
            
            # PUERTAS
            door_idx = agent.model.get_door_index(current, next_pos)
            if door_idx != -1:
                if agent.model.doors[door_idx][2] == 'Closed':
                    action_cost += 1 

            # FUEGO / HUMO
            cell_status = agent.model.get_cell_status(next_pos)
            if cell_status == 'Fire':
                if avoid_fire:
                    action_cost += 100 # Evita el fuego a toda costa
                else:
                    action_cost += 1 # Apaga y pasa
            elif cell_status == 'Smoke':
                action_cost += 1

            total_step_cost = cost + step_cost + action_cost
            
            if total_step_cost < 1000: # Solo añadimos si es un camino viable (menor a muro infinito)
                if next_pos not in visited or total_step_cost < visited[next_pos]:
                    new_first_step = first_step if first_step else next_pos
                    heapq.heappush(queue, (total_step_cost, next_pos, new_first_step))
    return None


def get_closest_entry_to_pois(entry_points, pois):
    """
    Calcula qué punto de entrada es el más cercano a cualquier punto de interés (POI) activo.
    Implementa el algoritmo de Distancia Manhattan para calcular la cercanía entre coordenadas.
    
    Parámetros:
        entry_points (list): Lista de coordenadas [y, x] de las entradas disponibles.
        pois (list): Lista de POIs activos con formato [y, x, type, ...].
    Retorna:
        tuple: Coordenadas (x, y) de la entrada más cercana. Si no hay datos, retorna una aleatoria o (0,0).
    """
    if not pois or not entry_points:
        if entry_points:
            rng = random.choice(entry_points)
            return (rng[1], rng[0])
        return (0, 0)
    best_entry = None
    min_dist = float('inf')
    for ep in entry_points:
        ep_y, ep_x = ep[0], ep[1]
        for p in pois:
            py, px = p[0], p[1]
            # Distancia Manhattan
            dist = abs(ep_x - px) + abs(ep_y - py)
            if dist < min_dist:
                min_dist = dist
                best_entry = (ep_x, ep_y)
    return best_entry

def formatMap():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "..", "Data", "InitialState.txt")
    file_path = os.path.abspath(file_path)

    if not os.path.exists(file_path):
        return None

    with open(file_path, mode="r") as f:
        # Leer todas las filas y borrar saltos de línea
        text = [line.strip() for line in f.readlines()]

        # Extraer solo las 6 filas de walls
        raw_walls = [row.split(" ") for row in text[:6]]

        # Unir bloques de 4 chars en un solo string por fila
        walls = ["".join(blocks) for blocks in raw_walls]

        def parse_coords(line_list, type_data):
            res = []
            for item in line_list:
                vals = item.split()

                # Coordenadas base
                row = int(vals[0])
                col = int(vals[1])

                # Parseo según el tipo de dato
                if type_data == "poi":
                    letter = vals[2]   # f o v
                    type_val = 0 if letter == "f" else 1
                    res.append([row, col, type_val])

                elif type_data in ("fire", "entry"):
                    res.append([row, col])

                elif type_data == "door":
                    row2 = int(vals[2])
                    col2 = int(vals[3])
                    res.append([[row, col], [row2, col2], "Closed"])

            return res
        pois = parse_coords(text[6:9], 'poi')
        fires = parse_coords(text[9:19], 'fire')
        doors = parse_coords(text[19:27], 'door')
        entryPoints = parse_coords(text[27::], 'entry')

        mapData = {
            "pois": [
                {"y": p[0], "x": p[1], "type": p[2], "revealed": False}
                for p in pois
            ],
            "walls": walls,
            "fires": fires,
            "doors": [
                {"p1": d[0], "p2": d[1], "status": d[2]}
                for d in doors
            ],
            "entryPoints": [{"values": (ep[0], ep[1])} for ep in entryPoints]
        }
    return mapData


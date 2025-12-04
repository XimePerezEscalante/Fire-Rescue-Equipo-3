import os
import numpy as np
import heapq

def get_grid(model):
    return np.zeros((model.grid.height, model.grid.width))

def readMap():
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
    Encuentra el siguiente paso hacia el objetivo más cercano.
    Considera la habilidad del agente para romper paredes.
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

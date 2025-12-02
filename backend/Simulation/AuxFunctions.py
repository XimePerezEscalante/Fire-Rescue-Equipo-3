# Simulation/AuxFunctions.py
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
        
        HEIGHT = 6
        raw_walls = list(map(lambda x: x.split(" "), text[0:6]))
        walls = raw_walls[::-1] 

        def parse_coords(line_list, type_data):
            res = []
            for item in line_list:
                vals = item.split(" ")
                
                r_txt = int(vals[0])
                c_txt = int(vals[1])
                
                x = c_txt - 1
                y = HEIGHT - r_txt
                
                if type_data == 'poi':
                    res.append([y, x, vals[2]])
                elif type_data == 'fire' or type_data == 'entry':
                    res.append([y, x])
                elif type_data == 'door':
                    r2, c2 = int(vals[2]), int(vals[3])
                    y2, x2 = HEIGHT - r2, c2 - 1
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
    Retorna: (next_x, next_y) o None si no hay ruta.
    """
    start = agent.pos
    width = agent.model.grid.width
    height = agent.model.grid.height
    
    # Cola de prioridad: (costo_acumulado, (x, y), primer_paso)
    queue = [(0, start, None)]
    visited = set()
    
    while queue:
        cost, current, first_step = heapq.heappop(queue)
        
        if current in visited:
            continue
        visited.add(current)
        
        if current in targets:
            return first_step if first_step else current

        cx, cy = current
        
        # Obtener vecinos 
        neighbors = agent.model.grid.get_neighborhood(current, moore=False, include_center=False)
        
        for next_pos in neighbors:
            nx, ny = next_pos
            if next_pos in visited:
                continue

            # Calcular dirección para verificar paredes
            wall_dir = -1
            if ny > cy: wall_dir = 0
            elif nx > cx: wall_dir = 1
            elif ny < cy: wall_dir = 2
            elif nx < cx: wall_dir = 3
            
            move_cost = 1
            
            # --- VERIFICACIÓN DE OBSTÁCULOS ---
            
            # Paredes
            if agent.model.has_wall(cx, cy, wall_dir):
                move_cost += 2 
            
            # Puertas
            door_idx = agent.model.get_door_index(current, next_pos)
            if door_idx != -1:
                door_status = agent.model.doors[door_idx][2]
                if door_status == 'Closed':
                    move_cost += 1
            
            # Fuego
            cell_status = agent.model.get_cell_status(next_pos)
            if cell_status in ['Fire', 'Smoke']:
                if avoid_fire:
                    move_cost += 10
                else:
                    move_cost += 1

            new_cost = cost + move_cost
            new_first_step = first_step if first_step else next_pos
            heapq.heappush(queue, (new_cost, next_pos, new_first_step))
            
    return None
import os
import numpy as np

def get_grid(model):
    # Invertimos ancho y alto para que coincida con la matriz de numpy (filas, columnas)
    grid = np.zeros((model.grid.height, model.grid.width))
    
    # 1. Pintar Fuego (Rojo = 2) y POIs (Verde = 3)
    # Validamos límites para evitar errores si el txt tiene coordenadas malas
    def is_valid(y, x): 
        return 0 <= y < model.grid.height and 0 <= x < model.grid.width

    if hasattr(model, 'fires'):
        for f in model.fires:
            # f ya viene como [y, x] corregido (enteros)
            if is_valid(f[0], f[1]):
                grid[f[0]][f[1]] = 2
            
    if hasattr(model, 'pois'):
        for p in model.pois:
            # p es [y, x, tipo]
            py, px = p[0], p[1]
            if is_valid(py, px):
                grid[py][px] = 3

    # 2. Pintar Base (Azul = 1)
    # La base definimos que está en (0,0) según tu ExplorerModel
    grid[0][0] = 1 

    # 3. Pintar Agentes (Negro = 4)
    for content, (x, y) in model.grid.coord_iter():
        if content is not None:
             grid[y][x] = 4 

    return grid

def readMap():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "..", "Data", "InitialState.txt")
    file_path = os.path.abspath(file_path) 

    with open(file_path, mode="r") as f:
        text = list(map(lambda x: x.strip(), f.readlines()))
        
        # Paredes: se leen igual
        walls = list(map(lambda x: x.split(" "), text[0:6]))
        
        # FUNCION AUXILIAR PARA CORREGIR INDICES (Resta 1 a las coordenadas)
        # El txt usa base-1, Python usa base-0
        def parse_coords(line_list, is_poi=False):
            res = []
            for item in line_list:
                vals = item.split(" ")
                # Convertimos a int y restamos 1 a las coordenadas X y Y
                # Formato POI: [fila, col, tipo]
                if is_poi:
                    res.append([int(vals[0])-1, int(vals[1])-1, vals[2]])
                # Formato Fuego/Entrada: [fila, col]
                elif len(vals) == 2:
                    res.append([int(vals[0])-1, int(vals[1])-1])
                # Formato Puerta: [f1, c1, f2, c2]
                elif len(vals) == 4:
                    res.append([int(vals[0])-1, int(vals[1])-1, int(vals[2])-1, int(vals[3])-1])
            return res

        pois = parse_coords(text[6:9], is_poi=True)
        fires = parse_coords(text[9:19])
        doors = parse_coords(text[19:27])
        entryPoints = parse_coords(text[27::])

    mapData = {
        'walls' : walls,
        'pois' : pois,
        'fires' : fires,
        'doors' : doors,
        'entryPoints' : entryPoints
    }
    return mapData
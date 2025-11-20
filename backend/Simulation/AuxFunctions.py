import numpy as np


def get_grid(model):
    grid = np.zeros((model.grid.width, model.grid.height))
    for content, (x, y) in model.grid.coord_iter():
        # 0 = vacío (blanco)
        # 1 = comida (rojo)
        # 2 = base (azul)
        # 3 = agente (negro)
        if model.cells[x][y] == 1:
            grid[x][y] = 1  # Comida
        elif (x, y) == model.center:
            grid[x][y] = 2  # Base
        
        if content is not None:
            grid[x][y] = 3  # Agente
    return grid



def readMap():
    text = None
    walls = None # [arriba, izquierda, abajo, derecha]
    pois = None # [fila, columna, victima/falsa alarma]
    fires = None # [fila, columna]
    doors = None # [fila01, columna01, fila02, columna02] -> celdas que unen una puerta conectada
    entryPoints = None # [fila, columna]


    with open("InitialState.txt", mode="r") as f:
        text = list(map(lambda x: x.strip(), f.readlines()))
        walls = list(map(lambda x: x.split(" "), text[0:6]))
        pois = list(map(lambda x: x.split(" "), text[6:9]))
        fires = list(map(lambda x: x.split(" "), text[9:19]))
        doors = list(map(lambda x: x.split(" "), text[19:27]))
        entryPoints = list(map(lambda x: x.split(" "), text[27::]))

    mapData = {
        'walls' : walls,
        'pois' : pois,
        'fires' : fires,
        'doors' : doors,
        'entryPoints' : entryPoints
    }
    return mapData


if __name__ == '__main__':
    '''Para probar funciones'''
    mapData = readMap()
    for key in mapData.keys():
        print(f'{key} :')
        print(mapData[key])
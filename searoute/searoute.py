import json
from turfpy import measurement
import osmnx as ox
import networkx as nx
from geojson import LineString, FeatureCollection, Feature
from os import path

#pathGeojson = 'C:\dev\dev-py-packages\searoute-py-package\searoute\data\marnet_densified.json'

here = path.abspath(path.dirname(__file__))
path2Json = 'data/marnet_densified_v2_improved.geojson'
#path2Json = 'data/maritime-trade-routes.geojson'
pathGeojson =  path.join(here, path2Json) 

def createFeatureCollection(path):
    # Opening JSON file
    f = open(path)
    # returns JSON object as 
    # a dictionary
    data = json.load(f)
    # Iterating through the json
    # list
    f.close()
    fc = FeatureCollection(data)
    
    return fc

'''
Online Python Compiler.
Code, Compile, Run and Debug python program online.
Write your code in this editor and press "Run" button to execute it.

'''
def get_unique_number(lon, lat):
    try:
        lat_double = None
        lon_double = None
        if isinstance(lat, str):
            lat_double = float(lat)
        else:
            lat_double = lat
        if isinstance(lon, str):
            lon_double = float(lon)
        else:
            lon_double = lon

        lat_int = int((lat_double * 1e7))
        lon_int = int((lon_double * 1e7))
        val = abs((lat_int << 16 & 0xffff0000) | (lon_int & 0x0000ffff))
        val = val % 2147483647
        return val
    except Exception as e:
        print("marking OD_LOC_ID as -1 getting exception inside get_unique_number function")
        print("Exception while generating od loc id")
        return None
    
def createGraph():
    fc = createFeatureCollection(pathGeojson)
    
    G = nx.MultiDiGraph()

    try:
        G.graph['crs'] = fc.crs['properties']['name']
    except:
         G.graph['crs'] = 'EPSG:3857'
         
    for i in fc.features:
        coords = i['geometry']['coordinates']
        coord_l = len(coords)

        properties = i['properties']

        k = 0
        for l in coords:
            c_X = l[0]
            c_Y = l[1]
            c_node = get_unique_number(c_X, c_Y)
            G.add_node(c_node, x=c_X, y=c_Y)



            if(k<coord_l-1):
                n_coord = coords[k+1]
                n_X = n_coord[0]
                n_Y = n_coord[1]
                nx_node = get_unique_number(n_X, n_Y)


                ll = LineString([(c_X, c_Y), (n_X, n_Y)])
                lenght = measurement.length(ll)
                G.add_edge(c_node, nx_node, weight=lenght, **properties)
                G.add_edge(nx_node, c_node, weight=lenght, **properties)

            k= k+1
    
    return G

G = createGraph()

#possible passages: babalmandab, bosporus, gibraltar, suez, panama, ormuz, northwest
RESTRICTIONS = ['northwest']

def filter_edge(n1, n2, n3):
    val = G[n1][n2][n3].get('passage')

    if (val is None) or (val not in RESTRICTIONS):
        return True
    return False

def searoute(origin, destination, units='km', speed_knot=24, append_orig_dest = False, restrictions = RESTRICTIONS):
    """
    searoute Returnes the shortest sea route between two points on Earth.

    :param origin: a point as array lon, lat format ex. [0.3515625, 50.064191736659104]
    :param destination: a point as array lon, lat format ex. [117.42187500000001, 39.36827914916014]
    :param units: units default to 'km' = kilometers, can be 'm' = meters 'mi = miles 'ft' = feets 'in' = inches 'deg' = degrees 'cen' = centimeters 'rad' = radians 'naut' = nauticals 'yd' = yards
    :param speed_knot: speed of the boat, default 24 knots 
    :param append_orig_dest: add origin and dest geopoints in the LineString of the route, default is False
    :param restrictions: an list of restrictions of paths to awoid, use as per your specific need; default restricted ['northwest']; possible passages: babalmandab, bosporus, gibraltar, suez, panama, ormuz, northwest
    :return: a Feature (geojson) of a LineSring of sea route with parameters : unit and legth
    """ 


    global RESTRICTIONS
    RESTRICTIONS = restrictions

    H = nx.subgraph_view(G, filter_edge=filter_edge)
    
    # In the graph, get the nodes closest to the points
    origin_node = ox.distance.nearest_nodes(H, origin[0], origin[1])
    destination_node = ox.distance.nearest_nodes(H, destination[0], destination[1])

    # Get the shortest route by distance
    shortest_route_by_distance = ox.shortest_path(H, origin_node, destination_node, weight='weight')
    ls = []
    previousX = None
    for i in shortest_route_by_distance:
        node = H.nodes[i]
        nowX = node['x']
        
        if previousX:
            if previousX-nowX<-180:
                nowX = -180-(180-nowX)
            elif previousX-nowX>180:
                nowX = nowX+360
        ls.append((nowX, node['y']))
        previousX = nowX

    if append_orig_dest:

        if len(ls) == 1:
            #to avoid strage connections remove, eventually non-ocean connections with one coord, remove it to add origin and dest 
            ls = []
        # add origin at fist position of the linestring
        ls.insert(0, origin )
        # add destination at the last position of the linestring
        nowX = destination[0]
        if previousX:
            if previousX-nowX<-180:
                nowX = -180-(180-nowX)
            elif previousX-nowX>180:
                nowX = nowX+360
        ls.append((nowX, destination[1]))

        
    lineString = LineString(ls)
        
    if (units == 'nm'):
        length =   measurement.length(lineString, units ='mi') * 1.15078
    else:
        length =  measurement.length(lineString, units = units)

    duration = 0
    if (speed_knot>0):
        speed_knot = speed_knot*speed_coef(units)
        duration = length/speed_knot

    return Feature(geometry=lineString, properties = {'length': length, 'units' : units, 'duration_hours' : duration}) 


def speed_coef(unit):
    if unit == 'km':
        return 1.852
    elif unit == 'm':
        return 1852
    elif unit == 'mi':
        return 1.15078
    elif unit == 'ft':
        return 6076.12
    elif unit == 'in':
        return 72913,4
    elif unit == 'deg':
        return 1.852
    elif unit == 'cen':
        return 185200
    elif unit == 'rad':
        return 1.852
    elif unit == 'yd':
        return 2025.37
    return 1

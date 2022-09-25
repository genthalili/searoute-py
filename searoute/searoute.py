from turfpy import measurement
from geojson import LineString, FeatureCollection, Feature, Point

import networkx as nx

import geopandas as gpd
import momepy
from os import path

import warnings
warnings.filterwarnings("ignore")

'''
path of the geojson network - martine network 
Not for routing purposes! This library was developed to generate realistic-looking searoutes for visualizations of maritime routes, not for mariners to route their ships.
'''

here = path.abspath(path.dirname(__file__))
path2Json = 'data/marnet_densified.json'

#convert geojson to geopandas
lines = gpd.GeoDataFrame.from_file( path.join(here, path2Json) )

#convert geopandas to networkx with momepy
G = momepy.gdf_to_nx(lines)

#isolate all nodes/points of the grpah/network into FeatureCollection
fs = []
for node in G.nodes:
    f = Feature(geometry=Point([node[0], node[1]], precision=20))
    fs.append(f)
fc = FeatureCollection(fs)


def searoute(origin, destination, units='km'):
    """
    searoute Returnes the shortest sea route between two points on Earth.

    :param origin: a point as array lon, lat format ex. [0.3515625, 50.064191736659104]
    :param destination: a point as array lon, lat format ex. [117.42187500000001, 39.36827914916014]
    :param units: units default to 'km' = kilometers, can be 'm' = meters 'mi = miles 'ft' = feets 'in' = inches 'deg' = degrees 'cen' = centimeters 'rad' = radians 'naut' = nauticals 'yd' = yards
    :return: a Feature (geojson) of a LineSring of sea route with parameters : unit and legth
    """ 
    
    snappedOrigin = snapToNetwork(origin)
    snappedDestination = snapToNetwork(destination)

    route = nx.dijkstra_path(G, source=snappedOrigin, target=snappedDestination, weight='mm_len')

    if ((route == None) or len(route)<2):
        print("No route found")
        return None
    
   
    
    lineString = LineString(route,precision= 20)
    if (units == 'nm'):
        length =   measurement.length(lineString, units ='mi') * 1.15078
    else:
        length =  measurement.length(lineString, units = units)
        
    f_result = Feature(geometry=lineString, properties = {'length': length, 'units' : units}) 
    return f_result


def snapToNetwork(point):
    """
    snapToNetwork Returnes the closest point in the network.

    :param point: any point of array lon, lat format ex. [0.3515625, 50.064191736659104]
    :return: a point in the netowork of array lon, lat format ex. [0.3515625, 50.064191736659104]
    """
    
    t = Feature(geometry=Point(point, precision=20))
    #search the neast_point
    near_by = tuple(measurement.nearest_point(t , FeatureCollection(fs)).geometry.coordinates)
    return near_by
from math import atan2, cos,  pow, radians, sin, sqrt, tan
import geojson
import inspect


def get_unique_number(lon, lat):
    """Get a unique hash

    Parameters
    ----------
    lon : longitude
    lat : latitude

    Returns
    -------
    A unique str of hash
    
    """
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
        return 72913, 4
    elif unit == 'deg':
        return 1.852
    elif unit == 'cen':
        return 185200
    elif unit == 'rad':
        return 1.852
    elif unit == 'yd':
        return 2025.37
    return 1


avg_earth_radius_km = 6371008.8
conversions = {
    "km": 0.001,
    "m": 1.0,
    "mi": 0.000621371192,
    "ft": 3.28084,
    "in": 39.370,
    "deg": 1 / 111325,
    "cen": 100,
    "rad": 1 / avg_earth_radius_km,
    "naut": 0.000539956803,
    "yd": 0.914411119,
    "nm": 0.00071506154
}


def distance(coordinates1, coordinates2, units: str = "km"):
    """
    Distance calculation

    Parameters
    ----------
    coordinates1 : tuple of lat,lon, from location
    coordinates2 : tuple of lat,lon, to location
    units : a unit, default is `km`


    Returns
    -------
    Distance in `units`


    """

    dlat = radians((coordinates2[1] - coordinates1[1]))
    dlon = radians((coordinates2[0] - coordinates1[0]))

    lat1 = radians(coordinates1[1])
    lat2 = radians(coordinates2[1])

    a = pow(sin(dlat / 2), 2) + pow(sin(dlon / 2), 2) * cos(lat1) * cos(lat2)
    b = 2 * atan2(sqrt(a), sqrt(1 - a))
    return b * avg_earth_radius_km * conversions[units]


def distance_length(line: list, units: str = "km"):
    """
    Length of a line of coordinates 

    Parameters
    ---------
    line : a list of tuple [(lon, lat), (lon, lat), ...]
    units: the unit, default is `km`

    Returns
    -------
    Distance in `units`
    """
    if line is None:
        return 0

    length = 0
    coords = line
    le = len(coords)-1
    for i, point in enumerate(coords):
        if i != le:
            length += distance(point, coords[i+1], units)

    return length


def get_duration(speed_knot, length, units):
    """Duration 


    Parameters
    ----------
    speed_knot : seed of the boat in knot
    length : length or distance in `units`
    units : the unit of the length/distance

    Returns
    -------
    The duration in hours `hr`

    """
    duration = 0

    if (speed_knot > 0):
        speed_knot = speed_knot*speed_coef(units)
        duration = length/speed_knot

    return duration


def find_lowest_key(data, *keys):
    min_dict_ids = tuple(
        min(data, key=lambda dict_id: data[dict_id].get(key, float('inf')))
        for key in keys
    )

    return min_dict_ids


def __default_filter(u, *something):
    """
    A default filter is a lazy filter and will return always True

    Parameters
    ----------
    u : a node, not used
    something : arguments of something, not used

    Returns
    --------
    Always `True`


    """
    return True


def nearest_node(G, *args, filter=None, fargs=()):
    """
    Nearest node in the graph

    Returns
    -------
    filter can be a True, callable function which should return a function
    when filter = True it means validated

    """
    dists = {}
    keys = set(range(len(args)))
    found = False
    ignoreEdgeCheck = False

    if filter is None:
        filter = __default_filter

    f_params = len(inspect.signature(filter).parameters)

    if not f_params in [2, 4]:
        raise Exception('filter should have 2 or 4 parameters')

    if f_params == 2:
        ignoreEdgeCheck = True

    for node, data in G.nodes(data=True):
        x = data.get('x', None)
        y = data.get('y', None)

        filtered = False
        if ignoreEdgeCheck:
            filtered = filter(node, fargs)

        for ix, arg in enumerate(args):
            arg = tuple(arg)
            aDist = distance((x, y), arg)
            if node not in dists:
                dists[node] = {}

            edge_data = {}
            if not ignoreEdgeCheck and G.has_edge(node, arg):
                edge_data = G.get_edge_data(node, arg)

            if filtered or (not ignoreEdgeCheck and filter(node, arg, edge_data, fargs)):
                dists[node][ix] = aDist
                found = True

    if not found:
        # return nothing if not found anything
        return None

    return find_lowest_key(dists, *keys)


def to_nodes_edges_list(G, file_name):
    """
    Converts a graph to nodes, edges list of dict, and exports to a file

    Parameters
    ----------
    G : a graph of Marnet or Ports
    file_name : the name of the file to be saved

    Returns
    -------
    Void
    
    """
    if not file_name:
        file_name = 'graph_data.py'

    with open(file_name, 'w') as convert_file:
        convert_file.write(f"node_list={str(list(G.nodes(data=True)))}\n\nedge_list={str(list(G.edges(data=True)))}")

def to_nodes_edges_set(G, file_name):
    if not file_name:
        file_name = 'graph_data.py'

    with open(file_name, 'w') as convert_file:
        convert_file.write(f"node_list={str(G._node)}\n\nedge_list={str(G._adj)}")

def from_nodes_edges_set(G, node_set, edge_set):
    """Returns a searoute Network (Ports or Marnet) from a set of nodes and edges.

    Parameters
    ----------
    G : a Ports or Marnet network (instance)
        Ports or Marnet object are searoute classes inheriting the NetworkX graph.


    node_set : dictorary of nodes, required.
        A set of nodes represnation with its attribites.
        A node should be a spacial location as a tuple of `lon`, `lat` (lon, lat)
        Must contain at least 2 attributes : `x` = lon, and `y` = lat

    edge_set : dictorary of edges, required.
       A set of edges represnation with its edge-data.

    Examples
    --------
    >>> my_nodes = {(1,2):{'x':1, 'y':2}, (2,2):{'x':2, 'y':2}}  # nodes of representing (1,2) of lon = 1, lat = 2
    >>> my_edges = {(1,2):{(2,2):{weight:10, other_attr:'some_value'}}} # (1,2) -> (2,2) with weight representing the distance or additional attributes
    >>> # recognized attributes are : `weight` (distance), ``passagepassage`` (name of the `passage` to be restricted by M.restrictions) 
    >>> M = sr.from_nodes_edges_set( sr.Marnet() ,my_nodes, my_edges)

    or

    >>> P = sr.from_nodes_edges_set( sr.Ports() ,my_nodes, None) # for Ports

    """


    if G is None:
        raise Exception('G should not be none or provide create_with')
    
    G._node = node_set or {}
    G._adj = edge_set or {}
    G.update_kdtree(node_set)

    return G

def from_nodes_edges_list(G, node_list, edge_list):
    #if type(G) in [Marnet, Ports] :
    G.add_nodes_from_list(node_list)
    G.add_edges_from_list(edge_list)

    return G

    #else:
    #    raise Exception(f"{type(G)} not supported")

def load_from_geojson(G, *geojson_file):
    for gf in geojson_file:
        with open(gf, 'r') as f:
            data = geojson.load(f)

        def handle_geometry(geometry, properties):
            if geometry.type == 'LineString':
                coords = geometry.coordinates
                for u, v in zip(coords[:-1], coords[1:]):
                    G.add_edge(tuple(u), tuple(v), **properties)
                    # the other side as well
                    G.add_edge(tuple(v), tuple(u), **properties)
            elif geometry.type == 'MultiLineString':
                for line_string in geometry.coordinates:
                    for u, v in zip(line_string[:-1], line_string[1:]):
                        G.add_edge(tuple(u), tuple(v), **properties)
                        # the other side as well
                        G.add_edge(tuple(v), tuple(u), **properties)
            elif geometry.type == 'Point':
                coords = tuple(geometry.coordinates)
                G.add_node(coords, **properties)
            elif geometry.type == 'MultiPoint':
                for point_coords in geometry.coordinates:
                    coords = tuple(point_coords)
                    G.add_node(coords, **properties)
            else:
                # Handle other geometries if needed (e.g., MultiPolygon, Polygon, etc.)
                pass

        # Extract CRS information from FeatureCollection
        if data.type == 'FeatureCollection':
            G.graph['crs'] = data.get('crs', {}).get(
                'properties', {}).get('name', None) or G.graph['crs']

            for feature in data.features:
                handle_geometry(feature.geometry, feature.properties)
        else:
            handle_geometry(data.geometry, data.properties)

    return G


def normalize_linestring(prev, now):
    """
    Normalize the coordinate for the lineString.
    The previus (`prev`) parameter will dictate the direction of the string

    Parameters
    ----------
    prev : a coord of (lon, lat)
    now : a coord to fix of format (lon, lat)

    Returns
    -------
    a cordinate normalized or fixt coordinate of format (lon, lat)

    """
    if not prev:
        return now
    
    now_x, now_y = now
    prev_x, prev_y = prev

    if not prev_x is None:
        px = prev_x-now_x
        if px < -180:
            now_x = now_x - 360
        elif px > 180:
            now_x = now_x + 360
    
    return (now_x, now_y)

def process_route(shortest_route_by_distance, M, return_passages=False):
    """
    Process the shortest route by distance, normalizing the coordinates and
    optionally extracting traversed passages.

    Args:
        shortest_route_by_distance (list): A list of nodes representing the shortest route.
        M (Graph): The graph object containing the edges and their attributes.
        return_passages (bool): A flag to determine whether to return traversed passages.

    Returns:
        tuple: A tuple containing:
            - ls (list): A list of normalized coordinate linestrings.
            - traversed_passages (list, optional): A list of passages traversed in the route if return_passages is True.
    """
    ls = []
    previous = None

    previous_traversed = None
    traversed_passages = []

    if return_passages:    
        for i in shortest_route_by_distance:
            now = i
            edge = M.get_edge_data(previous_traversed, now)
            if edge:
                traversed_passages.append(edge.get("passage", None))
                
            fixed_coords = normalize_linestring(previous, now)
            ls.append(fixed_coords)
            previous = fixed_coords
            previous_traversed = now

        return ls, traversed_passages
    else:
        for i in shortest_route_by_distance:
            now = i   
            fixed_coords = normalize_linestring(previous, now)
            ls.append(fixed_coords)
            previous = fixed_coords

        return ls, None



def validate_lon_lat(coord):
    """
    Validate a (lon, lat) coordinate.

    Parameters
    ----------
    coord (tuple or list): A tuple or list containing two elements, representing longitude and latitude.

    Raises
    ------
    ValueError: If the input format is incorrect or if the longitude and latitude values are invalid.

    Returns
    -------
    None: The function does not return anything. It either validates successfully or raises an exception.
    """

    # Check if the input is a tuple or list with two elements
    if not isinstance(coord, (tuple, list)) or len(coord) != 2:
        raise ValueError("Invalid input format. Must be a tuple or list with two elements as (lan,lon).")

    lon, lat = coord

    # Latitude should be between -90 and 90 degrees
    # Longitude can be any value
    if not (-90 <= lat <= 90) or not isinstance(lon, (int, float)):
        raise ValueError("Invalid longitude and/or latitude.")
    

def normalize_longitude(longitude:float):
    """
    Normalize a longitude value to the range of -180 to 180 degrees.

    Parameters:
    - longitude (float): The input longitude value.

    Returns:
    - float: The normalized longitude value within the range of -180 to 180 degrees.

    Examples:
    normalize_longitude(200)
    >>> -160.0

    normalize_longitude(-270)
    >>> 90.0
    """
    return (longitude % 360 + 540) % 360 - 180


def pnpoly(nvert: int, vertx: list, verty: list, testx :float, testy: float) ->bool:
    """
    Determines if a point is inside a polygon.
    document : https://wrfranklin.org/Research/Short_Notes/pnpoly.html
    Copyright (c) 1970-2003, Wm. Randolph Franklin

    Parameters:
    ==========
    - nvert (int): Number of vertices in the polygon. It's not necessary to repeat the first vertex at the end.
    - vertx (list or array of float): Array containing the x-coordinates of the polygon's vertices.
    - verty (list or array of float): Array containing the y-coordinates of the polygon's vertices.
    - testx (float): X-coordinate of the test point.
    - testy (float): Y-coordinate of the test point.

    Returns:
    =======
    bool: True if the test point is inside the polygon; False otherwise.
    """
    c = False
    for i in range(nvert):
        j = nvert - 1 if i == 0 else i - 1
        if ((verty[i] > testy) != (verty[j] > testy)) and \
                (testx < (vertx[j] - vertx[i]) * (testy - verty[i]) / (verty[j] - verty[i]) + vertx[i]):
            c = not c
    return c

from .classes import ports, marnet, passages 

from .utils import get_duration, distance_length, from_nodes_edges_set, process_route, validate_lon_lat, raise_warn_no_path
from geojson import Feature, LineString

from functools import lru_cache
#from copy import copy


@lru_cache(maxsize=None)
def setup_P(backend = None):
    from .data.ports_dict import edge_list as port_e, node_list as port_n
    return from_nodes_edges_set(ports.Ports(backend = backend), port_n, port_e)

@lru_cache(maxsize=None)
def setup_M(backend = None):
    from .data.marnet_dict import edge_list as marnet_e, node_list as marnet_n
    return from_nodes_edges_set(marnet.Marnet(backend = backend), marnet_n, marnet_e)



def get_graphs(M = None, P = None, backend = None):
    if M is None:
        M = setup_M(backend)#copy(setup_M())

    if P is None:
        P = setup_P(backend)#copy(setup_P())

    return M, P


def searoute(origin, destination, units='km', speed_knot=24, append_orig_dest=False, restrictions=[passages.Passage.northwest], include_ports=False, port_params={}, M:marnet.Marnet=None, P:ports.Ports=None, return_passages:bool = False, algorithm = None, backend="networkx"):
    """
    Calculates the shortest sea route between two points on Earth.

    Parameters
    ----------
    origin : a point as array lon, lat format ex. [0.35156, 50.06419]
    destination : a point as array lon, lat format ex. [117.42187, 39.36827]
    units : default is `km` = kilometers,
        can be `m` = meters `mi` = miles `ft` = foot 
        `in` = inches `deg` = degrees `cen` = centimeters 
        `rad` = radians `naut` = nautical `yd` = yards
    speed_knot : speed of the boat, default is `24` knots 
    append_orig_dest : add origin and dest geo-points in the LineString of the route, default is False
    restrictions : an list of restrictions of paths to avoid, use as per your specific need; default restricted ['northwest']; possible passages: babalmandab, bosporus, gibraltar, suez, panama, ormuz, northwest
    include_ports : boolean to include closest port close to origin or destinations
    port_params : object ; 
        - only_terminals: boolean, default False
        - country_pol: country iso code for port of load
        - country_pod: country iso code for port of discharge
        - country_restricted :  boolean or 'strict', default False ; if True it will consider `country_pod` as a parameter to match with `to_cty` in ports list
                                if set to 'strict' then if will force ALL queries to match
        - ports_in_areas : a FeatureCollection containing areas with preferred ports, created of AreaFeature, use AreaFeature.create([...]). The previous configurations will be ignored.
                            If there are many ports then the result will be a list of GeoJson Features, instead of an object of GeoJson Feature.
                            Preferred ports with share = 0 will be ignored.
    return_passages : boolean to return traversed passages (default is `False`)
    algorithm : str one of `dijkstra` or `astar`, default `dijkstra`
    backend : str one of `networkx` or `igraph`, default `networkx` chose between backend graph class

    Returns
    -------
    a Feature (geojson) of a LineString of sea route with parameters : `unit` and `length`, `duration_hours` or port details, others
    """

    #if M is None:
    #    M = copy(setup_M())
    #if P is None:
    #    P = copy(setup_P())
    M, P = get_graphs(M, P, backend)

    # Validate origin input
    validate_lon_lat(origin)
    # Validate destination input
    validate_lon_lat(destination)


    if P is None:
        raise Exception('Ports network must not be None')

    if M is None:
        raise Exception('Marnet network must not be None')

    o_origin = tuple(origin)
    o_destination = tuple(destination)

    # updating restrictions
    if restrictions is not None:
        M.restrictions = restrictions

    if include_ports:
        if not port_params:
            port_params = {}

        port_matrix = P.get_selected_port_matrix(origin, destination, port_params)
    else:
        port_matrix = [(None, None)]


    def _get_feature(o_origin, o_destination, origin, destination, port_origin, port_dest, include_ports, append_orig_dest, algorithm):

        # Get shortest route from the Marnet network 
        # if origin or destination is not present in M, searches from the closest one
        # if path is restricted then returns the next shortest possible one
        # if no paths are found due to restricted passages, length will be inf 
        length_km, shortest_route_by_distance = M.shortest_path(origin, destination, algorithm)

        # route path will be set to empty if length is inf due to restrictive passages
        if shortest_route_by_distance is None or length_km == float('inf'):
            # raise warning as no path found
            raise_warn_no_path(origin, destination, length_km, restrictions)
            shortest_route_by_distance = []
            
        if include_ports and shortest_route_by_distance:
            shortest_route_by_distance.insert(0, origin )
            shortest_route_by_distance.append(destination )

        if append_orig_dest:
            if (origin != o_origin):
                shortest_route_by_distance.insert(0, o_origin)
            if (destination != o_destination):
                shortest_route_by_distance.append(o_destination)

        # processes passages : checks and normalizes the coords
        ls, traversed_passages = process_route(shortest_route_by_distance, M, return_passages)

        # (re-)calculate length and duration
        # (optional) length can use the provided one by shortest_path which should be normalized
        total_length = distance_length(ls, units=units)
        duration = get_duration(speed_knot, total_length, units)


        # create Feature with LineSting and calculated parameters
        feature = Feature(geometry=LineString(ls), properties={
                        'length': total_length, 'units': units, 'duration_hours': duration})

        if include_ports and port_origin and port_dest:
            feature.properties['port_origin'] = port_origin
            feature.properties['port_dest'] = port_dest
        
        # add traversed passages if included in parameters
        if return_passages:
            feature.properties['traversed_passages'] = passages.Passage.filter_valid_passages(traversed_passages)

        return feature
    
    result = []
    for p_m in port_matrix:
        pFrom, pTo = p_m
        if pFrom:
            pid, share, pProp = pFrom
            origin = [pProp.get('x', None), pProp.get('y', None)]
            pProp['share'] = share
            pFrom = pProp

        if pTo:
            pid, share, pProp = pTo
            destination = [pProp.get('x', None), pProp.get('y', None)]
            pProp['share'] = share
            pTo = pProp

        res = _get_feature(o_origin, o_destination, origin, destination, pFrom, pTo, include_ports, append_orig_dest, algorithm)
        result.append(res)


    if len(result)==1:
        return result[0]
    else:
        return result
    


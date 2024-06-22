
from .classes import ports, marnet, passages
from .utils import get_duration, distance_length, from_nodes_edges_set, process_route, validate_lon_lat
from geojson import Feature, LineString

from functools import lru_cache
from copy import copy

@lru_cache(maxsize=None)
def setup_P():
    from .data.ports_dict import edge_list as port_e, node_list as port_n
    return from_nodes_edges_set(ports.Ports(), port_n, port_e)

@lru_cache(maxsize=None)
def setup_M():
    from .data.marnet_dict import edge_list as marnet_e, node_list as marnet_n
    return from_nodes_edges_set(marnet.Marnet(), marnet_n, marnet_e)



def searoute(origin, destination, units='km', speed_knot=24, append_orig_dest=False, restrictions=[passages.Passage.northwest], include_ports=False, port_params={}, M:marnet.Marnet=None, P:ports.Ports=None, return_passages:bool = False):
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

    Returns
    -------
    a Feature (geojson) of a LineString of sea route with parameters : `unit` and `length`, `duration_hours` or port details, others
    """

    if M is None:
        M = copy(setup_M())
    if P is None:
        P = copy(setup_P())
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

    # H = nx.subgraph_view(G, filter_edge=filter_edge)

    if include_ports:
        if not port_params:
            port_params = {}

        only_terminals = port_params.get('only_terminals', False)
        country_pol = port_params.get('country_pol', None)
        country_pod = port_params.get('country_pod', None)

        country_restricted = port_params.get('country_restricted', False)
        country_restricted_key =  'to_cty'
        country_restricted_strict = False

        if country_restricted == 'strict':
            country_restricted_strict = True
            country_restricted = True
        
        to_cty = country_pod if country_restricted else None
       
        # set origin as closest port
        closestPortOrigin = P.query(
            terminals=only_terminals, cty=country_pol, to_cty=to_cty, strict=country_restricted_strict).kdtree.query(origin)
        if closestPortOrigin:
            origin = closestPortOrigin
            port_origin = P.nodes[origin].copy()
            if country_restricted_key in port_origin:
                port_origin.pop(country_restricted_key)

        # set destination as closest port
        closestPortDest = P.query(
            terminals=only_terminals, cty=country_pod).kdtree.query(destination)
        if closestPortDest:
            destination = closestPortDest
            port_dest = P.nodes[destination].copy()
            if country_restricted_key in port_dest:
                port_dest.pop(country_restricted_key)
    
    # Get shortest route from the Marnet network 
    # if origin or destination is not present in M, searches from the closest one
    shortest_route_by_distance = M.shortest_path(o_origin, o_destination)

    if shortest_route_by_distance is None:
        shortest_route_by_distance = []
        
    if include_ports and shortest_route_by_distance:
        shortest_route_by_distance.insert(0, origin )
        shortest_route_by_distance.append(destination )

    if append_orig_dest:
        if (origin != o_origin):
            shortest_route_by_distance.insert(0, o_origin)
        if (destination != o_destination):
            shortest_route_by_distance.append(o_destination)

    '''
    ls = []
    previous = None
    traversed_passages = []

    for i in shortest_route_by_distance:
        now = i

        edge = M.get_edge_data(previous, now)
        if edge:
            traversed_passages.append(edge.get("passage", None))
            
        fixed_coords = normalize_linestring(previous, now)
        ls.append(fixed_coords)
        previous = fixed_coords

    '''
    ls, traversed_passages = process_route(shortest_route_by_distance, M, return_passages)

    total_length = distance_length(ls, units=units)

    duration = get_duration(speed_knot, total_length, units)

    feature = Feature(geometry=LineString(ls), properties={
                      'length': total_length, 'units': units, 'duration_hours': duration})

    if include_ports and port_origin and port_dest:
        feature.properties['port_origin'] = port_origin
        feature.properties['port_dest'] = port_dest

    if return_passages:
        feature.properties['traversed_passages'] = passages.Passage.filter_valid_passages(traversed_passages)

    return feature

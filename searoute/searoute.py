
from .classes import ports, marnet, passages
from .utils import get_duration, distance_length, from_nodes_edges_set
from geojson import Feature, LineString

from .data.ports_dict import edge_list as port_e, node_list as port_n
from .data.marnet_dict import edge_list as marnet_e, node_list as marnet_n


P = from_nodes_edges_set(ports.Ports(), port_n, port_e)
M = from_nodes_edges_set(marnet.Marnet(), marnet_n, marnet_e)

del port_e, port_n, marnet_e, marnet_n


def searoute(origin, destination, units='km', speed_knot=24, append_orig_dest=False, restrictions=[passages.Passage.northwest], include_ports=False, port_params={}, M:marnet.Marnet=M, P:ports.Ports=P):
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
    port_params : object ; only_terminals: boolean, country_pol: country iso code for port of load, country_pod: country iso code for port of discharge
    
    Returns
    -------
    a Feature (geojson) of a LineString of sea route with parameters : `unit` and `length`, `duration_hours` or port details
    """

    if not origin or not all(origin):
        raise Exception('Origin/Destination must not be empty or None')

    if not destination or not all(destination):
        raise Exception('Origin/Destination must not be empty or None')

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

        # set origin as closest port
        closestPortOrigin = P.query(
            terminals=only_terminals, cty=country_pol).kdtree.query(origin)
        if closestPortOrigin:
            origin = closestPortOrigin
            port_origin = P.nodes[origin]

        # set destination as closest port
        closestPortDest = P.query(
            terminals=only_terminals, cty=country_pod).kdtree.query(destination)
        if closestPortDest:
            destination = closestPortDest
            port_dest = P.nodes[destination]
    
    # Get shortest route from the Marnet network 
    # if origin or destination is not presnet in M, searches from the closest one
    shortest_route_by_distance = M.shortest_path(o_origin, o_destination)

    ls = []
    previousX = None
    for i in shortest_route_by_distance:
        node = M.nodes[i]
        nowX = node['x']

        if previousX:
            if previousX-nowX < -180:
                nowX = -180-(180-nowX)
            elif previousX-nowX > 180:
                nowX = nowX+360
        ls.append((nowX, node['y']))
        previousX = nowX

    if append_orig_dest:

        if len(ls) == 1:
            # to avoid strange connections remove, eventually non-ocean connections with one coord, remove it to add origin and dest
            ls = []
        # add origin at fist position of the linestring
        ls.insert(0, origin)

        # add destination at the last position of the linestring
        nowX = destination[0]
        if previousX:
            if previousX-nowX < -180:
                nowX = -180-(180-nowX)
            elif previousX-nowX > 180:
                nowX = nowX+360
        ls.append((nowX, destination[1]))

        if (origin != o_origin):
            ls.insert(0, o_origin)
        if (destination != o_destination):
            ls.append(o_destination)

    total_length = distance_length(ls, units=units)

    duration = get_duration(speed_knot, total_length, units)

    feature = Feature(geometry=LineString(ls), properties={
                      'length': total_length, 'units': units, 'duration_hours': duration})

    if include_ports and port_origin and port_dest:
        feature.properties['port_origin'] = port_origin
        feature.properties['port_dest'] = port_dest

    return feature

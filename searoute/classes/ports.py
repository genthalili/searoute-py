from .core import Graph

from ..utils import load_from_geojson
from .kdtree import KDTree
from . import area_feature
from geojson import FeatureCollection
from itertools import product


class Ports(Graph):
    """
    Base class for Ports network is an undirected graph. 

    A Ports graph stores nodes and edges with optional data, or attributes.

    Nodes are identified by an id of tuple representing a spacial location
    with (lon, lat) and it's attributes if applied.
    They form ports located around the world.


    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        DEFAULT_CRF = 'EPSG:3857'
        self.graph['crs'] = DEFAULT_CRF  # CRS attribute for the graph
        self.kdtree = KDTree()

    def add_node(self, node, **attr):
        if not isinstance(node, tuple):
            raise TypeError(
                "Node must be a str representing coordinates of a port.")
        #x, y = node
        #attr['x'] = x
        #attr['y'] = y
        if not (attr['port'] and attr['cty']):
            raise TypeError(
                "Node port requires to have both port name (name), and country (cty) in properties to be correctly mapped")

        self.kdtree.add_point(node)
        super().add_node(node, **attr)


    #def __copy__(self):
    #    cls = self.__class__
    #    result = cls.__new__(cls)
    #    result.__dict__.update(self.__dict__)
    #    return result

    def subgraph(self, nodes):
        subg = super().subgraph(nodes)
        subg.kdtree = KDTree(nodes)

        return subg

    def query(self, terminals: bool = True, cty: str = None, to_cty: str = None, strict = False):
        """
        Query the Port graph

        Parameters
        ----------
                
        terminal: boolean, default True
            filters out only terminal marked ports
        cty : str, default None
            filters out ports in given country code (must be an ISO country code with 2 letters uppercase)
        to_cty: str, default None
            filters out ports that have to_country the port of discharge (country_pod)
            must be an ISO country code with 2 letters uppercase

        Returns
        -------
        A subgraph of Ports filtered
        """

        if not terminals and not cty and not to_cty:
            return self

        def cty_filter(data, cty):
            if not cty:
                return True
            else:
                return data.get('port')[:2] == cty
            
        def cty_to_filter(data, to_cty):
            if not to_cty:
                return True
            else:
                return to_cty in (data.get('to_cty') or [])

        terminal_filter = True if terminals else None

        if strict:
            strict_filter = [n for n, data in self.nodes(data=True) 
             if data.get('t') == terminal_filter and cty_filter(data, cty) and cty_to_filter(data, to_cty)]
            
            if len(strict_filter)<1:
                raise KeyError(f'There is no ports for your query terminals:{terminals}, from country:{cty}, to country:{to_cty}, strict:{strict}')
            
            return self.subgraph(strict_filter)

        # add filter terminals
        filtered_nodes = [(n, data) for n, data in self.nodes(data=True) if data.get('t') == terminal_filter]
        filtered_nodes_prev = []

        if len(filtered_nodes)>0:
            # add filter "from county"
            filtered_nodes_prev = filtered_nodes
            filtered_nodes = [(n, data) for n, data in filtered_nodes_prev if cty_filter(data, cty)]
        else:
            filtered_nodes = filtered_nodes_prev

        if len(filtered_nodes)>0:
            # add filter "to county"
            filtered_nodes_prev = filtered_nodes
            filtered_nodes = [(n, data) for n, data in filtered_nodes_prev if cty_to_filter(data, to_cty)]
        else:
            filtered_nodes = filtered_nodes_prev

        # finally select all if not found any yet..
        if len(filtered_nodes)==0:
            filtered_nodes = self.nodes(data=True)
            
        if len(filtered_nodes)>0:
            return self.subgraph([n for n,_ in filtered_nodes])
        else:
            raise KeyError(f'There is no ports for your query terminals:{terminals}, from country:{cty}, to country:{to_cty}, strict:{strict}')

       

    def filter_only_terminals(self, u, v, edge_data):
        return True if edge_data.get('t', 0) == 1 else False

    def load_geojson(self, path):
        return load_from_geojson(self, path)

    @staticmethod
    def from_geojson(path):
        return Ports().load_geojson(path)
    

    def add_edges_from_list(self, edge_list):
        if not edge_list:
            return
        
        for edge in edge_list:
            u,v,args = edge
            self.add_edge(u, v, **args)

    def add_nodes_from_list(self, node_list):
        if not node_list:
            return

        for node in node_list:
            n, args = node
            self.add_node(n, **args)

    def update_kdtree(self, nodes = None):
        if nodes:
            self.kdtree = KDTree(nodes)
        else:
            self.kdtree = KDTree(self._node)

    
    def get_selected_port_matrix(self, origin, destination, port_params = {}):
        
        
        port_in_areas_from = port_params.get('ports_in_areas_from', None)
        port_in_areas_to = port_params.get('ports_in_areas_to', None)
        port_in_areas = port_params.get('ports_in_areas', None)

        if not port_in_areas_from:
            port_in_areas_from = port_in_areas
            
        if not port_in_areas_to:
            port_in_areas_to = port_in_areas

        # collecting config request
        only_terminals = port_params.get('only_terminals', False)
        country_pol = port_params.get('country_pol', None)
        country_pod = port_params.get('country_pod', None)

        country_restricted = port_params.get('country_restricted', False)
        country_restricted_key =  'to_cty'
        country_restricted_strict = False

        # strict area
        conf_strict_area = port_params.get('strict_area', True)

        if country_restricted == 'strict':
            country_restricted_strict = True
            country_restricted = True

        to_cty = country_pod if country_restricted else None

        pref_ports_from = []
        pref_ports_to= []

        if port_in_areas_from:
            pref_ports_from = self.get_preferred_ports(*origin, port_in_areas_from, top=None, strict_area=conf_strict_area)
            for i in pref_ports_from:
                _, _, c = i
                if country_restricted_key in c:
                    c.pop(country_restricted_key)

        if len(pref_ports_from)==0:
            # set origin as closest port
            closestPortOrigin = self.query(
                terminals=only_terminals, cty=country_pol, to_cty=to_cty, strict=country_restricted_strict).kdtree.query(origin)
            if closestPortOrigin:
                port_origin = self.nodes[closestPortOrigin].copy()
                if country_restricted_key in port_origin:
                    port_origin.pop(country_restricted_key)
                
                pref_ports_from = [(port_origin.get('port', None), 1 , port_origin)]

        if port_in_areas_to:
            pref_ports_to = self.get_preferred_ports(*destination, port_in_areas_to, top=None, strict_area=conf_strict_area)
            for i in pref_ports_to:
                _, _, c = i
                if country_restricted_key in c:
                    c.pop(country_restricted_key)

        if len(pref_ports_to)==0:
            closestPortDest = self.query(
                terminals=only_terminals, cty=country_pod).kdtree.query(destination)
            if closestPortDest:
                port_dest = self.nodes[closestPortDest].copy()
                if country_restricted_key in port_dest:
                    port_dest.pop(country_restricted_key)
                
                pref_ports_to = [(port_dest.get('port', None), 1 , port_dest)]

        return list(product(pref_ports_from, pref_ports_to))


    def get_preferred_ports(self, x, y, ft:FeatureCollection, top = None, include_area_name = False, strict_area = True):
        """
        Retrieves the preferred ports based on the given (x, y) location.

        Parameters:
        - x, y: Coordinates of the point to check.
        - ft: FeatureCollection containing multiple Area features.
        - top: (Optional) Limits the number of returned preferred ports.
        - include_area_name: (Optional) If True, includes the area name in the result.

        Returns:
        - A sorted list of preferred ports, normalized by their share value.
        """
        preferred_ports = []

        # Find the smallest area feature containing (x, y)
        smallest_area = min(
            [feature.properties for feature in ft.features 
            if isinstance(feature, area_feature.AreaFeature) and feature.contains(x, y)],
            key=lambda prop: prop.get('area', float('inf')),
            default=None)
        

        if smallest_area is None and strict_area == False:
            # Find the closest polygon based on distance
            max_distance = 2000
            closest_area = None
            closest_distance = float('inf')  # Start with an infinitely large distance

            # Loop through features once and find the closest area within the distance limit
            for feature in ft.features:
                if isinstance(feature, area_feature.AreaFeature):
                    dist = feature.distance(x, y)  # Calculate the distance
                    if dist <= max_distance:  # Check if the distance is within the allowed limit
                        if dist < closest_distance:  # Check if it's the closest found so far
                            closest_area = feature
                            closest_distance = dist
            
            # If a closest area is found, assign its properties
            if closest_area is not None:
                smallest_area = closest_area.properties
            else:
                # If no valid area found, handle it accordingly
                smallest_area ={}   # or assign a default value if necessary

        if smallest_area == None:
            smallest_area = {} 

                
        s_area_name = smallest_area.get('name', None)
        preferred_ports = smallest_area.get('preferred_ports', [])
        
        _sum = 0
        for p in preferred_ports:
            _sum+=p.share

        def _update_props(port_id, props):
            # update props
            if props is None or props == {}:
                try:
                    res = [y for x,y in self.nodes(data=True) if y['port']==port_id]
                    if len(res)>0:
                        return res[0] # first values
                except:
                    pass
            return props 

        if include_area_name:
            sorted_by_second = sorted([(a, b/max(_sum, 1), _update_props(a, c), s_area_name) for a,b,c in preferred_ports], key=lambda tup: tup[1], reverse=True)
        else:
            sorted_by_second = sorted([(a, b/max(_sum, 1), _update_props(a, c)) for a,b,c in preferred_ports], key=lambda tup: tup[1], reverse=True)
        
        if top:
            return sorted_by_second[:top]
        else:
            return sorted_by_second

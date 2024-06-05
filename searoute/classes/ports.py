import networkx as nx

from ..utils import load_from_geojson
from .kdtree import KDTree
from . import area_feature
from geojson import FeatureCollection


class Ports(nx.Graph):
    """
    Base class for Ports network is an undirected graph. 
s
    A Ports graph stores nodes and edges with optional data, or attributes.

    Nodes are identified by an id of tuple representing a spacial location
    with (lon, lat) and it's attributes if applied.
    They form ports located around the world.


    """

    def __init__(self):
        super().__init__()
        DEFAULT_CRF = 'EPSG:3857'
        self.graph['crs'] = DEFAULT_CRF  # CRS attribute for the graph
        self.kdtree = KDTree()

    def add_node(self, node, **attr):
        if not isinstance(node, tuple):
            raise TypeError(
                "Node must be a str representing coordinates of a port.")
        x, y = node
        attr['x'] = x
        attr['y'] = y
        if not (attr['port'] and attr['cty']):
            raise TypeError(
                "Node port requires to have both port name (name), and country (cty) in properties to be correctly mapped")

        self.kdtree.add_point(node)
        super().add_node(node, **attr)


    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

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
        filtered_nodes_prev = None

        if len(filtered_nodes)>0:
            # add filter "from county"
            filtered_nodes_prev = filtered_nodes
            filtered_nodes = [(n, data) for n, data in filtered_nodes_prev if cty_filter(data, cty)]

        if len(filtered_nodes)>0:
            # add filter "to county"
            filtered_nodes_prev = filtered_nodes
            filtered_nodes = [(n, data) for n, data in filtered_nodes_prev if cty_to_filter(data, to_cty)]

        # finally bring all 
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

    

    def get_preferred_ports(self, x,y, ft:FeatureCollection, top = None, include_area_name = False):
        preferred_ports = []
        
        s_area = None
        s_area_size = float('inf')
        s_area_name = None
        
        _sum = 0
        for feature in ft.features:
            if not isinstance(feature, area_feature.AreaFeature):
                continue
            
            if feature.contains(x,y):
                prop = feature.properties
                
                name = prop.get('name', None)
                area = prop.get('area', float("inf"))

                if s_area_size >= area:
                    s_area_size = area
                    s_area = prop
                    s_area_name = name
                
        preferred_ports = s_area.get('preferred_ports', [])
        
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

    
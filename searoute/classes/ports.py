import networkx as nx

from ..utils import load_from_geojson
from .kdtree import KDTree


class Ports(nx.Graph):
    """Base class for Ports network is an undirected graph. 

    A Ports grpah stores nodes and edges with optional data, or attributes.

    Nodes are identified by an id of tuple representing a spacial location
    with (lon, lat) and it's attributes if applied.
    They form portes located around the world.


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

    def subgraph(self, nodes):

        subg = super().subgraph(nodes)
        subg.kdtree = KDTree(nodes)

        return subg

    def query(self, terminals: bool = True, cty: str = None):
        """
        Query the Port graph

        Parameters
        ----------
                
        terminal: boolean, default True
            filters out only terminal marked ports
        cty : str, default None
            filters out ports in given country code (must be an ISO country code with 2 letters uppercase)

        Returns
        -------
        A subgraph of Ports filtered
        """

        if not terminals and not cty:
            return self

        def cty_filter(port, cty):
            if not cty:
                return True
            else:
                return port == cty

        terminal_filter = True if terminals else None

        filtered_nodes = [n for n, data in self.nodes(data=True) if data.get(
            't') == terminal_filter and cty_filter(data.get('port')[:2], cty)]
        
        if not filtered_nodes or len(filtered_nodes)==0:
            # filter without cty as cty seems to not have ports :/
            filtered_nodes = [n for n, data in self.nodes(data=True) if data.get(
            't') == terminal_filter]
        subgraph = self.subgraph(filtered_nodes)
        return subgraph

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

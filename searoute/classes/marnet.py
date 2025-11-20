import networkx as nx
import warnings
from .passages import Passage
from ..utils import load_from_geojson, distance
from .kdtree import KDTree


class Marnet(nx.Graph):
    """Base class for maritime network is an undirected graph. 

    A Marnet stores nodes and edges with optional data, or attributes.

    Nodes are identified by an id of tuple representing a spacial location
    with (lon, lat) and it's attributes if applied.
    They form maritime routes on water.

    
    """

    def __init__(self):
        super().__init__()
        DEFAULT_CRF = 'EPSG:3857'
        self.graph['crs'] = DEFAULT_CRF  # CRS attribute for the graph
        self.restrictions = [Passage.northwest]
        self.kdtree = KDTree()

    def add_node(self, node, **attr):
        if not isinstance(node, tuple):
            raise TypeError(
                "Node must be a tuple representing the coordinates.")
        x, y = node
        attr['x'] = x
        attr['y'] = y

        self.kdtree.add_point(node)
        super().add_node(node, **attr)

    def add_edge(self, u, v, **attr):
        if not isinstance(u, tuple) or not isinstance(v, tuple):
            raise TypeError(
                "Nodes must be tuples representing the coordinates.")

        # Create nodes if they don't exist in the graph
        if u not in self:
            self.add_node(u)
        if v not in self:
            self.add_node(v)

        if not "weight" in attr:
            length = distance(u, v)
            attr["weight"] = round(length, 1)
        super().add_edge(u, v, **attr)

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


    def subgraph(self, nodes):

        subg = super().subgraph(nodes)
        subg.kdtree = KDTree(nodes)

        return subg

    def edge_subgraph(self, edges):

        subg = super().edge_subgraph(edges)
        # subg.kdtree = KDTree([item for tpl in tuples_list for item in tpl])

        return subg

    def query(self, apply_restrictions=True, restrictions=None):
        """
        Query the Marnet graph

        Parameters
        ----------
        apply_restrictions : boolean, default True
            Filters out edges with passages out of restriction list
        restrictions : list of passages to be restricted
            A list of str, by default is None which means the restrictions of the Marnet

        Returns
        -------
        A subgraph of Marnet filtered
        """

        if apply_restrictions:
            restrictions_ = restrictions or self.restrictions
            filtered_edges = [(u, v) for u, v, data in self.edges(
                data=True) if data.get('passage', None) not in restrictions_]
            return self.subgraph(filtered_edges)
        else:
            return self

    def filter_avoid_passages(self, u, v, edge_data, args):
        edge_values = edge_data.values()

        avoid_edge = any(value.get('passage', None) in (
            self.restrictions or []) for value in edge_values)

        return not (avoid_edge)

    def load_geojson(self, *path):
        return load_from_geojson(self, *path)
    

    def update_kdtree(self, nodes = None):
        if nodes:
            self.kdtree = KDTree(nodes)
        else:
            self.kdtree = KDTree(self._node)

    def shortest_path(self, origin, destination):
        """
        Shortest Path between the origin and the destination.
        Dijkstra algorithm is used to perform the calculation.

        Parameters
        ----------
        origin : origin location, in the graph or not,
            if origin is not a known node, a closed node search will be performed
        destination : destination location in the graph or not
            if destination is not a known node, a closed node search will be performed

        Returns
        -------
        A list of nodes building the shortest path, or None if no path exits
        
        """
        origin_node = self.kdtree.query(origin)
        destination_node = self.kdtree.query(destination)

        def filter_edge(u, v):
            edge_data = self.get_edge_data(u, v)
            passage = edge_data.get('passage', None)
            return passage not in self.restrictions
        
        # create subgraph view without restricted edges
        filtered_graph = nx.subgraph_view(self, filter_edge=filter_edge)

        try:
            return nx.shortest_path(
                filtered_graph, origin_node, destination_node, weight='weight')
        except nx.NetworkXNoPath:
            warnings.warn(
                f"No path found between {origin} and {destination}. "
                f"The route may be blocked by passage restrictions: {self.restrictions}",
                UserWarning
            )
            return None # No path exists

    @staticmethod
    def from_geojson(*path):
        return Marnet().load_geojson(*path)

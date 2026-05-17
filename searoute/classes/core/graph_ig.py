from collections import defaultdict
from igraph import Graph as IGraph


def path_ix_to_name(g, path):
    """
    Convert vertex indices to vertex names
    """
    return [g.vs[ix]["name"] for ix in path]


class NodeAccessor:
    def __init__(self, graph):
        self.graph = graph

    def __getitem__(self, key):
        """
        O(1) lookup using name_to_idx
        """
        if isinstance(key, int):
            return self.graph.vs[key].attributes()

        idx = self.graph.name_to_idx[key]
        return self.graph.vs[idx].attributes()

    def __iter__(self):
        return iter(range(self.graph.vcount()))

    def __call__(self, data=False):
        if data:
            return [
                (v["name"], v.attributes())
                for v in self.graph.vs
            ]
        return [v["name"] for v in self.graph.vs]


class EdgeAccessor:
    def __init__(self, graph):
        self.graph = graph

    def __getitem__(self, key):
        """
        Access edge by:
        - integer index -> edge attributes
        - tuple(source, target) -> edge attributes
        """

        # Access by edge index
        if isinstance(key, int):
            return self.graph.es[key].attributes()

        # Access by (source, target)
        if isinstance(key, tuple) and len(key) == 2:
            source, target = key

            # Convert names → indices if needed
            if isinstance(source, str):
                source = self.graph.name_to_idx[source]
            if isinstance(target, str):
                target = self.graph.name_to_idx[target]

            edge_id = self.graph.get_eid(source, target)
            return self.graph.es[edge_id].attributes()

        raise KeyError(f"Invalid edge key: {key}")

    def __iter__(self):
        """
        Iterate over edge indices
        """
        return iter(range(self.graph.ecount()))

    def __call__(self, data=False):
        """
        Similar to NetworkX:
        
        graph.edges() -> [(u, v), ...]
        graph.edges(data=True) -> [(u, v, attrs), ...]
        """

        edges = []

        for e in self.graph.es:
            source = self.graph.vs[e.source]["name"]
            target = self.graph.vs[e.target]["name"]

            if data:
                edges.append(
                    (source, target, e.attributes())
                )
            else:
                edges.append((source, target))

        return edges



class GraphIG(IGraph):
    def __init__(self, *args, **kwargs):
        """
        Optimized igraph wrapper
        """
        self.name_to_idx = {}
        self.graph = {}

        # use set for O(1) membership lookup
        self.restrictions = set()

        #cache weights for fast access during pathfinding
        self.passage_to_edges = defaultdict(list)

        super().__init__(*args, **kwargs)

    # ---------------------------
    # NODE CREATION (optimized)
    # ---------------------------
    @property
    def _node(self):
        raise NotImplementedError("This is a setter-only property.")

    @_node.setter
    def _node(self, nodes: dict):
        """
        Bulk insert vertices (much faster than add_vertex loop)
        """

        names = list(nodes.keys())

        # Add all vertices at once
        self.add_vertices(len(names))

        # Set vertex names
        self.vs["name"] = names

        # Build fast lookup dict
        self.name_to_idx = {
            name: i for i, name in enumerate(names)
        }

        # Collect all attribute keys
        all_keys = set()
        for attrs in nodes.values():
            all_keys.update(attrs.keys())

        # Assign attributes in bulk
        for key in all_keys:
            if key == "name":
                continue

            self.vs[key] = [
                nodes[name].get(key)
                for name in names
            ]

    # ---------------------------
    # EDGE CREATION (optimized)
    # ---------------------------
    @property
    def _adj(self):
        raise NotImplementedError("This is a setter-only property.")

    @_adj.setter
    def _adj(self, edges_set: dict):
        """
        Bulk insert edges + attributes
        """

        if not self.name_to_idx:
            raise ValueError(
                "Vertices must be set before setting edges."
            )

        edges = []
        attrs_list = []  # one dict per edge, in order

        for u, targets in edges_set.items():
            u_idx = self.name_to_idx[u]

            for v, attr in targets.items():
                v_idx = self.name_to_idx[v]

                edges.append((u_idx, v_idx))
                attrs_list.append(attr)  # store the full attr dict for this edge

        
        self.add_edges(edges)

        # Collect all keys across all edges
        all_keys = set(key for attr in attrs_list for key in attr)

        # Transpose: for each key, get value from each edge (None if missing)
        for key in all_keys:
            atrs = []

            for eid, attr in enumerate(attrs_list):
                val = attr.get(key, None)
                atrs.append(val)
    
                if key == "passage" and val is not None:
                    self.passage_to_edges[val].append(eid)

            self.es[key] = atrs


            #self.es[key] = [attr.get(key, None) for attr in attrs_list]


    # ---------------------------
    # NODE ACCESS
    # ---------------------------
    @property
    def nodes(self):
        return NodeAccessor(self)

    # ---------------------------
    # EDGE ACCESS
    # ---------------------------
    @property
    def edges(self):
        return EdgeAccessor(self)

    # ---------------------------
    # SUBGRAPH
    # ---------------------------
    def subgraph(self, node_names):
        nodes = [
            self.name_to_idx[name]
            for name in node_names
            if name in self.name_to_idx
        ]
        return super().subgraph(nodes)


    def get_edge_data(self, u, v, default=None):
        """
        Same behavior as NetworkX:
        G.get_edge_data(u, v, default=None)
        """

        try:
            u_ix = self.name_to_idx[u]

            v_ix = self.name_to_idx[v]

            edge_id = self.get_eid(u_ix, v_ix)
            return self.es[edge_id].attributes()

        except Exception:
            return default



def avoid_passages0(g, avoid=None):
    if not avoid:
        return g.es["weight"]  # no copy needed — read only

    avoid_set = set(avoid)  # O(1) lookup, already a set but safety
    return [
        float("inf") if p in avoid_set else w
        for p, w in zip(g.es["passage"], g.es["weight"])
    ]

def avoid_passages(g, avoid=None):
    base_wights = g.es["weight"]
    if not avoid:
        return base_wights  # no copy needed — read only

    avoid_set = set(avoid)  # O(1) lookup, already a set but safety

    weights = base_wights.copy()

    for restricted_passage in avoid_set:
        for eid in g.passage_to_edges.get(restricted_passage, []):
            weights[eid] = float("inf")

    return weights

# -----------------------------------
# SHORTEST PATH
# -----------------------------------
def bidirectional_dijkstra(G:IGraph, source, target, weight="weight"):
    """
    Optimized shortest path:
    - only runs Dijkstra once
    - uses cached weights
    """

    source_idx = G.name_to_idx[source]
    target_idx = G.name_to_idx[target]

    path_idx = G.get_shortest_paths(
        source_idx,
        target_idx,
        algorithm="dijkstra", 
        weights = avoid_passages(G, G.restrictions)
    )[0]

    if not path_idx:
        return float("inf"), []

    # Compute total distance without running Dijkstra again
    total_distance = sum(
        float("inf") if edge["passage"] in G.restrictions else edge["weight"]
        for u, v in zip(path_idx, path_idx[1:])
        for edge in [G.es[G.get_eid(u, v)]]
    )

    return total_distance, path_ix_to_name(G, path_idx)

# -----------------------------------
# A*
# -----------------------------------
def astar_path(G:IGraph, source, target, heuristic=None, weight="weight"):
    """
    Optimized shortest path:
    - only runs A* once
    - uses cached weights
    """

    return bidirectional_dijkstra(G, source, target, weight)

    source_idx = G.name_to_idx[source]
    target_idx = G.name_to_idx[target]

    def custom_heuristic(graph, u, v):
        if heuristic is None:
            return 1
        return heuristic(
            graph.vs[u]["name"],
            graph.vs[v]["name"]
        )

    path_idx = G.get_shortest_path_astar(
        source_idx,
        target_idx,
        heuristics=custom_heuristic, 
        weights = avoid_passages(G, G.restrictions),
    )

    if not path_idx:
        return float("inf"), []
    

    # Compute total distance without running Dijkstra again
    total_distance = sum(
        float("inf") if edge["passage"] in G.restrictions else edge["weight"]
        for u, v in zip(path_idx, path_idx[1:])
        for edge in [G.es[G.get_eid(u, v)]]
    )

    return total_distance, path_ix_to_name(G, path_idx)
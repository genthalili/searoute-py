import networkx as nx

class GraphNx(nx.Graph):
    pass

def bidirectional_dijkstra(G:nx.Graph, source, target, weight="weight"):
    return nx.bidirectional_dijkstra(G, source, target, weight)

def astar_path(G:nx.Graph, source, target, heuristic=None, weight="weight"):
    # get path from astar function
    g_path = nx.astar_path(G, source, target, heuristic=heuristic, weight=weight)
    
    # measure weight, can be inf
    total_ln = sum(weight(u, v, G[u][v]) for u, v in zip(g_path[:-1], g_path[1:]))
    return total_ln, g_path

from .graph_nx import GraphNx, bidirectional_dijkstra as nx_dijkstra, astar_path as nx_astar

# Optional igraph backend
try:
    from .graph_ig import GraphIG, bidirectional_dijkstra as ig_dijkstra, astar_path as ig_astar
except ImportError:
    GraphIG = None
    ig_dijkstra = None
    ig_astar = None

# default binding at module level so import works immediately
_DEFAULT = "networkx"
bidirectional_dijkstra = nx_dijkstra
astar_path = nx_astar

class GraphBaseMeta(type):
    def __instancecheck__(cls, instance):
        return any(isinstance(instance, b) for b in cls._BACKENDS.values())
    
class Graph(metaclass=GraphBaseMeta):
    _BACKENDS = {
        "networkx": {"class": GraphNx, "bidirectional_dijkstra": nx_dijkstra, "astar_path": nx_astar},
        "igraph": {"class": GraphIG, "bidirectional_dijkstra": ig_dijkstra, "astar_path": ig_astar},
    }

    def __new__(cls, backend=None, **kwargs):

        if backend is None:
            backend = _DEFAULT
        else:
            if backend not in cls._BACKENDS:
                raise ValueError(f"Unknown backend '{backend}'. Choose from: {list(cls._BACKENDS.keys())}")

        cfg = cls._BACKENDS[backend]
        Base = cfg["class"]

        if Base is None:
            raise ImportError(
                "igraph backend is not installed. Run: pip install searoute[igraph] or pip install igraph"
            )

        # Inject algorithms as module-level names dynamically
        import sys
        module = sys.modules[cls.__module__]
        for name, fn in cfg.items():
            if name != "class":
                setattr(module, name, fn)  # rebind at module level 
        
        # Skip if already a resolved dynamic class (avoid infinite recursion)
        if Base in cls.__bases__:
            return Base.__new__(cls)
        
        # DynamicClass inherits from Marnet + Base, so super() works correctly
        DynamicClass = type(cls.__name__, (cls, Base), {"__new__": Base.__new__})
        instance = Base.__new__(DynamicClass)
        return instance

    def __init__(self, backend="graph_ig", *args, **kwargs):
        super().__init__(*args, **kwargs)


__all__ = [
    "Graph",
    "bidirectional_dijkstra",
    "astar_path"
]
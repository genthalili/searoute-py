"""Export only Madeira additions, preserving unrelated runtime/source differences.

Run from the checkout root: python tools/update_madeira_network.py
Uses the repository GeoJSON loader and graph dictionary exporter.
"""
from pathlib import Path

import searoute as sr
from searoute.utils import to_nodes_edges_set

ROOT = Path(__file__).resolve().parents[1]
NEW_NODES = {(-16.900556, 32.634167), (-16.9, 32.6), (-17.45, 32.5), (-17.45, 32.9)}
source = sr.Marnet.from_geojson(str(ROOT / "searoute/data/marnet_searoute.geojson"))
network = sr.setup_M()
for node in source:
    if node in NEW_NODES:
        network.add_node(node, **source.nodes[node])
for u, v, attributes in source.edges(data=True):
    if u in NEW_NODES or v in NEW_NODES:
        network.add_edge(u, v, **attributes)
        network.add_edge(v, u, **attributes)
to_nodes_edges_set(network, str(ROOT / "searoute/data/marnet_dict.py"))

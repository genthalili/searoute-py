"""Funchal coverage regressions using the normal packaged maritime network."""
import json
from pathlib import Path

import networkx as nx
import pytest
from shapely.geometry import LineString, Point, shape
from shapely.ops import unary_union

import searoute as sr
from searoute.utils import distance

HARBOUR = [-16.900556, 32.634167]
NEW_NODES = {tuple(HARBOUR), (-16.9, 32.6), (-17.45, 32.5), (-17.45, 32.9)}
LAND = unary_union([
    shape(feature["geometry"])
    for feature in json.loads(
        (Path(__file__).parent / "fixtures" / "madeira-land.geojson").read_text()
    )["features"]
])


@pytest.mark.parametrize("origin", [HARBOUR, [-16.895, 32.63], [-16.91, 32.632]])
@pytest.mark.parametrize("destination", [[-18., 32.], [-17.183808, 33.116222], [-16.31887, 32.773089]])
@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("append", [False, True])
def test_funchal_routes_stay_in_water(origin, destination, reverse, append):
    assert not LAND.intersects(Point(origin))
    start, end = (destination, origin) if reverse else (origin, destination)
    route = sr.searoute(start, end, append_orig_dest=append)
    coords = route["geometry"]["coordinates"]
    harbour_end = coords[-2 if append else -1] if reverse else coords[1 if append else 0]
    assert distance(origin, harbour_end) < 1.5
    assert len(coords) >= 2
    # Check whole segment interiors, rather than just route vertices.
    assert not LineString(coords).intersects(LAND)
    assert route["properties"]["length"] > 0


def test_madeira_edges_connected_and_match_source():
    network = sr.setup_M()
    source = sr.Marnet.from_geojson(
        str(Path(sr.__file__).parent / "data" / "marnet_searoute.geojson")
    )
    assert NEW_NODES <= set(network)
    component = nx.node_connected_component(network, (-17.183808, 33.116222))
    assert NEW_NODES <= component
    # Removing the added nodes must leave the same number of components.
    original = network.copy()
    original.remove_nodes_from(NEW_NODES)
    assert nx.number_connected_components(original) == nx.number_connected_components(network)
    for node in NEW_NODES:
        assert dict(network[node]) == dict(source[node])
        for neighbour, attributes in network[node].items():
            assert network[neighbour][node] == attributes
            assert attributes["weight"] == round(distance(node, neighbour), 1)
            assert not LineString([node, neighbour]).intersects(LAND)

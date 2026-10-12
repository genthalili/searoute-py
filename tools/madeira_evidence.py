"""Reproduce Madeira coastline extraction, public API routes and map evidence.

See evidence/madeira/README.md for commands and provenance.
"""
import argparse
import json
from pathlib import Path
import runpy
import struct
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import searoute as sr
from shapely.geometry import LineString, Point, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "searoute/tests/fixtures/madeira-land.geojson"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--coastline-archive", type=Path)
parser.add_argument("--baseline-runtime", type=Path)
args = parser.parse_args()

if args.coastline_archive:
    features = []
    with zipfile.ZipFile(args.coastline_archive) as archive:
        with archive.open("gshhs_f.b") as stream:
            while header := stream.read(44):
                ident, n, flag, west, east, south, north, *_ = struct.unpack(
                    ">11i", header
                )
                points = stream.read(n * 8)
                # Whole level-1 polygons within the Madeira archipelago region.
                if flag & 255 != 1 or not (
                    340000000 < west < 345000000 and 30000000 < south < 35000000
                ):
                    continue
                coordinates = [
                    [x / 1e6 - 360, y / 1e6]
                    for x, y in struct.iter_unpack(">2i", points)
                ]
                features.append({
                    "type": "Feature", "properties": {"id": ident},
                    "geometry": {"type": "Polygon", "coordinates": [coordinates]},
                })
    FIXTURE.write_text(json.dumps(
        {"type": "FeatureCollection", "features": features}, separators=(",", ":")
    ) + "\n")

features = json.loads(FIXTURE.read_text())["features"]
land = unary_union([shape(f["geometry"]) for f in features])
output = ROOT / "evidence/madeira"
output.mkdir(parents=True, exist_ok=True)
summary = {}

for label in ("before", "after"):
    if label == "before":
        if not args.baseline_runtime:
            continue
        baseline = runpy.run_path(str(args.baseline_runtime))
        graph = sr.from_nodes_edges_set(
            sr.Marnet(), baseline["node_list"], baseline["edge_list"]
        )
        graph_args = {"M": graph}
    else:
        # Exercise the installed package's normal default maritime network.
        graph_args = {}
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_facecolor("#e6f3fa")
    for feature in features:
        ring = feature["geometry"]["coordinates"][0]
        x, y = zip(*ring)
        ax.fill(x, y, color="#ded8c5", edgecolor="#786c54", linewidth=0.7)
    for name, origin, color, style in (
        ("harbour", [-16.900556, 32.634167], "#086ca8", "-"),
        ("cached", [-16.9086783, 32.6496497], "#c0392b", "--"),
    ):
        for append in (False, True):
            route = sr.searoute(
                origin, [-18., 32.], append_orig_dest=append, **graph_args
            )
            path = route["geometry"]["coordinates"]
            (output / f"{label}-{name}-{append}.geojson").write_text(
                json.dumps(route, indent=2) + "\n"
            )
            if append:
                crosses = LineString(path).intersects(land)
                summary[f"{label}-{name}"] = {
                    "input_on_land": land.intersects(Point(origin)),
                    "route_intersects_land": crosses,
                    "length_km": route["properties"]["length"],
                    "snapped_node": path[1],
                }
                x, y = zip(*path)
                ax.plot(x, y, style, color=color, linewidth=2,
                        marker="o", markersize=4,
                        label=f"{name}: {'intersects land' if crosses else 'in water'}")
    ax.text(-17.12, 32.77, "Madeira", fontsize=12)
    ax.set(xlim=(-18.1, -16.25), ylim=(31.92, 33.22),
           xlabel="Longitude (WGS84)", ylabel="Latitude (WGS84)",
           title=f"Funchal → southwest offshore: {label}")
    ax.set_aspect(1 / 0.84)
    ax.grid(alpha=0.2)
    ax.legend(loc="lower right")
    fig.text(0.5, 0.02,
             "Coastline: GSHHG 2.3.7 full resolution · Wessel & Smith / UH / NOAA · LGPL-3.0-or-later",
             ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(output / f"{label}.png", dpi=150)
    plt.close(fig)
(output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))

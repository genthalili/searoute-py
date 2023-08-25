<p align="center">
 <img src="https://raw.githubusercontent.com/genthalili/searoute-py/main/searoute/assets/searoute_logo.png" alt="Searoute-py" width=350>
</p>
<p align="center">
<a href="https://pypi.org/project/searoute" target="_blank">
    <img src="https://img.shields.io/pypi/v/searoute.svg" alt="Package version">
</a>
<a href="https://pepy.tech/project/searoute" target="_blank">
    <img src="https://static.pepy.tech/personalized-badge/searoute?period=total&units=international_system&left_color=grey&right_color=green&left_text=downloads" alt="Downloads">
</a>
<a href="https://pypi.org/project/searoute" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/searoute.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>

---
## Searoute py

A python package for generating the shortest sea route between two points on Earth. 

If points are on land, the function will attempt to find the nearest point on the sea and calculate the route from there. 

**Not for routing purposes!** This library was developed to generate realistic-looking sea routes for visualizations of maritime routes, not for mariners to route their ships. 

![Searoute map](https://raw.githubusercontent.com/genthalili/searoute-py/main/searoute/assets/searoute.png)

## Installation

~~~bash
pip install searoute
~~~

## Usage

~~~py
import searoute as sr

#Define origin and destination points:
origin = [0.3515625, 50.064191736659104]

destination = [117.42187500000001, 39.36827914916014]


route = sr.searoute(origin, destination)
# > Returns a GeoJSON LineString Feature
# show route distance with unit
print("{:.1f} {}".format(route.properties['length'], route.properties['units']))

# Optionally, define the units for the length calculation included in the properties object.
# Defaults to km, can be can be 'm' = meters 'mi = miles 'ft' = feets 'in' = inches 'deg' = degrees
# 'cen' = centimeters 'rad' = radians 'naut' = nauticals 'yd' = yards
routeMiles = sr.searoute(origin, destination, units="mi")
~~~
### Bring your network :
```py
# using version >= 1.2.0

# nodes representing (1,2) of lon = 1, lat = 2
# required : 'x' for lon, 'y' for lat ; optional 'tt' for terminals (boolean or None)
my_nodes = {
    (1, 2): {'x': 1, 'y': 2},
    (2, 2): {'x': 2, 'y': 2}
}
# (1,2) -> (2,2) with weight, representing the distance, other attribures can be added
# recognized attributes are : `weight` (distance), `passage` (name of the passage to be restricted by restrictions) 
my_edges = {
    (1, 2): {
        (2, 2): {"weight": 10, "other_attr": "some_value"}
    }
}

# Marnet
myM = sr.from_nodes_edges_set(sr.Marnet(), my_nodes, my_edges)
# Ports
myP = sr.from_nodes_edges_set(sr.Ports(), my_nodes, None) 

# get shotest with your ports
route_with_my_ports = sr.searoute(origin, destination, P = myP, include_ports=True)

# get shotest with your ports
route_with_my_ntw = sr.searoute(origin, destination, P = myP, M = myM )

```
### Nodes and Edges
#### Nodes 
A node (or vertex) is a fondamantal unit of which the graphs Ports and Marnet are formed.

In searoute, a node is represend by it's id as a ``tuple`` of lon,lat, and it's attributes:
- `x` : float ; required
- `y` : float ; required
- `t` : bool ; optional. default is `False`, will be used for filtering ports with `terminals`.
```py
{
    (lon:float, lat:float): {'x': lon:float, 'y': lat:float, *args:any},
    ...
}
```
#### Edges 
An edge is a line or connection between a note and an other. This connection can be represented by a set of node_id->node_id with it's attributes:
- `weight` : float ; required. Can be distance, cost etc... if not set will by default calculate the distance between nodes using [Haversine formula](https://en.wikipedia.org/wiki/Haversine_formula).
- `passage` : str ; optional.  Can be one of Passage (searoute.classes.passages.Passage). If not not set, no restriction will be applied. If set make sure to update `Marnet().restrictions = [...]` with your list of passages to avoid.
```py
{
    (lon:float, lat:float)->node_id: {
        (lon:float, lat:float)->node_id: {
          "weight": distance:float, 
          *args: any}
    },
    ...
}
```

### Example with more parameters :
~~~py
## Using all parameters, wil include ports as well
route = sr.searoute(origin, destination, append_orig_dest=True, restrictions=['northwest'], include_ports=True, port_params={'only_terminals':True, 'country_pol': 'FR', 'country_pod' :'CN'})
~~~
returns :
~~~json
{
  "geometry": {
    "coordinates": [],
    "type": "LineString"
  },
  "properties": {
    "duration_hours": 461.88474412693756,
    "length": 20529.85310695412,
    "port_dest": {
      "cty": "China",
      "name": "Tianjin",
      "port": "CNTSN",
      "t": 1,
      "x": 117.744852,
      "y": 38.986802
    },
    "port_origin": {
      "cty": "France",
      "name": "Le Havre",
      "port": "FRLEH",
      "t": 1,
      "x": 0.107054,
      "y": 49.485998
    },
    "units": "km"
  },
  "type": "Feature"
}
~~~

## Parameters

`origin`    
Mandatory. A tuple or array of 2 floats representing longitude and latitude i.e : `({lon}, {lat})`

`destination`    
Mandatory. A tuple or array of 2 floats representing longitude and latitude i.e : `({lon}, {lat})`

`units`    
Optional. Default to `km` = kilometers, can be `m` = meters `mi` = miles `ft` = feets `in` = inches `deg` = degrees `cen` = centimeters `rad` = radians `naut` = nauticals `yd` = yards

`speed_knot`    
Optional. Speed of the boat, default 24 knots 

`append_orig_dest`    
Optional. If the origin and destination should be appended to the LineString, default is `False`

`restrictions`    
Optional. List of passages to be restricted during calculations.
Possible values : `babalmandab`, `bosporus`, `gibraltar`, `suez`, `panama`, `ormuz`, `northwest`;
default is `['northwest']`

`include_ports`    
Optional. If the port of load and discharge should be included, default is `False`

`port_params`    
Optional. If `include_ports` is `True` then you can set port configuration for advanced filtering :
- `only_terminals` to include only terminal ports, default `False`
- `country_pol` country iso code (2 letters) for closest port of load, default `None`. When not set or not found, closest port is based on geography.
- `country_pod` country iso code (2 letters) for closest port of discharge, default `None`. When not set or not found, closest port is based on geography.

default is `{}`

### Returns
GeoJson Feature
## Credits

- [NetworkX](https://networkx.org/), a Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks.
- [turfpy](https://github.com/omanges/turfpy), a Python library for performing geospatial data analysis which reimplements turf.js.
- [OSMnx](https://github.com/gboeing/osmnx), for geo-spacial networks.
- Eurostat's [Searoute Java library](https://github.com/eurostat/searoute)
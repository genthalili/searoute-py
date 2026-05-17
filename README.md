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
# Defaults to km, can be can be 'm' = meters 'mi = miles 'ft' = feet 'in' = inches 'deg' = degrees
# 'cen' = centimeters 'rad' = radians 'naut' = nautical 'yd' = yards
routeMiles = sr.searoute(origin, destination, units="mi")
~~~
### Graph backend :
Core graph abstraction layer for searoute, providing a unified interface
over multiple graph backends.

It supports two graph backends:
- **networkx** (default): Pure Python, no extra dependencies.
- **igraph** (optional): C-based, significantly faster for large graphs.
  Install with: ``pip install searoute[igraph]`` or ``pip install igraph``

#### Usage :
Basic usage with the default networkx backend
```py

sr.searoute(..., backend = "igraph")  # build the network with igraph

m = Marnet()                          # defaults to networkx
m = Marnet(backend="networkx")        # explicit networkx
m = Marnet(backend="igraph")          # igraph (if installed)
```

### Bring your network :
```py
# using version >= 1.2.0

# nodes representing (1,2) of lon = 1, lat = 2
# required : 'x' for lon, 'y' for lat ; optional 'tt' for terminals (boolean or None)
my_nodes = {
    (1, 2): {'x': 1, 'y': 2},
    (2, 2): {'x': 2, 'y': 2}
}
# (1,2) -> (2,2) with weight, representing the distance, other attributes can be added
# recognized attributes are : `weight` (distance), `passage` (name of the passage to be restricted by restrictions) 
# Note: Ensure that both directions of the edge are included. If (u, v) is added, (v, u) should also be included to account for bidirectional relationships.
my_edges = {
    (1, 2): {
        (2, 2): {"weight": 10, "other_attr": "some_value u->v"}
    }
    (2, 2): {
        (1, 2): {"weight": 10, "other_attr": "some_value v->u"}
    }
}

# Marnet
myM = sr.from_nodes_edges_set(sr.Marnet(), my_nodes, my_edges)
# Ports
myP = sr.from_nodes_edges_set(sr.Ports(), my_nodes, None) 

# get shortest with your ports
route_with_my_ports = sr.searoute(origin, destination, P = myP, include_ports=True)

# get shortest with your ports
route_with_my_ntw = sr.searoute(origin, destination, P = myP, M = myM )

```
### Nodes and Edges
#### Nodes 
A node (or vertex) is a fundamental unit of which the graphs Ports and Marnet are formed.

In searoute, a node is represented by it's id as a ``tuple`` of lon,lat, and it's attributes:
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
    "port_origin": {
      "cty": "France",
      "name": "Le Havre",
      "port": "FRLEH",
      "t": 1,
      "x": 0.107054,
      "y": 49.485998
    },
    "port_dest": {
      "cty": "China",
      "name": "Tianjin",
      "port": "CNTSN",
      "t": 1,
      "x": 117.744852,
      "y": 38.986802
    },
    "units": "km"
  },
  "type": "Feature"
}
~~~

## Preferred Ports

Preferred ports can be defined using one or more `AreaFeature` objects:

Start by creating or referencing preferred ports with the `PortProps` class.A PortProps instance includes:

  - `port_id` — the port identifier
  - `share` — a positive weight used for selection
  - `props` — optional attributes describing the port (e.g., coordinates or metadata)



```py
# your preferred ports
port_one = PortProps('MY_PORT_ID', 2, {'x':1, 'y':2})
port_two = PortProps('USNYC', 1)
```
Initiate a `AreaFeature` with its coords and a name, as well as `list` of `preferred_ports` (could be a `list`, `str`, or `PortProps`)
```py
# initiate an AreaFeature
area_one = AreaFeature(coordinates=[[[0,0], [0,10],[0,20], [20, 20], [0, 0]]], name= 'Special_Name', preferred_ports=[port_one, port_two])

# create other AreaFeature
area_two = AreaFeature(...)
```
When multiple AreaFeature objects contain a point, the smallest area will be used to determine the preferred ports.

Finally, call the function which will return a tuple of 3 values, or 4 values when `include_area_name` is set to `True`:
```py
# myPorts is the instance of Port, by default is sr.setup_P()
origin = (11, 12)
pref_ports = myPorts.get_preferred_ports(*origin, AreaFeature.create([area_one, area_two]), top=2, include_area_name = True)
```

### Usage in main function
````py
areas = AreaFeature.create([area_one, area_two])
sr.searoute(..., include_ports = True, port_params = {'ports_in_areas': areas})
````



## Parameters

* **`origin`** *(required)*
  Tuple or array of two floats representing the **longitude and latitude** of the starting point.

  Example:

  ```
  (lon, lat)
  ```

* **`destination`** *(required)*
  Tuple or array of two floats representing the **longitude and latitude** of the destination point.

  Example:

  ```
  (lon, lat)
  ```

* **`units`** *(optional)*
  Unit used to compute the route distance.

  Default:
  ```
  km
  ```

  Supported values:
  `km` = kilometers, `m` = meters `mi` = miles `ft` = feets `in` = inches `deg` = degrees `cen` = centimeters `rad` = radians `naut` = nauticals `yd` = yards

* **`speed_knot`** *(optional)*
  Vessel speed used to estimate route duration.

  Default:

  ```
  24
  ```

  Unit: **knots**

* **`append_orig_dest`** *(optional)*
  If `True`, the origin and destination coordinates will be appended to the returned `LineString`.

  Default:

  ```
  False
  ```

* **`restrictions`** *(optional)*
  List of maritime passages to **avoid during route calculation**.

  Default:

  ```
  ["northwest"]
  ```

  Supported values:  `babalmandab`, `bosporus`, `gibraltar`, `suez`, `panama`, `ormuz`, `northwest`, `malacca`, `sunda`, `chili`, `south_africa`

* **`include_ports`** *(optional)*
  If `True`, the algorithm includes the **port of loading (POL)** and **port of discharge (POD)** in the result.

  Default:

  ```
  False
  ```

* **`port_params`** *(optional)*
  Additional configuration used when `include_ports=True`.

  Available options:

  * **`only_terminals`**
    Include only terminal ports.
    Default: `False`

  * **`country_pol`**
    ISO-2 country code used to select the **Port of Loading (POL)**.
    If not provided, the closest port geographically will be selected.

    Example:

    ```
    "FR"
    ```

  * **`country_pod`**
    ISO-2 country code used to select the **Port of Discharge (POD)**.
    If not provided, the closest port geographically will be selected.

  * **`country_restricted`**
    Filters out ports that define a `to_cty` attribute containing the same country code as `country_pod`.

    Default:

    ```
    False
    ```

  * **`ports_in_areas`**
    Overrides all previous port filtering rules and defines preferred ports within geographic areas.

    Must be created using:

    ```
    AreaFeature.create([...])
    ```

    Notes:

    * Preferred ports with `share = 0` are ignored.
    * If multiple ports match, the function returns **multiple GeoJSON routes**.

  * **`ports_in_areas_from`**
    Same behavior as `ports_in_areas`, but applied only to the **origin point (POL)**.

  * **`ports_in_areas_to`**
    Same behavior as `ports_in_areas`, but applied only to the **destination point (POD)**.

  * **`strict_area`**
    Only relevant when using `ports_in_areas`, `ports_in_areas_from`, or `ports_in_areas_to`.

    Default:

    ```
    True
    ```

    Behavior:

    * `False` → if the point is outside all areas, the **closest area** is used.
    * `True` → if the point is outside all areas, the configuration is ignored.

* **`return_passages`** *(optional)*
  If `True`, the result will include the **list of traversed maritime passages**.

  Default:

  ```
  False
  ```

* **`algorithm`** *(optional)*
  The algorithm to perform shortest distance calculation.
  Options : `dijkstra`, `astar`

  If concerned by performances, use `astar`.


  *Note : The `A star` algorithm uses the Haversine distance heuristic, and only available for `backend= "networkx"`.* 

  Default:

  ```
  None (dijkstra)
  ```

* **`backend`** *(optional)*
  The algorithm to perform shortest distance calculation.
  Options : `networkx`, `igraph`

  If concerned by performances, use `igraph` which is C-based and **3x times** faster for batch requests.


  Default:

  ```
  networkx
  ```

# Return Value

The function returns:

```
GeoJSON Feature
```

or (when many routes configured in `port_params`)

```
List[GeoJSON Feature]
```


## Credits

- [NetworkX](https://networkx.org/), a Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks.
- [igraph](https://python.igraph.org/en/stable), a Python interface of igraph, a fast and open source C library to manipulate and analyze graphs.
- [GeoJson](https://github.com/jazzband/geojson), a python package for GeoJSON
- Eurostat's [Searoute Java library](https://github.com/eurostat/searoute)
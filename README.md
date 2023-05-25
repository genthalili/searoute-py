<p align="center">
 <img src="https://raw.githubusercontent.com/genthalili/searoute-py/main/searoute/assets/searoute-logo.png" alt="Searoute-py" width=350>
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

An python package for generating the shortest sea route between two points on Earth. 

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
### Example with more parameters :
~~~py
## Using all parameters, wil include ports as well
route = sr.searoute(origin, destination, append_orig_dest=True, restrictions=['northwest'], include_ports=True, port_params={'only_terminals':True, 'country_pol': 'FR', 'country_pod' :'CH'})
~~~
returns :
~~~json
{
  "geometry": {
    "coordinates": [[..],[..],..],
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
Mandatory. An array of 2 floats representing longitude and latitude i.e : `[{lon}, {lat}]`

`destination`    
Mandatory. An array of 2 floats representing longitude and latitude i.e : `[{lon}, {lat}]`

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
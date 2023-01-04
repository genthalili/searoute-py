# Searoute py

An python package for generating the shortest sea route between two points on Earth. 

If points are on land, the function will attempt to find the nearest point on the sea and calculate the route from there. 

**Not for routing purposes!** This library was developed to generate realistic-looking searoutes for visualizations of maritime routes, not for mariners to route their ships. 

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

## Credits

Based on Eurostat's [Searoute Java library](https://github.com/eurostat/searoute) and Dijkstra's algorithm implemented by [perliedman](https://www.liedman.net/geojson-path-finder/).
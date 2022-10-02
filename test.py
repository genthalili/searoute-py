import searoute as sr

#Define origin and destination points:
origin = [121.8983, 29.9445]

destination = [12.6917, 56.0279]


route = sr.searoute(origin, destination)
# > Returns a GeoJSON LineString Feature
# show route distance with unit
print("{:.1f} {}".format(route.properties['length'], route.properties['units']))

print(route)

# Optionally, define the units for the length calculation included in the properties object.
# Defaults to km, can be can be 'm' = meters 'mi = miles 'ft' = feets 'in' = inches 'deg' = degrees
# 'cen' = centimeters 'rad' = radians 'naut' = nauticals 'yd' = yards
routeMiles = sr.searoute(origin, destination, units="mi")

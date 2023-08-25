import searoute as sr

#Define origin and destination points:
origin = [21.1545, 55.6526]
destination = [-118.2629, 33.7276]


route = sr.searoute(origin, destination, append_orig_dest=True, restrictions=['northwest'], include_ports=True, port_params={'only_terminals':True, 'country_pol': '', 'country_pod' :'DD'})
# > Returns a GeoJSON LineString Feature
# show route distance with unit
print("{:.1f} {}".format(route.properties['length'], route.properties['units']))

print(route)

# Optionally, define the units for the length calculation included in the properties object.
# Defaults to km, can be can be 'm' = meters 'mi = miles 'ft' = feets 'in' = inches 'deg' = degrees
# 'cen' = centimeters 'rad' = radians 'naut' = nauticals 'yd' = yards
routeMiles = sr.searoute(origin, destination, units="mi")
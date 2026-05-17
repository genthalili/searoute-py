import searoute as sr

print('current version:', sr.__version__)

#Define origin and destination points:
origin = [21.1545, 55.6526]
destination = [-118.2629, 33.7276]
origin = [5.333333333333333, 43.333333333333336] 
destination = [18.366666666666667, -33.916666666666664]


route = sr.searoute(origin, destination, append_orig_dest=True, algorithm='astar', restrictions=['northwest'], include_ports=True, port_params={'only_terminals':True, 'country_pol': '', 'country_pod' :'', 'country_restricted': False})
# > Returns a GeoJSON LineString Feature
# show route distance with unit
print("{:.1f} {}".format(route.properties['length'], route.properties['units']))

print(route)

# Optionally, define the units for the length calculation included in the properties object.
# Defaults to km, can be can be 'm' = meters 'mi = miles 'ft' = feets 'in' = inches 'deg' = degrees
# 'cen' = centimeters 'rad' = radians 'naut' = nauticals 'yd' = yards
routeMiles = sr.searoute(origin, destination, units="mi")

import searoute as sr

#Define origin and destination points:
origin = [21.1545, 55.6526]
destination = [-118.2629, 33.7276]


origin = [2.650544, 39.571625] 
destination = [13.298993, 38.080190]

origin = [-93.62078577368268,25.737539051869824]
destination = [-40.32618417902073,6.608564614815155]

origin = [101.362, 2.9735]
destination = [149.5505,-34.9452]

#Define origin and destination points:
origin = [0.3515625, 50.064191736659104]
destination = [117.42187500000001, 39.36827914916014]

origin = [0.3515625, 50.064191736659104]

destination = [117.42187500000001, 39.36827914916014]


route = sr.searoute(origin, destination, append_orig_dest=True, restrictions=['northwest'], include_ports=True, port_params={'only_terminals':True, 'country_pol': '', 'country_pod' :'DD'})
# > Returns a GeoJSON LineString Feature
# show route distance with unit
print("{:.1f} {}".format(route.properties['length'], route.properties['units']))

print(route)

# Optionally, define the units for the length calculation included in the properties object.
# Defaults to km, can be can be 'm' = meters 'mi = miles 'ft' = feets 'in' = inches 'deg' = degrees
# 'cen' = centimeters 'rad' = radians 'naut' = nauticals 'yd' = yards
routeMiles = sr.searoute(origin, destination, units="mi")
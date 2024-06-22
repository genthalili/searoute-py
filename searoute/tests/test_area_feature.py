import geojson
from searoute.classes.area_feature import AreaFeature
from searoute.classes.ports_props import PortProps
from searoute.tests.test_utils import generate_random_word, get_eur_like_poly, get_suisse_poly


def test_norm_preferred_ports():
    area = AreaFeature(coordinates = geojson.utils.generate_random("Polygon").coordinates,
                name=generate_random_word(4), 
                preferred_ports=None)
                
    # Test case 1: None input
    result = area.norm_preferred_ports(None)
    assert result == []

    # Test case 2: Single PortProps input
    port_props_instance = PortProps("8080")
    result = area.norm_preferred_ports(port_props_instance)
    print(result)
    assert result == [port_props_instance]

    # Test case 3: String input
    result = area.norm_preferred_ports("9090")
    print(result)
    assert result == [PortProps("9090")]

    # Test case 4: Integer input
    result = area.norm_preferred_ports(7070)
    print(result)
    assert result == [PortProps("7070")]

    # Test case 5: Tuple input
    result = area.norm_preferred_ports((6060,1))
    print(result)
    assert result == [PortProps("6060", 1)]

    # Test case 6: List input with mixed types
    input_list = ["8080", 9090, (6060,), None, "7070"]
    result = area.norm_preferred_ports(input_list)
    print(result)
    assert result == [
        PortProps("8080", 1),
        PortProps("9090", 1),
        PortProps("6060",1),
        PortProps("7070", 1)
    ]
    
    # Test case 7: Unsupported type input
    result = area.norm_preferred_ports(True)
    assert result == [PortProps(True, 1)]

def test_contains():
    # Test if Basel is in Switzerland
    basel_point = (7.6174, 47.5186) # Basel city
    areaCH = AreaFeature(coordinates=get_suisse_poly(), name='CH_poly_area')
    assert True == areaCH.contains(*basel_point)

    # test if Paris is not in Switweland
    paris_point = (2.333333, 48.866667) # Paris
    assert False == areaCH.contains(*paris_point)

    # test example simplified within europe Area
    example_zone_coords = get_eur_like_poly()
    areaEUR = AreaFeature(coordinates = example_zone_coords, name='example_poly_area')
    
    # Paris in EUR
    assert True == areaEUR.contains(*paris_point)
    
    # Basel in EUR
    assert True == areaEUR.contains(*basel_point)
    
    # first 10 point of CH in EUR
    for ch_p in areaCH.geometry.coordinates[0][:10]:
         assert True == areaEUR.contains(*ch_p)

    # New york is not in EUR
    new_york_point = (-74.005941 , 40.712784 )
    assert False == areaEUR.contains(*new_york_point)

    # Tokyo is not in EUR
    tokyo_point = (139.839478, 35.652832 )
    assert False == areaEUR.contains(*tokyo_point)



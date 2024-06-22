from searoute.classes.area_feature import AreaFeature
from searoute.classes.ports_props import PortProps
from searoute.tests.test_utils import get_eur_like_poly, get_suisse_poly

import searoute as sr
import unittest

class TestPortProps(unittest.TestCase):
    def test_initialization(self):
        """Test that a PortProps object is initialized with the correct values."""
        pp = PortProps('port1', 2, {'prop1': 'value1'})
        self.assertEqual(pp.port_id, 'port1')
        self.assertEqual(pp.share, 2)
        self.assertEqual(pp.props, {'prop1': 'value1'})

    def test_default_values(self):
        """Test that default values are correctly applied."""
        pp = PortProps('port2')
        self.assertEqual(pp.port_id, 'port2')
        self.assertEqual(pp.share, 1)
        self.assertIsNone(pp.props)

    def test_properties(self):
        """Test that property getters work as expected."""
        pp = PortProps('port3', 3, {'prop2': 'value2'})
        self.assertEqual(pp.port_id, 'port3')
        self.assertEqual(pp.share, 3)
        self.assertEqual(pp.props, {'prop2': 'value2'})

    def test_immutability(self):
        """Test that the PortProps object is immutable."""
        pp = PortProps('port4', 4, {'prop3': 'value3'})
        with self.assertRaises(AttributeError):
            pp.port_id = 'new_port'
        with self.assertRaises(AttributeError):
            pp.share = 5
        with self.assertRaises(AttributeError):
            pp.props = {'prop4': 'value4'}


    def test_in_list(self):
        port_props_list = [
            PortProps('port1', 2, {'prop1': 'value1'}),
            PortProps('port2', 3, {'prop2': 'value2'}),
            PortProps('port3', 4, {'prop3': 'value3'}),
            # Add more PortProps instances as needed
        ]
        third_port_props = port_props_list[2]
        expected_share_value = 4
        self.assertEqual(third_port_props.share, expected_share_value)
        self.assertNotEqual(third_port_props.share, 1)
        self.assertEqual(port_props_list[1].port_id, 'port2')


    def test_preferred_ports(self):
        # assuming 2 ports prefered
        first_port = PortProps('FRMAR', 2)
        second_port = PortProps('NEW_PRT_ID', 7, {'x':1, 'y':2})

        # point is in Europe
        point = (7, 47)
        # europan area
        eurArea = AreaFeature(get_eur_like_poly(), 
                              name= 'EUR', 
                              preferred_ports=
                              [first_port, second_port])
        

        result = sr.setup_P().get_preferred_ports(*point, AreaFeature.create([eurArea]), top=None, include_area_name = True)
        
        self.assertEqual(2, len(result))
        # get_preferred_ports should return 1st the highest share of preferred ports, here is NEW_PRT_ID with share 7
        self.assertEqual(second_port.port_id, result[0][0])
        self.assertEqual(eurArea.properties['name'], result[0][3])

        # assuming 2 areas
        # it should select the smalles base on its area, here 'CH'
        chArea = AreaFeature(get_suisse_poly(), 
                              name= 'CH', 
                              preferred_ports=
                              [first_port])

        result = sr.setup_P().get_preferred_ports(*point, AreaFeature.create([eurArea, chArea]), top=None, include_area_name = True)
        
        self.assertEqual(chArea.properties['name'], result[0][3])

        # if point elsevere, like Paris
        point = (2.333333, 48.866667)
        result = sr.setup_P().get_preferred_ports(*point, AreaFeature.create([eurArea, chArea]), top=None, include_area_name = True)
        
        self.assertNotEqual(chArea.properties['name'], result[0][3])
        self.assertEqual(eurArea.properties['name'], result[0][3])
        
        
from geojson import Feature, FeatureCollection, Polygon
from typing import Union, List, Tuple
from .ports_props import PortProps
from ..utils import pnpoly


class AreaFeature(Feature):

    @staticmethod
    def create(areas:list) ->List:
        """
        Create a feature collection of geojson type from a list of AreaFeature

        Parameters:
        ==========
        - areas: a list of AreaFeature

        Returns:
        ========
        FeatureCollection
        
        """
        if areas is None:
            raise Exception('Areas can not be empty')
        
        features = []
        for area in areas:
            features.append(area)

        return FeatureCollection(features)
        
        
    def __init__(self, coordinates, preferred_ports:list=None, name=None, **kwargs):
        geometry = Polygon(coordinates)
        super().__init__(geometry=geometry, properties={})

        self.properties['preferred_ports'] = self.norm_preferred_ports(preferred_ports)
        self.properties['name'] = name
        self.properties['area'] = self.calculate_geometry_area(coordinates[0])
        self.properties.update(kwargs)
        self.type = 'Feature'

    
    
    def norm_preferred_ports(self, preferred_ports: Union[None, PortProps, str, int, Tuple, List]) -> List[PortProps]:
        if preferred_ports is None:
            return []
        elif isinstance(preferred_ports, PortProps):
            return [preferred_ports]
        elif isinstance(preferred_ports, str):
            return [PortProps(preferred_ports)]
        elif isinstance(preferred_ports, int):
            return [PortProps(str(preferred_ports))]
        elif isinstance(preferred_ports, tuple):
            return [PortProps(*preferred_ports)]
        elif isinstance(preferred_ports, list):
            # Flatten the list by iterating over each item
            result = []
            for p in preferred_ports:
                result.extend(self.norm_preferred_ports(p))  # Use extend to avoid nested lists
            return result
        else:
            return [PortProps(preferred_ports)]


    def calculate_geometry_area(self, polyline_coordinates):
        """
        Calculate the area of a polygon defined by a set of coordinates using the shoelace formula.
    
        Parameters:
        - polyline_coordinates (list): List of coordinates defining the polygon.
    
        Returns:
        - float: The calculated area in square units.
        """
    
        # Ensure the polyline is closed to form a polygon
        if polyline_coordinates[0] != polyline_coordinates[-1]:
            polyline_coordinates.append(polyline_coordinates[0])
    
        # Calculate the area using the shoelace formula
        n = len(polyline_coordinates)
        area = 0.5 * sum(
            (polyline_coordinates[i][0] * polyline_coordinates[i + 1][1] -
             polyline_coordinates[i + 1][0] * polyline_coordinates[i][1])
            for i in range(n - 1)
        )
    
        # Return the absolute value of the calculated area
        return abs(area)
        

    def contains(self, x: float, y: float) -> bool:
        # will ignore other group of coordinates
        # assuming a closed and solid polygon
        poly = self.geometry.coordinates[0]
        n = len(poly)
        vx, vy  = list(zip(*poly))
        return pnpoly(n, vx, vy, x, y) 
        
import searoute as sr
from copy import copy

from searoute.classes.passages import Passage
import geojson

def get_middle_element(lst):
    length = len(lst)
    middle_index = length // 2  # Integer division
    
    if length % 2 == 0:
        # Even length: return the element just before the middle
        return lst[middle_index]
    else:
        # Odd length: return the middle element
        return lst[middle_index]
    
# Function to find edges with a specific attribute value
def find_edges_by_attribute(G, passage_values):
    passage_list = {key: [] for key in passage_values}

    for u, v, attr in G.edges(data=True):
        for attr_value in passage_values:
            if attr.get('passage') == attr_value:
                passage_list[attr_value].append((u, v))
    return passage_list


def append_features(features):
    """
    Appends a list of GeoJSON features into a single FeatureCollection.

    Parameters:
    - features (List[geojson.Feature]): A list of GeoJSON features to be appended.

    Returns:
    - geojson.FeatureCollection: A GeoJSON FeatureCollection containing all features.
    """
    # Create a FeatureCollection with the list of features
    feature_collection = geojson.FeatureCollection(features)
    
    return feature_collection

def get_features_with_stops( origin, dest, mandatory_passages):
    M:sr.Marnet = copy(sr.setup_M())

    passage_pts = find_edges_by_attribute(M, mandatory_passages)
    lst = []
    for key, value in passage_pts.items():
        mid_pt = get_middle_element(value)
        # get second point of found passage
        yp,xp = mid_pt[1]
        lst.append(((yp,xp), key))

    fts = []
    step = origin
    #add last position
    lst.append((dest, None))
    for stop in lst:
        stop_i = stop[0]
        traj = sr.searoute(step, stop_i, append_orig_dest=True, return_passages=True)
        fts.append(traj)
        step = stop_i

    return fts


def test_mandatory_passage():
    origin = [-61.87, 17.15]# barbuda 
    dest =   [52.99, 25.01] # dubai
    # barbuda to dubai
    mandatory_passages = [ Passage.panama,Passage.chili, Passage.south_africa, Passage.gibraltar, Passage.suez]
    # the way around dubai to barbuda
    #mandatory_passages = [  Passage.suez,  Passage.gibraltar, Passage.south_africa, Passage.chili,Passage.panama]

   
    fts = get_features_with_stops(origin, dest, mandatory_passages)
    print(append_features(fts))

    traversed_passages = []
    for ft in fts:
        passed = ft['properties']['traversed_passages']
        traversed_passages.extend(passed)

    traversed_passages = set(traversed_passages)

    assert all(element in traversed_passages for element in mandatory_passages)


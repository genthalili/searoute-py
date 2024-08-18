import searoute as sr

def test_passages():
    traj = sr.searoute([52.99, 25.01], [-61.87, 17.15], append_orig_dest=True, restrictions=['northwest', 'chili'], return_passages=True)
    result_expected = ['suez', 'ormuz', 'babalmandab', 'gibraltar'] 
    true_result = traj['properties']['traversed_passages']
    assert sorted(result_expected)==sorted(true_result)

def test_restriction_passage():
    traj = sr.searoute([52.99, 25.01], [-61.87, 17.15], append_orig_dest=True, restrictions=['suez'], return_passages=True)
    result_expected = [ 'ormuz', 'south_africa'] 
    true_result = traj['properties']['traversed_passages']
    assert sorted(result_expected)==sorted(true_result)


def test_rev_lat_lon_passages():

    traj = sr.searoute([140.02, 35.51], [-97.36, 27.81], append_orig_dest=True, return_passages=True)
    true_result = traj['properties']['traversed_passages']
    assert ['panama'] == true_result



    
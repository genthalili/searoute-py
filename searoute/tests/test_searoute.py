import searoute as sr


def test_passages():
    traj = sr.searoute([52.99, 25.01], [-61.87, 17.15], append_orig_dest=True, restrictions=['northwest', 'chili'], return_passages=True)
    result_expected = ['suez', 'ormuz', 'babalmandab', 'gibraltar'] 
    true_result = traj['properties']['traversed_passages']
    assert sorted(result_expected)==sorted(true_result)
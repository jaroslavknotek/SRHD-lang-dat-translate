import numbers

import utils


def test_apply_dict():

    inner_dict = {"num_2_1": 3, "str_2_1": "y"}
    data = {
        "dict_1": {"num_1_1": 1, "str_1_1": "x"},
        "arr": [inner_dict, "str", 22],
        "num": 0,
    }

    def add(x):
        if isinstance(x, str):
            return x + "1"
        if isinstance(x, numbers.Number):
            return x + 1
        return x

    res_data = utils.apply_on_dict_scalars(data, add)
    assert 1 == res_data["num"]

    assert "dict_1" in res_data
    res_dict_1 = res_data["dict_1"]
    assert 2 == res_dict_1["num_1_1"]
    assert "x1" == res_dict_1["str_1_1"]

    assert "arr" in res_data
    res_arr = res_data["arr"]
    assert 3 == len(res_arr)

    assert 4 == res_arr[0]["num_2_1"]
    assert "y1" == res_arr[0]["str_2_1"]

    assert "str1" == res_arr[1]
    assert 23 == res_arr[2]


def test_count_dict_elements():

    assert 0 == utils.count_dict_scalars({})
    assert 100 == utils.count_dict_scalars({"r": list(range(100))})

    assert 0 == utils.count_dict_scalars({"x": {}})

def apply_on_dict_scalars(element, apply_func):
    if isinstance(element, dict):
        fn_pairs = [
            (k, apply_on_dict_scalars(v, apply_func)) for k, v in element.items()
        ]
        return dict(fn_pairs)
    elif isinstance(element, list):
        return [apply_on_dict_scalars(v, apply_func) for v in element]
    elif element is not None:
        # assuming it's a scalar
        return apply_func(element)


class Counter:
    def __init__(self):
        self.count = 0

    def __call__(self, el):
        self.count += 1


def count_dict_scalars(d):
    counter = Counter()
    apply_on_dict_scalars(d, counter)
    return counter.count

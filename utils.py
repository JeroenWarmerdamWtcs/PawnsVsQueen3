def create_list(size, value):
    result = [value] * size
    return [result]


def create_matrix(size, value):
    result = []
    for _ in size:
        result.append(create_list(size, value))
    return result

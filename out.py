def witness_harmony(path):
    def compare(path, reflection):
        if not path and not reflection:
            return True
        elif not path or not reflection:
            return False
        elif path[0] == reflection[-1]:
            return compare(path[1:], reflection[:-1])
        else:
            return False

    def reflect(path):
        return path[::-1]

    def first_of(path):
        return path[0]

    def last_of(path):
        return path[-1]

    def rest_of(path):
        return path[1:]

    def beginning_of(path):
        return path[:-1]

    reflection = reflect(path)
    return compare(path, reflection)

unrest = [1, 2, 3, 4]
result = witness_harmony(unrest)
print(result)
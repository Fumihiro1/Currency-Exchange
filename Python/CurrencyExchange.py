from py_exchangeratesapi import Api

api = Api('32079035db98992849d78653cbdeadba')

api.get_rates()

print(api.get_rate(target='GBP'))

class Edge:
    def __init__(self, start, destination, weight):
        self.start = start
        self.destination = destination
        self.weight = weight

class Graph:
    def __init__(self, no_vertices, edges):
        self.noVertices = no_vertices
        self.edges = edges

def input_type():
    print('1. APi')
    print('2. Custom')
    type = input();

    if input == 1:
        print('API chosen')
        return input;
    elif input == 2:
        print('Custom chosen')
        return input;
    else:
        print('Try again')
        return inputType()

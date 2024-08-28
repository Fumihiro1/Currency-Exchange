import numpy as np
from py_exchangeratesapi import Api

api = Api('32079035db98992849d78653cbdeadba')

api.get_rates()

#print(api.get_rate(target='GBP'))

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
    print('1. API')
    print('2. Custom')
    type = input()

    if input == 1:
        print('API chosen')
        return input
    elif input == 2:
        print('Custom chosen')
        return input
    else:
        print('Try again')
        return inputType()


# Hard coded arbitrage list
edges = []

edges.append(Edge('USD', 'EUR', 0.85))
edges.append(Edge('USD', 'GBP', 0.75))
edges.append(Edge('USD', 'JPY', 110))
edges.append(Edge('USD', 'AUD', 1.35))

edges.append(Edge('EUR', 'USD', 1.18))
edges.append(Edge('EUR', 'GBP', 0.88))
edges.append(Edge('EUR', 'JPY', 129.53))
edges.append(Edge('EUR', 'AUD', 1.59))

edges.append(Edge('GBP', 'USD', 1.33))
edges.append(Edge('GBP', 'EUR', 1.14))
edges.append(Edge('GBP', 'JPY', 147.05))
edges.append(Edge('GBP', 'AUD', 1.81))

edges.append(Edge('JPY', 'USD', 0.0091))
edges.append(Edge('JPY', 'EUR', 0.0077))
edges.append(Edge('JPY', 'GBP', 0.0068))
edges.append(Edge('JPY', 'AUD', 0.012))

edges.append(Edge('AUD', 'USD', 0.74))
edges.append(Edge('AUD', 'EUR', 0.63))
edges.append(Edge('AUD', 'GBP', 0.55))
edges.append(Edge('AUD', 'JPY', 83.33))

graph = Graph(5, edges)


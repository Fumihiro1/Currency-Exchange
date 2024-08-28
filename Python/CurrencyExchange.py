#from py_exchangeratesapi import Api

#api = Api('32079035db98992849d78653cbdeadba')

#api.get_rates()

#print(api.get_rate(target=3))
import requests

from_currency = str(
    input("Enter in the currency you'd like to convert from: ")).upper()

to_currency = str(
    input("Enter in the currency you'd like to convert to: ")).upper()

amount = float(input("Enter in the amount of money: "))

response = requests.get(
    f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}")

print(
    f"{amount} {from_currency} is {response.json()['rates'][to_currency]} {to_currency}")

class Edge:
    def __init__(self, start, destination, weight):
        self.start = start
        self.destination = destination
        self.weight = weight

class Graph:
    def __init__(self, no_vertices):
        self.no_vertices = no_vertices
        self.edges = []

    def add_edge(self, start, destination, weight):
        self.edges.append((start, destination, weight))

    def bellman_ford(self, src):
        # Initialize distances
        d = [float("Inf")] * (self.no_vertices + 1)  # starting from 1
        d[src] = 0

        # Repeat |V| - 1 times
        for _ in range(self.no_vertices - 1):
            for start, destination, weight in self.edges:
                if d[start] != float("Inf") and d[start] + weight < d[destination]:
                    d[destination] = d[start] + weight

        # Check for negative-weight cycles
        for start, destination, weight in self.edges:
            if d[start] != float("Inf") and d[start] + weight < d[destination]:
                print("Graph contains a negative weight cycle")
                return  # If a cycle is found, stop the function
        print("No Negative Cycle found")

        # Print distances
        self.print_distances(d)

    def print_distances(self, dist):
        print("Vertex Distance from Source")
        for i in range(1, len(dist)):  # Start from 1
            print("{0}\t\t{1}".format(i, dist[i]))

def input_type():
    print('1. API')
    print('2. Custom')
    type = input()

    if type == 1:
        print('API chosen')
        return input
    elif type == 2:
        print('Custom chosen')
        return input
    else:
        print('Try again')
        return input_type()

# Hard coded arbitrage list
graph = Graph(5)

graph.add_edge(1, 2, 0.85)
graph.add_edge(1, 3, 0.75)
graph.add_edge(1, 4, 110)
graph.add_edge(1, 5, 1.35)

graph.add_edge(2, 1, 1.18)
graph.add_edge(2, 3, 0.88)
graph.add_edge(2, 4, 129.53)
graph.add_edge(2, 5, 1.59)

graph.add_edge(3, 1, 1.33)
graph.add_edge(3, 2, 1.14)
graph.add_edge(3, 4, 147.05)
graph.add_edge(3, 5, 1.81)

graph.add_edge(4, 1, 0.0091)
graph.add_edge(4, 2, 0.0077)
graph.add_edge(4, 3, 0.0068)
graph.add_edge(4, 5, 0.012)

graph.add_edge(5, 1, 0.74)
graph.add_edge(5, 2, 0.63)
graph.add_edge(5, 3, 0.55)
graph.add_edge(5, 4, 83.33)


graph2 = Graph(6)
graph2.add_edge(1, 2, 5)
graph2.add_edge(2, 3, 1)
graph2.add_edge(3, 4, 2)
graph2.add_edge(3, 5, -4)
graph2.add_edge(3, 6, 5)
graph2.add_edge(4, 1, -2)
graph2.add_edge(4, 2, -2)
graph2.add_edge(5, 4, 4)
graph2.add_edge(6, 5, 5)

print('GRAPH 1')
graph.bellman_ford(1)

print('GRAPH 2')
graph2.bellman_ford(1)
        return inputType()
    
   

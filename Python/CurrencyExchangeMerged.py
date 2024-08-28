import math
import requests


# Graphs
class Edge:
    def __init__(self, start, destination, weight):
        self.start = start
        self.destination = destination
        self.weight = weight

class Graph:
    def __init__(self, no_vertices):
        self.no_vertices = no_vertices
        self.edges = []

    # Add edge
    def add_edge(self, start, destination, weight):
        self.edges.append(Edge(start,destination,weight))

    def bellman_ford(self, source):                  # Bellman-Ford Algorithm
        distance = [float("Inf")] * self.no_vertices # Start with distances as infinity
        predecessor = [-1] * self.no_vertices        # Predecessor array to store path
        distance[source] = 0                         # distance to source node is always 0

        # Relaxation Process
        for _ in range(self.noVertices - 1): # Iterate n-1 times
            for edge in self.edges: # For each edge in the graph
                # If the start node has been reached before, and the path through the edge is a shorter path
                if distance[edge.start] != float('inf') and distance[edge.start] + edge.weight < distance[edge.destination]:
                    distance[edge.destination] = distance[edge.start] + edge.weight # Update the shortest path found
                    predecessor[edge.destination] = edge.start

        # After n-1 iterations, if you can still find a shorter path, there is a negative cycle
        for edge in self.edges: # For each edge
            if distance[edge.start] + edge.weight < distance[edge.destination]: # If there is a shorter path
                # Return that there is a negative cycle, and where the cycle is
                return True, self.get_negative_cycle(predecessor, edge.destination)

        # Find where the negative cycle is
        def get_negative_cycle(predecessor, start):
            cycle = [] # The nodes that are in the negative cycle
            visited = set() # Keep track of visited Node
            node = start # Set the current node to the start

            # Trace the node backwards through the predecessor array
            while node not in visited: # Loops until all nodes are visited
                visited.add(node) # Add the node to visited Node
                node = predecessor[node] # Move to the predecessor of the current node

            cycle_start = node # The first node that was revisited
            cycle.append(cycle_start) # Add the first node to the cycle
            node = predecessor[cycle_start] # Move to the predecessor of the cycle start

            # Adds all the nodes to the cycle
            while node != cycle_start: # While the cycle is incomplete
                cycle.append(node)  # Add to cycle
                node = predecessor[node] # go to predecessor

            cycle.append(cycle_start) # Complete the cycle
            cycle.reverse() # Since the cycle is backwards, reverse it
            return cycle

# API
def fetch_exchange_rates(currencies):
    # Fetch the latest exchange rates for the specified currencies using get
    response = requests.get(f"https://api.exchangerate-api.com/v4/latest/USD")
    rates = response.json().get('rates', {}) # Returns the rates, or an empty dictionary if the rates field is missing

    # Creates and returns a matrix of the currency rates from the requested currencies
    matrix = [[1 if i == j else rates[currencies[j]] / rates[currencies[i]] for j in range(len(currencies))] for i in range(len(currencies))]
    return matrix

def get_exchange_rates_from_input():
    currencies = input('Enter currencies (comma-separated): ').split(',')
    n = len(currencies)
    matrix = []

    print('Enter exchange rates row by row (space-separated):')
    for _ in range(n):
        row = list(map(float, input().split()))
        matrix.append(row)

    return currencies, matrix
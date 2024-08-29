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
        self.arbitrages = []

    # Add edge
    def add_edge(self, start, destination, weight):
        self.edges.append(Edge(start, destination, weight))
        print(f"Added edge: {start} -> {destination} with weight {weight}")

    def bellman_ford(self, source):  # Bellman-Ford Algorithm
        distance = [float("Inf")] * self.no_vertices  # Start with distances as infinity
        predecessor = [-1] * self.no_vertices  # Predecessor array to store path
        distance[source] = 0  # Distance to source node is always 0

        print(f"Initial distances: {distance}")
        print(f"Initial predecessors: {predecessor}")

        # Relaxation Process
        for _ in range(self.no_vertices - 1):  # Iterate n-1 times
            print(f"Iteration {_ + 1}:")
            for edge in self.edges:  # For each edge in the graph
                if distance[edge.start] != float('inf') and distance[edge.start] + edge.weight < distance[
                    edge.destination]:
                    distance[edge.destination] = distance[edge.start] + edge.weight  # Update the shortest path found
                    predecessor[edge.destination] = edge.start
                    print(f"Updated distance for node {edge.destination} to {distance[edge.destination]}")
                    print(f"Updated predecessor for node {edge.destination} to {predecessor[edge.destination]}")

        # Check for negative cycles after n-1 iterations
        found_cycles = False
        print("Checking for negative cycles...")
        for edge in self.edges:  # For each edge
            if distance[edge.start] + edge.weight < distance[edge.destination]:  # If there is a shorter path
                print(f"Negative cycle detected involving edge: {edge.start} -> {edge.destination}")
                cycle = get_negative_cycle(predecessor, edge.destination)
                if cycle not in self.arbitrages:  # To avoid duplicates
                    self.arbitrages.append(cycle)
                    found_cycles = True

        return found_cycles


# Find where the negative cycle is
def get_negative_cycle(predecessor, start):
    cycle = []  # The nodes that are in the negative cycle
    visited = set()  # Keep track of visited Node
    node = start  # Set the current node to the start

    print(f"Tracing negative cycle starting at node {start}")

    # Trace the node backwards through the predecessor array
    while node not in visited:  # Loops until all nodes are visited
        visited.add(node)  # Add the node to visited Node
        node = predecessor[node]  # Move to the predecessor of the current node

    cycle_start = node  # The first node that was revisited
    cycle.append(cycle_start)  # Add the first node to the cycle
    node = predecessor[cycle_start]  # Move to the predecessor of the cycle start

    # Adds all the nodes to the cycle
    while node != cycle_start:  # While the cycle is incomplete
        cycle.append(node)  # Add to cycle
        node = predecessor[node]  # go to predecessor

    cycle.append(cycle_start)  # Complete the cycle
    cycle.reverse()  # Since the cycle is backwards, reverse it
    print(f"Negative cycle detected: {cycle}")
    return cycle


# API
def fetch_exchange_rates(currencies):
    response = requests.get(f"https://api.exchangerate-api.com/v4/latest/USD")
    rates = response.json().get('rates', {})

    # Creates and returns a matrix of the currency rates from the requested currencies
    matrix = [[1 if i == j else rates[currencies[j]] / rates[currencies[i]] for j in range(len(currencies))] for i in
              range(len(currencies))]
    print(f"Fetched exchange rates: {rates}")
    print("Exchange Rate Matrix:")
    for row in matrix:
        print(" ".join(f"{rate:.4f}" for rate in row))
    return matrix


# Get exchange rates from user input
def get_exchange_rates_from_input():
    currencies = input('Enter currencies (comma-separated)').split(',')
    n = len(currencies)  # Number of currencies for 'n'

    matrix = []
    print('Enter exchange rates row by row (space-separated):')
    for _ in range(n):
        row = list(map(float, input().split()))
        matrix.append(row)

    print(f"User-entered currencies: {currencies}")
    print(f"User-entered exchange rate matrix: {matrix}")
    return currencies, matrix


# Create a graph from a matrix and list of currencies
def build_graph(currencies, matrix):
    n = len(currencies)
    graph = Graph(n)

    # Fill the graph with the matrix values
    for i in range(n):
        for j in range(n):
            if i != j:
                rate = matrix[i][j]
                weight = -math.log10(rate)  # using the negative logarithm
                graph.add_edge(i, j, weight)

    return graph


# Runs the arbitrage program
def find_arbitrage(graph, currencies):
    print("Detecting arbitrage opportunities...")
    arbitrage_exists = graph.bellman_ford(0)
    if arbitrage_exists:
        arbitrage_string = ''
        for arbitrage in graph.arbitrages:
            arbitrage_string += ' -> '.join(str(item) for item in arbitrage)
            arbitrage_string += '\n'
        print("Arbitrage detected! Currency sequence:\n" + arbitrage_string)
    else:
        print("No arbitrage opportunities found.")


# Get the input type
def input_type():
    print('Input type?')
    print('1. API')
    print('2. Custom')
    choice = input('Choose input type (1 or 2): ')

    if choice == '1':
        print('API chosen')
        return 'API'
    elif choice == '2':
        print('Custom chosen')
        return 'Custom'
    else:
        print('Invalid choice. Try again.')
        return input_type()


def main():
    input_choice = input_type()

    if input_choice == 'API':
        currencies = [currency.strip() for currency in input("Enter currencies (comma-separated): ").split(',')]
        matrix = fetch_exchange_rates(currencies)
    else:
        currencies, matrix = get_exchange_rates_from_input()

    graph = build_graph(currencies, matrix)  # Build graph

    print('Detecting arbitrage opportunities...')
    find_arbitrage(graph, currencies)  # Run arbitrage program


if __name__ == '__main__':
    main()

import math
from py_exchangeratesapi import Api

class Edge:
    def __init__(self, start, destination, weight):
        self.start = start
        self.destination = destination
        self.weight = weight

class Graph:
    def __init__(self, noVertices):
        self.noVertices = noVertices
        self.edges = []

    def add_edge(self, start, destination, weight):
        self.edges.append(Edge(start, destination, weight))

    def bellman_ford(self, source):
        # initialise stuff
        distance = [float('inf')] * self.noVertices # start with all distances as infinity
        predecessor = [-1] * self.noVertices # Predecessor array to store path
        distance[source] = 0 # distance to source is 0

        for _ in range(self.noVertices - 1):
            for edge in self.edges:
                # if distance to start node is not infinite and shorter path is found
                if distance[edge.start] != float('inf') and distance[edge.start] + edge.weight < distance[edge.destination]:
                    distance[edge.destination] = distance[edge.start] + edge.weight
                    predecessor[edge.destination] = edge.start

        # Check for negative weight cycle
        for edge in self.edges:
            # if shorter path is still found there is a negative weight cycle
            if distance[edge.start] + edge.weight < distance[edge.destination]:
                # There is a negative cycle
                return True, self.get_negative_cycle(predecessor, edge.destination)
        return False, distance

    def get_negative_cycle(self, predecessor, start):
        # find negative cycle using predecessor array
        cycle = []
        visited = set()
        node = start

        # go back in predecessor array to find start of cycle
        while node not in visited:
            visited.add(node)
            node = predecessor[node]

        cycle_start = node
        cycle.append(cycle_start)
        node = predecessor[cycle_start]

        while node != cycle_start:
            cycle.append(node)
            node = predecessor[node]
        cycle.append(cycle_start)

        cycle.reverse()
        return cycle

def inputType():
    print('1. API (doesnt work)')
    print('2. Custom')
    choice = input('Choose input type (1 or 2): ')

    if choice == '1':
        print('API chosen (API does not work haha xd)')
        return 'API'
    elif choice == '2':
        print('Custom chosen')
        return 'Custom'
    else:
        print('Invalid choice. Try again.')
        return inputType()

def fetch_exchange_rates(api_key):
    api = Api(api_key)
    rates = api.get_rates()
    currencies = list(rates.keys())
    matrix = [[1 if i == j else rates[currencies[j]] / rates[currencies[i]] for j in range(len(currencies))] for i in range(len(currencies))]
    return currencies, matrix

def get_exchange_rates_from_input():
    currencies = input('Enter currencies (comma-separated): ').split(',')
    n = len(currencies)
    matrix = []

    print('Enter exchange rates row by row (space-separated):')
    for _ in range(n):
        row = list(map(float, input().split()))
        matrix.append(row)

    return currencies, matrix

def build_graph(currencies, matrix):
    n = len(currencies)
    graph = Graph(n)

    for i in range(n):
        for j in range(n):
            if i != j:
                rate = matrix[i][j]
                weight = -math.log10(rate)
                graph.add_edge(i, j, weight)

    return graph

def find_arbitrage(graph, currencies):
    arbitrage_exists, result = graph.bellman_ford(0)
    if arbitrage_exists:
        print("Arbitrage detected! Currency sequence: " + " -> ".join(currencies[i] for i in result))
    else:
        print("No arbitrage opportunities found.")

def find_best_conversion_rate(graph, currencies, source, target):
    source_index = currencies.index(source)
    target_index = currencies.index(target)
    _, distances = graph.bellman_ford(source_index)

    best_rate = math.pow(10, -distances[target_index])
    print(f"Best conversion rate from {source} to {target}: {best_rate}")

def main():
    input_choice = inputType()
    currencies = []
    matrix = []

    if input_choice == 'API':
        api_key = input('Enter your API key: ')
        currencies, matrix = fetch_exchange_rates(api_key)
    else:
        currencies, matrix = get_exchange_rates_from_input()

    graph = build_graph(currencies, matrix)

    print('1. Detect arbitrage opportunities')
    print('2. Find best conversion rate')
    choice = input('Choose task (1 or 2): ')

    if choice == '1':
        find_arbitrage(graph, currencies)
    elif choice == '2':
        source = input('Enter source currency: ')
        target = input('Enter target currency: ')
        find_best_conversion_rate(graph, currencies, source, target)
    else:
        print('Invalid choice.')

if __name__ == '__main__':
    main()

import math
import requests

class Edge:
    def __init__(self, start, destination, weight):
        self.start = start
        self.destination = destination
        self.weight = weight

class Graph:
    def __init__(self, no_vertices):
        self.noVertices = no_vertices
        self.edges = []

    def add_edge(self, start, destination, weight):
        self.edges.append(Edge(start, destination, weight))

    def bellman_ford(self, source, tolerance=1e-5):
        # Initialize distances and predecessors
        distance = [float('inf')] * self.noVertices
        predecessor = [-1] * self.noVertices
        distance[source] = 0

        for _ in range(self.noVertices - 1):
            for edge in self.edges:
                if distance[edge.start] != float('inf') and distance[edge.start] + edge.weight < distance[
                    edge.destination]:
                    distance[edge.destination] = distance[edge.start] + edge.weight
                    predecessor[edge.destination] = edge.start

        # Check for negative weight cycles
        for edge in self.edges:
            if distance[edge.start] + edge.weight < distance[edge.destination]:
                cycle = self.get_negative_cycle(predecessor, edge.destination)
                cycle_product = 1.0
                for i in range(len(cycle) - 1):
                    cycle_product *= 10 ** (-self.edges[i].weight)
                if cycle_product > 1 + tolerance:
                    return True, cycle

        return False, distance

    @staticmethod
    def get_negative_cycle(predecessor, start):
        # Find negative cycle using predecessor array
        cycle = []
        visited = set()
        node = start

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

def input_type():
    print('1. API')
    print('2. Custom')
    choice = input('Choose input type (1 or 2): ')

    if choice == '1':
        return 'API'
    elif choice == '2':
        return 'Custom'
    else:
        print('Invalid choice. Try again.')
        return input_type()

def fetch_exchange_rates(currencies):
    rates = {}
    try:
        for currency in currencies:
            response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{currency.strip()}")
            response.raise_for_status()  # Check for request errors
            rates[currency] = response.json().get('rates', {})
    except requests.exceptions.RequestException as e:
        print(f"Error fetching exchange rates: {e}")
        return None

    n = len(currencies)
    matrix = [[0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 1.0
            else:
                matrix[i][j] = rates[currencies[i]].get(currencies[j], None)

    return matrix

def get_exchange_rates_from_input():
    currencies = [currency.strip().upper() for currency in input('Enter currencies (comma-separated): ').split(',')]
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

def find_arbitrage_or_best_rate(graph, currencies):
    currencies = [currency.upper() for currency in currencies]
    arbitrage_exists, result = graph.bellman_ford(0)
    if arbitrage_exists:
        print("Arbitrage detected! Currency sequence: " + " -> ".join(currencies[i] for i in result))
    else:
        print("No arbitrage opportunities found.")
        source = input('Enter source currency: ').strip().upper()
        target = input('Enter target currency: ').strip().upper()
        if source in currencies and target in currencies:
            find_best_conversion_rate(graph, currencies, source, target)
        else:
            print('Invalid currencies entered. Please try again.')

def find_best_conversion_rate(graph, currencies, source, target):
    source_index = currencies.index(source)
    target_index = currencies.index(target)
    _, (distances, predecessors) = graph.bellman_ford(source_index)

    if distances[target_index] == float('inf'):
        print(f"No conversion path found from {source} to {target}.")
    else:
        best_rate = math.pow(10, -distances[target_index])
        path = get_path(predecessors, source_index, target_index)
        print(f"Best conversion rate from {source} to {target}: {best_rate:.6f}")
        print("Conversion path:", " -> ".join(currencies[i] for i in path))

def get_path(predecessor, start, end):
    path = []
    current = end

    while current != start:
        path.append(current)
        current = predecessor[current]
        if current == -1:
            return None  # Path not found

    path.append(start)
    path.reverse()
    return path

def main():
    while True:
        input_choice = input_type()

        if input_choice == 'API':
            currencies = [currency.strip().upper() for currency in input("Enter currencies (comma-separated): ").split(',')]
            matrix = fetch_exchange_rates(currencies)
            if matrix is None:
                print("Failed to fetch exchange rates. Exiting.")
                continue

            print("Exchange Rate Matrix:")
            for row in matrix:
                print(" ".join(f"{rate:.4f}" if rate is not None else "None" for rate in row))
        else:
            currencies, matrix = get_exchange_rates_from_input()

        graph = build_graph(currencies, matrix)
        find_arbitrage_or_best_rate(graph, currencies)

        replay = input('Do you want to try again? (yes or no): ')
        if replay.lower() != 'yes':
            print("Goodbye!")
            break

if __name__ == '__main__':
    main()

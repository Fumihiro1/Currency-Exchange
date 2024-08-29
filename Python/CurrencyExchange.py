import math
import requests
from decimal import Decimal, getcontext

# Set precision for Decimal operations
getcontext().prec = 50


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

    def bellman_ford(self, source, tolerance=Decimal('1e-15')):
        # Initialize distances and predecessors
        distance = [Decimal('inf')] * self.noVertices
        predecessor = [-1] * self.noVertices
        distance[source] = Decimal('0')

        for _ in range(self.noVertices - 1):
            for edge in self.edges:
                if distance[edge.start] != Decimal('inf') and distance[edge.start] + edge.weight < distance[
                    edge.destination]:
                    distance[edge.destination] = distance[edge.start] + edge.weight
                    predecessor[edge.destination] = edge.start

        # Check for negative weight cycles and find all arbitrages
        arbitrages = []
        seen_cycles = set()  # Set to store unique cycles

        for edge in self.edges:
            if distance[edge.start] + edge.weight < distance[edge.destination]:
                cycle = self.get_negative_cycle(predecessor, edge.destination)

                # Normalize cycle by sorting to avoid duplicates
                normalized_cycle = tuple(sorted(cycle))

                # Check if we already found this cycle
                if normalized_cycle not in seen_cycles:
                    seen_cycles.add(normalized_cycle)
                    cycle_product = Decimal('1.0')
                    for i in range(len(cycle) - 1):
                        start_currency = cycle[i]
                        next_currency = cycle[i + 1]
                        for e in self.edges:
                            if e.start == start_currency and e.destination == next_currency:
                                cycle_product *= Decimal(10) ** (-e.weight)
                                break
                    if cycle_product > 1 + tolerance:
                        arbitrages.append((cycle, cycle_product))

        if arbitrages:
            return True, arbitrages
        else:
            return False, (distance, predecessor)

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
    matrix = [[Decimal(0)] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = Decimal(1.0)
            else:
                rate = rates[currencies[i]].get(currencies[j], None)
                if rate is not None:
                    matrix[i][j] = Decimal(rate)

    return matrix


def get_exchange_rates_from_input():
    currencies = [currency.strip().upper() for currency in input('Enter currencies (comma-separated): ').split(',')]
    n = len(currencies)
    matrix = []

    print('Enter exchange rates row by row (space-separated):')
    for _ in range(n):
        row = list(map(Decimal, input().split()))
        matrix.append(row)

    return currencies, matrix


def build_graph(currencies, matrix):
    n = len(currencies)
    graph = Graph(n)

    for i in range(n):
        for j in range(n):
            if i != j:
                rate = matrix[i][j]
                weight = -Decimal(math.log10(rate))
                graph.add_edge(i, j, weight)

    return graph


def find_arbitrage_or_best_rate(graph, currencies):
    """
    Detects arbitrage opportunities or finds the best conversion rates for all currency pairs.
    """
    currencies = [currency.upper() for currency in currencies]
    arbitrage_exists, result = graph.bellman_ford(0)

    if arbitrage_exists:
        for cycle, gain in result:
            print("Arbitrage detected! Currency sequence: " + " -> ".join(currencies[i] for i in cycle))
            print(f"Potential gain from this arbitrage: {(gain - 1) * 100:.15f}%")
    else:
        print("No arbitrage opportunities found.")
        # Automatically find the best conversion rates for all pairs
        find_best_conversion_rates(graph, currencies, result)


def find_best_conversion_rates(graph, currencies, bellman_ford_result):
    """
    Finds and prints the best conversion rates for all currency pairs.
    """
    distances, predecessors = bellman_ford_result
    n = len(currencies)

    # Loop through each currency as the source
    for i in range(n):
        source = currencies[i]

        # For each source, loop through all other currencies as the target
        for j in range(n):
            if i != j:
                target = currencies[j]
                if distances[j] == Decimal('inf'):
                    print(f"No conversion path found from {source} to {target}.")
                else:
                    best_rate = Decimal(10) ** -distances[j]
                    path = get_path(predecessors, i, j)
                    print(f"Best conversion rate from {source} to {target}: {best_rate:.15f}")
                    print("Conversion path:", " -> ".join(currencies[k] for k in path))


def get_path(predecessor, start, end):
    """
    Reconstructs the path from `start` to `end` using the `predecessor` array.
    """
    path = []
    current = end

    # Avoid infinite loops by keeping track of visited nodes
    visited = set()

    while current != start:
        if current == -1 or current in visited:  # No path exists or a cycle detected
            return []
        visited.add(current)
        path.append(current)
        current = predecessor[current]

    # Append the start node and reverse the path
    path.append(start)
    path.reverse()
    return path

def main():
    while True:
        input_choice = input_type()

        if input_choice == 'API':
            currencies = [currency.strip().upper() for currency in
                          input("Enter currencies (comma-separated): ").split(',')]
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

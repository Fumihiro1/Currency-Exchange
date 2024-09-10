import math
import tkinter as tk


class Exchange:
    def __init__(self):
        self.cycle = ""
        self.arbitrage_info = ""


class BellmanFord:
    INF = float('inf')

    def __init__(self, ex):
        self.ex = ex

    def find_arbitrage_and_shortest_path(self, edges, rates, start_currency, end_currency):
        # Extract all unique nodes
        nodes = set(u for u, _, _ in edges).union(v for _, v, _ in edges)
        distance = {node: self.INF for node in nodes}
        predecessor = {node: None for node in nodes}
        distance[start_currency] = 0

        # Relax all edges |V| - 1 times
        for _ in range(len(nodes) - 1):
            for u, v, w in edges:
                if round(distance[u] + w, 3) < round(distance[v], 3):
                    distance[v] = round(distance[u] + w, 3)
                    predecessor[v] = u

        # Check for negative weight cycles
        arbitrage_found = False
        cycle_start = None

        for u, v, w in edges:
            if round(distance[u] + w, 3) < round(distance[v], 3):
                arbitrage_found = True
                cycle_start = v
                break

        if arbitrage_found:
            # If there is an arbitrage, trace the path using predecessors
            cycle = []
            current = cycle_start

            # Find the cycle starting point
            for _ in range(len(nodes)):
                current = predecessor[current]

            cycle_start = current

            # Trace back to find the complete cycle
            while True:
                cycle.append(current)
                current = predecessor[current]
                if current == cycle_start:
                    cycle.append(current)
                    break
            cycle.reverse()

            # Calculate the gain product
            gain_product = 1.0
            for i in range(len(cycle) - 1):
                from_currency = cycle[i]
                to_currency = cycle[i + 1]
                rate = rates.get(from_currency, {}).get(to_currency, 'N/A')
                if rate != 'N/A':
                    gain_product *= round(float(rate), 3)

            # Check if the gain product exceeds the threshold
            path = ' -> '.join(cycle)
            self.ex.arbitrage_info = (f"Arbitrage opportunity found: {path}\n"
                                          f"Potential gain: {(gain_product - 1) * 100:.2f}%")
        else:
            self.ex.arbitrage_info = "No arbitrage opportunity detected. Returning shortest path"

        # Find the shortest path from start_currency to end_currency
        shortest_path = self._reconstruct_path(predecessor, start_currency, end_currency)
        if shortest_path:
            path_str = ' -> '.join(shortest_path)
            self.ex.path_info = f"Shortest path from {start_currency} to {end_currency}: {path_str}"
        else:
            self.ex.path_info = "No path found."

    def _reconstruct_path(self, predecessor, start_currency, end_currency):
        path = []
        current = end_currency
        while current is not None:
            path.append(current)
            current = predecessor[current]
        path.reverse()
        if path[0] == start_currency:
            return path
        return []


# Example usage:
if __name__ == "__main__":
    ex = Exchange()

    # Define a list of edges and a rates dictionary
    edges = [
        ('USD', 'EUR', -math.log(0.85)),
        ('EUR', 'JPY', -math.log(130.0)),
        ('JPY', 'USD', -math.log(0.0075))
    ]

    rates = {
        'USD': {'EUR': '0.85'},
        'EUR': {'JPY': '130.0'},
        'JPY': {'USD': '0.0075'}
    }

    # Dropdown selections for currencies
    selected_currency_1 = 'USD'
    selected_currency_2 = 'JPY'

    bellman_ford = BellmanFord(ex)
    bellman_ford.find_arbitrage_and_shortest_path(edges, rates, selected_currency_1, selected_currency_2)

    print(ex.arbitrage_info)
    print(ex.cycle)

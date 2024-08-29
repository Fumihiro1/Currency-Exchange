import math
import requests

# Graphs
class Edge:
    def __init__(self, start, destination, weight):
        self.start = start
        self.destination = destination
        self.weight = weight

class Graph:
    def __init__(self, no_vertices, arbitrages):
        self.no_vertices = no_vertices
        self.edges = []
        self.arbitrage = []

    # Add edge
    def add_edge(self, start, destination, weight):
        self.edges.append(Edge(start,destination,weight))

    def bellman_ford(self, source):                  # Bellman-Ford Algorithm
        distance = [float("Inf")] * self.no_vertices # Start with distances as infinity
        predecessor = [-1] * self.no_vertices        # Predecessor array to store path
        distance[source] = 0                         # distance to source node is always 0

        # Relaxation Process
        for _ in range(self.no_vertices - 1): # Iterate n-1 times
            for edge in self.edges: # For each edge in the graph
                # If the start node has been reached before, and the path through the edge is a shorter path
                if distance[edge.start] != float('inf') and distance[edge.start] + edge.weight < distance[edge.destination]:
                    distance[edge.destination] = distance[edge.start] + edge.weight # Update the shortest path found
                    predecessor[edge.destination] = edge.start

        # Check for negative cycles after n-1 iterations
        found_cycles = False
        for edge in self.edges:  # For each edge
            if distance[edge.start] + edge.weight < distance[edge.destination]:  # If there is a shorter path
                # Add the negative cycle to the list of arbitrages
                cycle = self.get_negative_cycle(predecessor, edge.destination)
                if cycle not in self.arbitrages:  # To avoid duplicates
                    self.arbitrages.append(cycle)
                    found_cycles = True

        return found_cycles, self.arbitrages

    # Find where the negative cycle is
    def get_negative_cycle(self, predecessor, start):
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

# Create a graph from a matrix and list of currencies
def build_graph(currencies, matrix):
    # Get the number of currencies and create a graph
    n = len(currencies)
    graph = Graph(n)

    # Fill the graph with the matrix values
    for i in range(n):
        for j in range(n):
            if i != j:
                rate = matrix[i][j]
                weight = -math.log10(rate) # using the negative logarithm
                graph.add_edge(i, j, weight)

    return graph

# Runs the arbitrage program
def find_arbitrage(graph, currencies):
    arbitrage_exists, result = graph.bellman_ford(0)
    if arbitrage_exists:
        print("Arbitrage detected! Currency sequence: " + " -> ".join(currencies[i] for i in result))
    else:
        print("No arbitrage opportunities found.")

# Get the input type
def input_type():
    print('Input type?')
    print('1. API')
    print('2. Custom')
    print('3. Run Test Cases')
    choice = input('Choose input type (1, 2 or 3): ')

    # Return the appropriate string
    if choice == '1':
        print('API chosen')
        return 'API'
    elif choice == '2':
        print('Custom chosen')
        return 'Custom'
    elif choice == '3':
        print('Test cases chosen')
    else:
        print('Invalid choice. Try again.')
        return input_type()

def main():
    # Get input choice
    input_choice = input_type()
    main()

if __name__ == '__main__':
    main()
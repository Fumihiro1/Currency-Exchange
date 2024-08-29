import math

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
        self.currency_matrix

        # 2d n * n array of key value pairs (GROSS)
        self.best_conversion_rates = [[{} for _ in range(no_vertices)] for _ in range(no_vertices)]

    # Add edge
    def add_edge(self, start, destination, weight):
        self.edges.append(Edge(start,destination,weight))

    def calculate_best_conversion_rates(self):


    def build_graph(self, currencies, matrix):
        # Get the number of currencies and create a graph
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
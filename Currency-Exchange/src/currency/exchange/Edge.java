package currency.exchange;

class Edge {
    int start;
    int destination;
    int weight;

    Edge(int start, int destination, int weight) {
        this.start = start;
        this.destination = destination;
        this.weight = weight;
    }
}

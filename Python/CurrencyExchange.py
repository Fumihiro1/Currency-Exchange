import tkinter as tk
from tkinter import messagebox, ttk
import requests
import numpy as np

# Function to fetch exchange rates from the API
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
    return rates

# Function to update the matrix view with fetched exchange rates
def update_matrix_view(event=None):
    selected_currencies = [currency1.get(), currency2.get(), currency3.get(), currency4.get(), currency5.get()]
    if len(set(selected_currencies)) < len(selected_currencies):
        messagebox.showerror("Duplicate Currency", "Please select different currencies for each dropdown.")
        return

    rates = fetch_exchange_rates(selected_currencies)

    if rates:
        for i, currency in enumerate(selected_currencies):
            conversion_rates[0][i + 1].config(text=currency)
            conversion_rates[i + 1][0].config(text=currency)
            for j, rate_currency in enumerate(selected_currencies):
                if i == j:
                    conversion_rates[i + 1][j + 1].config(text="1.000")
                else:
                    rate = rates[currency].get(rate_currency, 'N/A')
                    conversion_rates[i + 1][j + 1].config(text=f"{rate:.3f}" if rate != 'N/A' else 'N/A')

        # Detect arbitrage
        edges = create_graph_from_rates(rates)
        bellman_ford_arbitrage(edges, rates)

def create_graph_from_rates(rates):
    edges = []
    for from_currency in rates:
        for to_currency in rates:
            if from_currency != to_currency:
                rate = rates[from_currency].get(to_currency, 'N/A')
                if rate != 'N/A':
                    # Create edge with weight as negative log of rate
                    edges.append((from_currency, to_currency, -np.log10(float(rate))))
    return edges

def bellman_ford_arbitrage(edges, rates):
    # Initialize distances and predecessors
    distance = {node: float('inf') for node in set([u for u, _, _ in edges] + [v for _, v, _ in edges])} # initialise all distances to infinity except for start node
    predecessor = {node: None for node in distance} # initialise predecessor dictionary to keep track of path
    start_node = list(distance.keys())[0] # Choose first node as start node
    distance[start_node] = 0 # Distance from start node to itself is 0

    # Relax all edges |V| - 1 times
    for _ in range(len(distance) - 1):
        for u, v, w in edges:
            # relax the edge (u,v) if a shorter path is found
            if distance[u] + w < distance[v]:
                distance[v] = distance[u] + w
                predecessor[v] = u # Update the predecessor of v to be equal to u

    # Check for negative weight cycles to detect arbitrage opportunities
    arbitrage_found = False
    cycle_start = None

    # loop again, if shorter path is still found then negative weight cycle is present
    for u, v, w in edges:
        if distance[u] + w < distance[v]:
            arbitrage_found = True
            cycle_start = v # start of cycle
            break

    if arbitrage_found:
        # If there is an arbitrage, trace the path using predecessors
        cycle = []
        visited = set()
        current = cycle_start

        # Find the cycle starting point
        for _ in range(len(distance)):
            current = predecessor[current]

        cycle_start = current

        # Trace back to find the complete cycle
        while True:
            cycle.append(current)
            current = predecessor[current]
            if current == cycle_start:
                cycle.append(current)
                break
        cycle.reverse() # reverse to get the correct order of the cycle

        # Calculate the gain product
        gain_product = 1.0
        for i in range(len(cycle) - 1):
            from_currency = cycle[i]
            to_currency = cycle[i + 1]
            rate = rates[from_currency].get(to_currency, 'N/A') # get the rate from one currency to the next
            if rate != 'N/A':
                gain_product *= float(rate) # multiply to accumulate the gain

        # Print the arbitrage opportunity and percentage gain
        path = ' -> '.join(cycle)
        print(f"Arbitrage opportunity found: {path}")
        print(f"Potential gain: {(gain_product - 1) * 100:.2f}%")
    else:
        print("No arbitrage opportunity detected.")

# Initialize Tkinter window
root = tk.Tk()
root.geometry('1000x500')
root.title("Currency Exchange")

# Define available currencies
available_currencies = ['USD', 'NZD', 'AUD', 'EUR', 'JPY', 'THB', 'INR', 'BOB', 'BRL']

# Create frames
top_left_frame = tk.Frame(root)
top_right_frame = tk.Frame(root)
bottom_left_frame = tk.Frame(root)
bottom_right_frame = tk.Frame(root)

# Place frames in a grid with padding
top_left_frame.grid(row=0, column=0, padx=40, pady=10, sticky="nw")
top_right_frame.grid(row=0, column=1, padx=40, pady=10, sticky="ne")
bottom_left_frame.grid(row=1, column=0, padx=40, pady=10, sticky="sw")
bottom_right_frame.grid(row=1, column=1, padx=40, pady=10, sticky="se")

# add color to frames
bottom_left_frame.config(background="white")

# Create the title for dropdown selectors
dropdown_title = tk.Label(top_left_frame, text="Currencies", font=('Arial', 12, 'bold'))
dropdown_title.grid(row=0, column=0, padx=5, pady=5, sticky="n")

# Create dropdown selectors for currencies
currency1 = tk.StringVar(value=available_currencies[0]) # set to first 5 available currencies
currency2 = tk.StringVar(value=available_currencies[1])
currency3 = tk.StringVar(value=available_currencies[2])
currency4 = tk.StringVar(value=available_currencies[3])
currency5 = tk.StringVar(value=available_currencies[4])

currency_selectors = [
    ttk.Combobox(top_left_frame, textvariable=currency1, values=available_currencies),
    ttk.Combobox(top_left_frame, textvariable=currency2, values=available_currencies),
    ttk.Combobox(top_left_frame, textvariable=currency3, values=available_currencies),
    ttk.Combobox(top_left_frame, textvariable=currency4, values=available_currencies),
    ttk.Combobox(top_left_frame, textvariable=currency5, values=available_currencies)
]

# Function to handle currency selection changes
def on_currency_select(event):
    update_matrix_view()

# Place currency selectors in a vertical column on the left side
for i, selector in enumerate(currency_selectors):
    selector.grid(row=i+1, column=0, padx=5, pady=10, sticky="w")
    selector.bind("<<ComboboxSelected>>", on_currency_select)

# Matrix to display conversion rates
conversion_rates = [[None for _ in range(6)] for _ in range(6)]

# matrix view title
matrix_title = tk.Label(top_right_frame, text="Exchange Rate Matrix", font=('Arial', 12, 'bold'))
matrix_title.grid(row=0, column=0, columnspan=6, padx=5, pady=5, sticky="w")

# set up headers and initialize matrix cells
conversion_rates[0][0] = tk.Label(top_right_frame, text="From/To", borderwidth=1, relief="solid", width=15, height=2)
conversion_rates[0][0].grid(row=1, column=0, sticky="nsew")

for i in range(5):
    conversion_rates[0][i+1] = tk.Label(top_right_frame, text="N/A", borderwidth=1, relief="solid", width=15, height=2)
    conversion_rates[0][i+1].grid(row=1, column=i+1, sticky="nsew")  # Top row headers

    conversion_rates[i+1][0] = tk.Label(top_right_frame, text="N/A", borderwidth=1, relief="solid", width=15, height=2)
    conversion_rates[i+1][0].grid(row=i+2, column=0, sticky="nsew")  # Left column headers

    for j in range(5):
        conversion_rates[i+1][j+1] = tk.Label(top_right_frame, text="N/A", borderwidth=1, relief="solid", width=15, height=2)
        conversion_rates[i+1][j+1].grid(row=i+2, column=j+1, sticky="nsew")  # Conversion rates

# bottom left frame (show arbitrage and percentage gain)


# Initialize the matrix view with default values
update_matrix_view()

# Run the Tkinter main loop
root.mainloop()
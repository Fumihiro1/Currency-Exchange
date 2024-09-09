import tkinter as tk
from tkinter import messagebox, ttk
import requests
import numpy as np

use_custom_rates = False

exchange_rates = {}

class Labels:
    def __init__(self):
        self.cycle = ""
        self.arbitrage_info = ""

class BellmanFord:
    INF = float('inf')

    def __init__(self, ex):
        self.ex = ex

    def find_arbitrage_and_shortest_path(self, edges, rates, start_currency, end_currency, epsilon=0.01):
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
                rate = exchange_rates.get(from_currency, {}).get(to_currency, 'N/A')
                if rate != 'N/A':
                    gain_product *= round(float(rate), 3)

            # Check if the gain product exceeds the threshold
            path = ' -> '.join(cycle)
            self.ex.arbitrage_info = (f"Arbitrage opportunity found: {path}\n"
                                        f"Potential gain: {(gain_product - 1) * 100:.2f}%")
            self.ex.cycle = "No path found. Due to arbitrage present."
        else:
            self.ex.arbitrage_info = "No arbitrage opportunity detected."
            # Find the shortest path from start_currency to end_currency
            shortest_path = self._reconstruct_path(predecessor, start_currency, end_currency)
            if shortest_path:
                path_str = ' -> '.join(shortest_path)
                self.ex.cycle = f"Path from {start_currency} to {end_currency}: {path_str}"

    def _reconstruct_path(self, predecessor, start_currency, end_currency):
        path = []
        current = end_currency

        # Handle cases where end_currency is not reachable
        while current is not None:
            path.append(current)
            current = predecessor[current]

            # If we've reached the start_currency or gone through all predecessors
            if current == start_currency:
                path.append(start_currency)
                break
            if len(path) > len(predecessor):  # Detect a possible cycle or infinite loop
                return []  # No valid path found

        path.reverse()
        return path if path[0] == start_currency else []

# Function to fetch exchange rates from the API
def fetch_exchange_rates(currencies):
    global exchange_rates
    global use_custom_rates

    if use_custom_rates is False:

        # Fetch live exchange rates from API
        try:
            for base_currency in currencies:
                response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{base_currency.strip()}")
                response.raise_for_status()  # Check for request errors
                all_rates = response.json().get('rates', {})

                # Filter rates to include only those in the 'currencies' list
                filtered_rates = {currency: rate for currency, rate in all_rates.items() if
                                    currency in currencies and currency != base_currency}

                exchange_rates[base_currency] = filtered_rates
        except requests.exceptions.RequestException as e:
            print(f"Error fetching exchange rates: {e}")


# Function to update the matrix view with fetched exchange rates
def update_matrix_view(event=None):
    global exchange_rates

    selected_currencies = [currency1.get(), currency2.get(), currency3.get(), currency4.get(), currency5.get()]
    if len(set(selected_currencies)) < len(selected_currencies):
        messagebox.showerror("Duplicate Currency", "Please select different currencies for each dropdown.")
        return

    fetch_exchange_rates(selected_currencies)
    update_conversion_rate_dropdowns()

    for i, currency in enumerate(selected_currencies):
        conversion_rates[0][i + 1].config(text=currency)
        conversion_rates[i + 1][0].config(text=currency)
        for j, rate_currency in enumerate(selected_currencies):
            if i == j:
                conversion_rates[i + 1][j + 1].config(text="1.000")
            else:
                rate = exchange_rates[currency].get(rate_currency, 'N/A')
                conversion_rates[i + 1][j + 1].config(text=f"{rate:.3f}" if rate != 'N/A' else 'N/A')

        # Detect arbitrage
        edges = create_graph_from_rates(exchange_rates)
        bellman_ford = BellmanFord(ex)
        bellman_ford.find_arbitrage_and_shortest_path(edges, exchange_rates, selected_currency_1.get(), selected_currency_2.get(), epsilon=0.01)

        # Update arbitrage info
        arbitrage_info.set(ex.arbitrage_info)

        # Update the best path info
        bestpath_info.set(ex.cycle)

def create_graph_from_rates(rates):
    edges = []
    for from_currency in rates:
        for to_currency in rates:
            if from_currency != to_currency:
                rate = rates[from_currency].get(to_currency, 'N/A')
                if rate != 'N/A':
                    # Convert rate to float and round it to 3 decimal places
                    rate_value = round(float(rate), 3)
                    # Create edge with weight as negative log of rate (rounded to 3 decimal places)
                    weight = -round(np.log10(rate_value), 3)
                    edges.append((from_currency, to_currency, weight))
    return edges

# Initialize Tkinter window
root = tk.Tk()
root.geometry('1200x500')
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

# Add color to frames
bottom_left_frame.config(background="white")
bottom_right_frame.config(background="white")

# Create the title for dropdown selectors
dropdown_title = tk.Label(top_left_frame, text="Currencies", font=('Arial', 12, 'bold'))
dropdown_title.grid(row=0, column=0, padx=5, pady=5, sticky="n")

# Create dropdown selectors for currencies
currency1 = tk.StringVar(value=available_currencies[0])
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

# Create a list to store the currently selected currencies
selected_currencies = [currency1.get(), currency2.get(), currency3.get(), currency4.get(), currency5.get()]

# Function to update the selected_currencies list whenever a selection is made
def update_selected_currencies(*args):
    selected_currencies[0] = currency1.get()
    selected_currencies[1] = currency2.get()
    selected_currencies[2] = currency3.get()
    selected_currencies[3] = currency4.get()
    selected_currencies[4] = currency5.get()

# Bind the trace method to each currency variable to update the selected_currencies list on change
currency1.trace('w', update_selected_currencies)
currency2.trace('w', update_selected_currencies)
currency3.trace('w', update_selected_currencies)
currency4.trace('w', update_selected_currencies)
currency5.trace('w', update_selected_currencies)

# Create the dropdowns in the top_left_frame and place them
for idx, selector in enumerate(currency_selectors):
    selector.grid(row=idx, column=0, padx=5, pady=5)

# Function to handle currency selection changes
def on_currency_select(event):
    update_matrix_view()

# Place currency selectors in a vertical column on the left side
for i, selector in enumerate(currency_selectors):
    selector.grid(row=i + 1, column=0, padx=5, pady=10, sticky="w")
    selector.bind("<<ComboboxSelected>>", on_currency_select)

# Matrix to display conversion rates
conversion_rates = [[None for _ in range(6)] for _ in range(6)]

# Matrix view title
matrix_title = tk.Label(top_right_frame, text="Exchange Rate Matrix", font=('Arial', 12, 'bold'))
matrix_title.grid(row=0, column=0, columnspan=6, padx=5, pady=5, sticky="w")

# Set up headers and initialize matrix cells
conversion_rates[0][0] = tk.Label(top_right_frame, text="From/To", borderwidth=1, relief="solid", width=15, height=2)
conversion_rates[0][0].grid(row=1, column=0, sticky="nsew")

for i in range(5):
    conversion_rates[0][i + 1] = tk.Label(top_right_frame, text="N/A", borderwidth=1, relief="solid", width=15, height=2)
    conversion_rates[0][i + 1].grid(row=1, column=i + 1, sticky="nsew")  # Top row headers

    conversion_rates[i + 1][0] = tk.Label(top_right_frame, text="N/A", borderwidth=1, relief="solid", width=15, height=2)
    conversion_rates[i + 1][0].grid(row=i + 2, column=0, sticky="nsew")  # Left column headers

    for j in range(5):
        conversion_rates[i + 1][j + 1] = tk.Label(top_right_frame, text="N/A", borderwidth=1, relief="solid", width=15, height=2)
        conversion_rates[i + 1][j + 1].grid(row=i + 2, column=j + 1, sticky="nsew")  # Main matrix

# Label for arbitrage information
ex = Labels()
arbitrage_info = tk.StringVar(value="No arbitrage opportunity detected.")
arbitrage_label = tk.Label(bottom_left_frame, textvariable=arbitrage_info, wraplength=400, background="white", font=('Arial', 10))
arbitrage_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

# Add a title above the dropdowns
title_label = ttk.Label(bottom_right_frame, text="Best Conversion Rate")
title_label.grid(row=0, column=0, columnspan=3, pady=10)

# Create variables for the two dropdowns
selected_currency_1 = tk.StringVar(value=selected_currencies[0])
selected_currency_2 = tk.StringVar(value=selected_currencies[1])

# Function to update the second dropdown based on the first dropdown's selection
def update_second_dropdown(*args):
    selected_1 = selected_currency_1.get()
    updated_options = [currency for currency in selected_currencies if currency != selected_1]
    currency_dropdown_2['values'] = updated_options

    # If the selected currency in dropdown 2 is no longer valid, reset it
    if selected_currency_2.get() == selected_1 or selected_currency_2.get() not in updated_options:
        selected_currency_2.set(updated_options[0] if updated_options else '')

# Function to update the first dropdown based on the second dropdown's selection
def update_first_dropdown(*args):
    selected_2 = selected_currency_2.get()
    updated_options = [currency for currency in selected_currencies if currency != selected_2]
    currency_dropdown_1['values'] = updated_options

    # If the selected currency in dropdown 1 is no longer valid, reset it
    if selected_currency_1.get() == selected_2 or selected_currency_1.get() not in updated_options:
        selected_currency_1.set(updated_options[0] if updated_options else '')

def update_conversion_rate_dropdowns(*args):
    update_first_dropdown()
    update_second_dropdown()

# Create the dropdowns in the bottom-right frame
currency_dropdown_1 = ttk.Combobox(bottom_right_frame, textvariable=selected_currency_1, values=selected_currencies)
currency_dropdown_2 = ttk.Combobox(bottom_right_frame, textvariable=selected_currency_2, values=selected_currencies)

# Position the dropdowns
currency_dropdown_1.grid(row=1, column=0, padx=10, pady=10)
currency_dropdown_2.grid(row=1, column=2, padx=10, pady=10)

# Add an arrow between the dropdowns
arrow_label = ttk.Label(bottom_right_frame, text=" -> ")
arrow_label.grid(row=1, column=1, pady=10)

bestpath_info = tk.StringVar(value="Loading..")
bestpath_label = tk.Label(bottom_right_frame, textvariable=bestpath_info, background="white", font=('Arial', 10))
bestpath_label.grid(row=2, column=0)

def on_dropdown_select(event):
    global exchange_rates

    fetch_exchange_rates(selected_currencies)

    update_conversion_rate_dropdowns()
    # Detect arbitrage
    edges = create_graph_from_rates(exchange_rates)
    bellman_ford = BellmanFord(ex)
    bellman_ford.find_arbitrage_and_shortest_path(edges, exchange_rates, selected_currency_1.get(), selected_currency_2.get(),
                                                  epsilon=0.01)
    # Update arbitrage info
    arbitrage_info.set(ex.arbitrage_info)

    # Update the best path info
    bestpath_info.set(ex.cycle)


# Bind the selection event to the update functions
currency_dropdown_1.bind("<<ComboboxSelected>>", on_dropdown_select)
currency_dropdown_2.bind("<<ComboboxSelected>>", on_dropdown_select)

exchange_rates_no_arbitrage_direct = {
    'A': {
        'B': 1,
        'C': 1,
        'D': 1,
        'E': 1
    },
    'B': {
        'A': 1,
        'C': 1,
        'D': 1,
        'E': 1
    },
    'C': {
        'A': 1,
        'B': 1,
        'D': 1,
        'E': 1
    },
    'D': {
        'A': 1,
        'B': 1,
        'C': 1,
        'E': 1
    },
    'E': {
        'A': 1,
        'B': 1,
        'C': 1,
        'D': 1
    }
}

exchange_rates_no_arbitrage_indirect = {
    'A': {
        'B': 0.5,
        'C': 0.9,
        'D': 0.9,
        'E': 0.5
    },
    'B': {
        'A': 0.8,
        'C': 0.8,
        'D': 1,
        'E': 1
    },
    'C': {
        'A': 1,
        'B': 0.5,
        'D': 1,
        'E': 1
    },
    'D': {
        'A': 1,
        'B': 1,
        'C': 1,
        'E': 1
    },
    'E': {
        'A': 1,
        'B': 1,
        'C': 1,
        'D': 1
    }
}

# Add a button to set the selected currencies to those in the exchange_rates_no_arbitrage dictionary
def set_custom_currencies(custom_currencies):
    global use_custom_rates

    # Use currencies from exchange_rates_no_arbitrage to update the dropdowns
    available_currencies_in_dict = list(custom_currencies.keys())

    # Disable interaction with dropdowns
    for selector in currency_selectors:
        selector.config(state="disabled")

    # Set the first five available currencies from the dictionary into the dropdowns
    if len(available_currencies_in_dict) >= 5:
        currency1.set(available_currencies_in_dict[0])
        currency2.set(available_currencies_in_dict[1])
        currency3.set(available_currencies_in_dict[2])
        currency4.set(available_currencies_in_dict[3])
        currency5.set(available_currencies_in_dict[4])

        use_custom_rates = True

        # Update the selected currencies list and matrix view with custom rates
        update_matrix_view_with_custom_rates(custom_currencies)

def reset_gui():
    global use_custom_rates

    use_custom_rates = False

    # Set to first 5 moneys
    currency1.set(available_currencies[0])
    currency2.set(available_currencies[1])
    currency3.set(available_currencies[2])
    currency4.set(available_currencies[3])
    currency5.set(available_currencies[4])

    # Disable interaction with dropdowns
    for selector in currency_selectors:
        selector.config(state="enabled")

    update_matrix_view()

def update_matrix_view_with_custom_rates(custom_currencies):

    global exchange_rates
    # Fetch selected currencies from dropdowns
    selected_currencies = [currency1.get(), currency2.get(), currency3.get(), currency4.get(), currency5.get()]

    # Use custom exchange rates for the selected currencies
    exchange_rates = {currency: custom_currencies[currency] for currency in selected_currencies}

    # Update the matrix view with the selected currencies and their rates
    for i, currency in enumerate(selected_currencies):
        conversion_rates[0][i + 1].config(text=currency)  # Update column headers
        conversion_rates[i + 1][0].config(text=currency)  # Update row headers
        for j, rate_currency in enumerate(selected_currencies):
            if i == j:
                conversion_rates[i + 1][j + 1].config(text="1.000")  # Diagonal should be 1.000 (self conversion)
            else:
                rate = exchange_rates[currency].get(rate_currency, 'N/A')  # Get the conversion rate from the custom rates
                conversion_rates[i + 1][j + 1].config(text=f"{rate:.3f}" if rate != 'N/A' else 'N/A')

        update_conversion_rate_dropdowns()

        # Detect arbitrage
        edges = create_graph_from_rates(exchange_rates)
        bellman_ford = BellmanFord(ex)
        bellman_ford.find_arbitrage_and_shortest_path(edges, exchange_rates, selected_currency_1.get(), selected_currency_2.get(), epsilon=0.01)

        # Update arbitrage info
        arbitrage_info.set(ex.arbitrage_info)

        # Update the best path info
        bestpath_info.set(ex.cycle)

# Create and place the button in the bottom-left frame
arbitrage_button = ttk.Button(bottom_left_frame, text="Case 1: No Arbitrage, Direct Path", command=lambda: set_custom_currencies(exchange_rates_no_arbitrage_direct))
arbitrage_button.grid(row=1, column=0, padx=10, pady=10, sticky="w")

arbitrage_button2 = ttk.Button(bottom_left_frame, text="Case 2: No Arbitrage, Indirect Path", command=lambda: set_custom_currencies(exchange_rates_no_arbitrage_indirect))
arbitrage_button2.grid(row=2, column=0, padx=10, pady=10, sticky="w")


reset_button = ttk.Button(bottom_left_frame, text="Reset", command=lambda: reset_gui())
reset_button.grid(row=3, column=0, padx=10, pady=10, sticky="w")

# Refresh matrix view
update_matrix_view()

# Run the application
root.mainloop()
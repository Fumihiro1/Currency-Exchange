import tkinter as tk
from tkinter import messagebox, ttk
import requests
import numpy as np

# Global dictionary to store exchange rates
exchange_rates = {}

# Static dictionaries for exchange rates with no arbitrage (direct and indirect)
exchange_rates_no_arbitrage_direct = {
    'A': {'B': 1, 'C': 1, 'D': 1, 'E': 1},
    'B': {'A': 1, 'C': 1, 'D': 1, 'E': 1},
    'C': {'A': 1, 'B': 1, 'D': 1, 'E': 1},
    'D': {'A': 1, 'B': 1, 'C': 1, 'E': 1},
    'E': {'A': 1, 'B': 1, 'C': 1, 'D': 1}
}

exchange_rates_no_arbitrage_indirect = {
    'A': {'B': 0.5, 'C': 0.9, 'D': 0.9, 'E': 0.5},
    'B': {'A': 0.8, 'C': 0.8, 'D': 1, 'E': 1},
    'C': {'A': 1, 'B': 0.5, 'D': 1, 'E': 1},
    'D': {'A': 1, 'B': 1, 'C': 1, 'E': 1},
    'E': {'A': 1, 'B': 1, 'C': 1, 'D': 1}
}

class Labels:
    """ Class to store and manage label texts."""
    def __init__(self):
        self.path_info = "" # Best path label
        self.arbitrage_info = "" # Arbitrage path and percentage gain label

class BellmanFord:
    """ Class to find arbitrage opportunities and shortest paths using the Bellman-Ford algorithm"""
    INF = float('inf')

    def __init__(self, ex):
        self.ex = ex

    def find_arbitrage_and_shortest_path(self, edges, start_currency, end_currency):
        """
        Find arbitrage opportunities and the shortest path between two currencies.

        Args:
            edges (list of tuples): List of edges in the form (from_currency, to_currency, rate).
            start_currency (str): The starting currency.
            end_currency (str): The ending currency.
        """

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

            # Calculate the product of exchange rates for the detected cycle, calculated using 3 dp rounded values
            gain_product = 1.0
            for i in range(len(cycle) - 1):
                from_currency = cycle[i]
                to_currency = cycle[i + 1]
                rate = exchange_rates.get(from_currency, {}).get(to_currency, 'N/A')
                if rate != 'N/A':
                    gain_product *= round(float(rate), 3)

            # Construct the output string labels
            path = ' -> '.join(cycle)
            self.ex.arbitrage_info = (f"Arbitrage opportunity found: {path}\n"
                                        f"Potential gain: {(gain_product - 1) * 100:.2f}%")
            self.ex.path_info = "No path found. Due to arbitrage present."
        else:
            self.ex.arbitrage_info = "No arbitrage opportunity detected."

            # Find the shortest path from start_currency to end_currency
            shortest_path = self._reconstruct_path(predecessor, start_currency, end_currency)
            if shortest_path:
                path_str = ' -> '.join(shortest_path)
                self.ex.path_info = f"Path from {start_currency} to {end_currency}: {path_str}"

    def _reconstruct_path(self, predecessor, start_currency, end_currency):
        """
        Reconstruct the shortest path from start_currency to end_currency.

        Args:
            predecessor (dict): The predecessor map for path reconstruction.
            start_currency (str): The starting currency.
            end_currency (str): The ending currency.

        Returns:
            list: The list of currencies in the shortest path.
        """

        path = []
        current = end_currency

        while current is not None:
            path.append(current)
            current = predecessor[current]

            if current == start_currency:
                path.append(start_currency)
                break
            if len(path) > len(predecessor):  # Detect a possible cycle or infinite loop
                return []  # No valid path found

        path.reverse()
        return path if path[0] == start_currency else []

# Function to fetch exchange rates from the API
def fetch_exchange_rates(currencies):
    """
    Fetch live exchange rates for a list of currencies and store them in a global dictionary.

    Args:
        currencies (list): List of currency codes to fetch rates for.
    """

    global exchange_rates
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
    """
    Update the matrix view with the latest exchange rates and check for arbitrage opportunities.
    """
    global exchange_rates

    # Fetch selected currencies from dropdowns (allow blanks)
    selected_currencies = [currency1.get(), currency2.get(), currency3.get(), currency4.get(), currency5.get()]

    # Ensure there are at least two non-blank currencies selected
    if len([currency for currency in selected_currencies if currency]) < 2:
        messagebox.showerror("Selection Error", "Please select at least two different currencies.")
        return

    # Fetch exchange rates for non-blank currencies only
    non_blank_currencies = [currency for currency in selected_currencies if currency]
    fetch_exchange_rates(non_blank_currencies)
    update_conversion_rate_dropdowns()

    # Update the matrix view with exchange rates
    for i, currency in enumerate(selected_currencies):

        # Set the table headers; if currency is blank, set cell to blank
        conversion_rates[0][i + 1].config(text=currency if currency else "")
        conversion_rates[i + 1][0].config(text=currency if currency else "")

        for j, rate_currency in enumerate(selected_currencies):
            if i == j and currency:  # Diagonal cells should show 1.000
                conversion_rates[i + 1][j + 1].config(text="1.000")
            elif not currency or not rate_currency:  # Cells with blank currencies
                conversion_rates[i + 1][j + 1].config(text="")
            else:
                # Set fetched exchange rate or 'N/A'
                rate = exchange_rates.get(currency, {}).get(rate_currency, 'N/A')
                conversion_rates[i + 1][j + 1].config(text=f"{rate:.3f}" if rate != 'N/A' else 'N/A')

    # Detect arbitrage if there are at least two selected currencies
    if len(non_blank_currencies) >= 2:
        edges = create_graph_from_rates(exchange_rates)
        bellman_ford = BellmanFord(ex)
        bellman_ford.find_arbitrage_and_shortest_path(edges, selected_currency_1.get(), selected_currency_2.get())

        # Update arbitrage and best path info
        arbitrage_info.set(ex.arbitrage_info)
        bestpath_info.set(ex.path_info)

    else:
        # Clear arbitrage and path info if fewer than two currencies are selected
        arbitrage_info.set("")
        bestpath_info.set("")

def create_graph_from_rates(rates):
    """
    Create a negative logarithm graph representation of the exchange rates for use with the Bellman-Ford algorithm.
    """
    edges = []
    for from_currency in rates:
        for to_currency in rates:
            if from_currency != to_currency and from_currency and to_currency:  # Skip blanks
                rate = rates[from_currency].get(to_currency, 'N/A')
                if rate != 'N/A':
                    # Convert rate to float and round it to 3 decimal places
                    rate_value = round(float(rate), 3)
                    # Create edge with weight as negative log of rate (rounded to 3 decimal places)
                    weight = -round(np.log10(rate_value), 3)
                    edges.append((from_currency, to_currency, weight))
    return edges

def update_selected_currencies(*args):
    """
    Update the selected currencies list based on current dropdown selections.
    """
    selected_currencies[0] = currency1.get()
    selected_currencies[1] = currency2.get()
    selected_currencies[2] = currency3.get()
    selected_currencies[3] = currency4.get()
    selected_currencies[4] = currency5.get()

def on_currency_select(event):
    """
    Handle changes in currency selection and update the matrix view accordingly.
    """
    update_matrix_view()

def on_dropdown_select(event):
    """
    Handle changes in dropdown selections and update exchange rates and arbitrage information.
    """
    global exchange_rates

    update_conversion_rate_dropdowns()
    # Detect arbitrage
    edges = create_graph_from_rates(exchange_rates)
    bellman_ford = BellmanFord(ex)
    bellman_ford.find_arbitrage_and_shortest_path(edges, selected_currency_1.get(), selected_currency_2.get())
    # Update arbitrage info
    arbitrage_info.set(ex.arbitrage_info)

    # Update the best path info
    bestpath_info.set(ex.path_info)

# Function to update the second dropdown based on the first dropdown's selection
def update_second_dropdown(*args):
    """
    Update the options in the second currency dropdown based on the selected value of the first dropdown.
    """
    selected_1 = selected_currency_1.get()
    updated_options = [currency for currency in selected_currencies if currency != selected_1 and currency]  # Skip blanks
    currency_dropdown_2['values'] = updated_options

    # If the selected currency in dropdown 2 is no longer valid, reset it
    if selected_currency_2.get() == selected_1 or selected_currency_2.get() not in updated_options:
        selected_currency_2.set(updated_options[0] if updated_options else '')

# Function to update the first dropdown based on the second dropdown's selection
def update_first_dropdown(*args):
    """
    Update the options in the first currency dropdown based on the selected value of the second dropdown.
    """
    selected_2 = selected_currency_2.get()
    updated_options = [currency for currency in selected_currencies if currency != selected_2 and currency]  # Skip blanks
    currency_dropdown_1['values'] = updated_options

    # If the selected currency in dropdown 1 is no longer valid, reset it
    if selected_currency_1.get() == selected_2 or selected_currency_1.get() not in updated_options:
        selected_currency_1.set(updated_options[0] if updated_options else '')

def update_conversion_rate_dropdowns(*args):
    """
    Update the options in both currency dropdowns.
    """
    update_first_dropdown()
    update_second_dropdown()

# Add a button to set the selected currencies to those in the exchange_rates_no_arbitrage dictionary
def set_custom_currencies(custom_currencies):
    """
    Set custom currencies in the dropdowns based on provided rates.
    """
    # Use currencies to update the dropdowns
    available_currencies_in_dict = list(custom_currencies.keys())

    # Disable interaction with dropdowns
    for selector in currency_selectors:
        selector.config(state="disabled")

    # Set the available currencies from the dictionary into the dropdowns (up to 5)
    currency_list = [currency1, currency2, currency3, currency4, currency5]

    # Loop through the selectors and set values based on available currencies
    for i, selector in enumerate(currency_list):
        if i < len(available_currencies_in_dict):
            selector.set(available_currencies_in_dict[i])
        else:
            selector.set("")  # Clear the remaining selectors if fewer than 5 currencies are available


    # Update the selected currencies list and matrix view with custom rates
    update_matrix_view_with_custom_rates(custom_currencies)

def reset_gui():
    """
    Reset the dropdowns to the first 5 available currencies.
    """

    currency1.set(available_currencies[0])
    currency2.set(available_currencies[1])
    currency3.set(available_currencies[2])
    currency4.set(available_currencies[3])
    currency5.set(available_currencies[4])

    # Enable interaction with dropdowns
    for selector in currency_selectors:
        selector.config(state="enabled")

    # Update the matrix view with the newly set currencies
    update_matrix_view()

def update_matrix_view_with_custom_rates(custom_currencies):
    """
    Updates the matrix view using custom exchange rates provided by the user.

    Args:
        custom_currencies (dict): A dictionary where keys are currency names and values are dictionaries
                                  of exchange rates, with inner dictionaries mapping other currency names
                                  to exchange rates.
    """
    global exchange_rates
    # Fetch selected currencies from dropdowns (allow blanks)
    selected_currencies = [currency1.get(), currency2.get(), currency3.get(), currency4.get(), currency5.get()]

    # Filter out any blank selections
    non_blank_currencies = [currency for currency in selected_currencies if currency]

    # Ensure there are at least two non-blank selections
    if len(non_blank_currencies) < 2:
        messagebox.showerror("Selection Error", "Please select at least two different currencies.")
        return

    # Use custom exchange rates for the non-blank selected currencies
    exchange_rates = {currency: custom_currencies[currency] for currency in non_blank_currencies}

    # Update the matrix view with the selected currencies and their rates
    for i, currency in enumerate(selected_currencies):
        # Set the table headers; if currency is blank, set cell to blank
        conversion_rates[0][i + 1].config(text=currency if currency else "")
        conversion_rates[i + 1][0].config(text=currency if currency else "")

        for j, rate_currency in enumerate(selected_currencies):
            if i == j and currency:  # Diagonal cells should show 1.000 for non-blank currencies
                conversion_rates[i + 1][j + 1].config(text="1.000")
            elif not currency or not rate_currency:  # If any currency is blank, set cell to blank
                conversion_rates[i + 1][j + 1].config(text="")
            else:
                # Otherwise, set the fetched exchange rate or 'N/A' if not available
                rate = exchange_rates.get(currency, {}).get(rate_currency, 'N/A')
                conversion_rates[i + 1][j + 1].config(text=f"{rate:.3f}" if rate != 'N/A' else 'N/A')

    update_conversion_rate_dropdowns()

    # Detect arbitrage if enough currencies are selected
    edges = create_graph_from_rates(exchange_rates)
    bellman_ford = BellmanFord(ex)
    bellman_ford.find_arbitrage_and_shortest_path(edges, selected_currency_1.get(), selected_currency_2.get())

    # Update arbitrage info
    arbitrage_info.set(ex.arbitrage_info)

    # Update the best path info
    bestpath_info.set(ex.path_info)

def get_input(input_text_field, input_window):
    """
    Processes user input for custom exchange rates from a text field.
    Validates and parses the input data, then updates the currencies with the new custom rates.

    Args:
        input_text_field (tk.Text): The text field widget where the user inputs the exchange rate data.
        input_window (tk.Tk): The tkinter window containing the input text field.
    """
    exchange_rates_custom = {}

    # Fetch the text from the input field and store it in a variable
    user_input = input_text_field.get("1.0", "end-1c")  # Get all the text in the text field

    lines = user_input.strip().split('\n')

    # First line is the number of rows/columns
    num_columns = int(lines[0].split(',')[0].strip())

    if num_columns < 2 or num_columns > 5:
        messagebox.showerror("Input Error", "Please input between 2 and 5 currencies")

    # The rest of the first line are the labels for the rows/columns
    labels = [label.strip() for label in lines[0].split(',')[1:]]

    # Ensure that the number of labels matches the number of columns
    if len(labels) != num_columns:
        messagebox.showerror("Input Error", "Number of labels does not match the number of columns")

    # Process the exchange rate data
    for i in range(1, num_columns + 1):
        rates = list(map(float, lines[i].strip().split()))
        exchange_rates_custom[labels[i - 1]] = {}

        for j in range(num_columns):
            if i - 1 != j:  # Skip self-reference
                exchange_rates_custom[labels[i - 1]][labels[j]] = rates[j]

    input_window.destroy()
    set_custom_currencies(exchange_rates_custom)

def create_own_matrix():
    """
    Creates a GUI window for user input of custom exchange rates.
    Provides instructions and a text field for entering data.
    Includes a submit button to process the input and update currencies.
    """
    input_window = tk.Tk()
    input_window.geometry('400x500')
    input_window.title("Input Your Own")

    inputFrame = tk.Frame(input_window)
    inputFrame.pack(pady=20)

    # Label to prompt the user
    instruction_label = tk.Label(
        inputFrame,
        text=(
            "Please enter data formatted similar to the example below:\n\n"
            "3, A, B, C\n"
            "1 0.651 0.581\n"
            "1.531 1 0.952\n"
            "1.711 1.049 1\n"
        ),
        # Align text to the left
        justify="left"
    )
    instruction_label.pack(pady=10)

    # Text field for the user to input data
    input_text_field = tk.Text(inputFrame, height=10, width=40)
    input_text_field.pack(pady=10)

    # Button to retrieve the entered text
    submit_button = tk.Button(inputFrame, text="Submit", command=lambda: get_input(input_text_field, input_window))
    submit_button.pack(pady=10)

    # Start the GUI loop
    input_window.mainloop()

# Initialize Tkinter window
root = tk.Tk()
root.geometry('1200x550')
root.title("Currency Exchange")

# Define available currencies
available_currencies = ['USD', 'NZD', 'AUD', 'EUR', 'JPY', 'THB', 'INR', 'BOB', 'BRL', '']

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

# Bind the trace method to each currency variable to update the selected_currencies list on change
currency1.trace('w', update_selected_currencies)
currency2.trace('w', update_selected_currencies)
currency3.trace('w', update_selected_currencies)
currency4.trace('w', update_selected_currencies)
currency5.trace('w', update_selected_currencies)

# Create the dropdowns in the top_left_frame and place them
for idx, selector in enumerate(currency_selectors):
    selector.grid(row=idx, column=0, padx=5, pady=5)

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

# Bind the selection event to the update functions
currency_dropdown_1.bind("<<ComboboxSelected>>", on_dropdown_select)
currency_dropdown_2.bind("<<ComboboxSelected>>", on_dropdown_select)

# Create and place the button in the bottom-left frame
arbitrage_button = ttk.Button(bottom_left_frame, text="Case 1: No Arbitrage, Direct Path", command=lambda: set_custom_currencies(exchange_rates_no_arbitrage_direct))
arbitrage_button.grid(row=1, column=0, padx=10, pady=10, sticky="w")

arbitrage_button2 = ttk.Button(bottom_left_frame, text="Case 2: No Arbitrage, Indirect Path", command=lambda: set_custom_currencies(exchange_rates_no_arbitrage_indirect))
arbitrage_button2.grid(row=2, column=0, padx=10, pady=10, sticky="w")

reset_button = ttk.Button(bottom_left_frame, text="Reset", command=lambda: reset_gui())
reset_button.grid(row=3, column=0, padx=10, pady=10, sticky="w")

input_button = ttk.Button(root, text="Input Custom Matrix", command=create_own_matrix)
input_button.grid(row=4, column=0, padx=10, pady=10, sticky="w")

# Refresh matrix view
update_matrix_view()

# Run the application
root.mainloop()
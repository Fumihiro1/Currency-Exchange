import tkinter as tk
from tkinter import messagebox, ttk
import requests
import numpy as np


# Function to fetch exchange rates from the API
def fetch_exchange_rates(currencies):
    rates = {}
    try:
        for base_currency in currencies:
            response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{base_currency.strip()}")
            response.raise_for_status()  # Check for request errors
            all_rates = response.json().get('rates', {})

            # Filter rates to include only those in the 'currencies' list
            filtered_rates = {currency: rate for currency, rate in all_rates.items() if
                              currency in currencies and currency != base_currency}

            rates[base_currency] = filtered_rates
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

        # update dropdowns
        update_first_dropdown()
        update_second_dropdown()

        # update best path
        best_conversion_rate(selected_currency_1.get(), selected_currency_2.get(), edges, rates)


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

# add color to frames
bottom_left_frame.config(background="white")
bottom_right_frame.config(background="white")

# Create the title for dropdown selectors
dropdown_title = tk.Label(top_left_frame, text="Currencies", font=('Arial', 12, 'bold'))
dropdown_title.grid(row=0, column=0, padx=5, pady=5, sticky="n")

# Create dropdown selectors for currencies
currency1 = tk.StringVar(value=available_currencies[0])  # set to first 5 available currencies
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

# matrix view title
matrix_title = tk.Label(top_right_frame, text="Exchange Rate Matrix", font=('Arial', 12, 'bold'))
matrix_title.grid(row=0, column=0, columnspan=6, padx=5, pady=5, sticky="w")

# set up headers and initialize matrix cells
conversion_rates[0][0] = tk.Label(top_right_frame, text="From/To", borderwidth=1, relief="solid", width=15, height=2)
conversion_rates[0][0].grid(row=1, column=0, sticky="nsew")

for i in range(5):
    conversion_rates[0][i + 1] = tk.Label(top_right_frame, text="N/A", borderwidth=1, relief="solid", width=15,
                                          height=2)
    conversion_rates[0][i + 1].grid(row=1, column=i + 1, sticky="nsew")  # Top row headers

    conversion_rates[i + 1][0] = tk.Label(top_right_frame, text="N/A", borderwidth=1, relief="solid", width=15,
                                          height=2)
    conversion_rates[i + 1][0].grid(row=i + 2, column=0, sticky="nsew")  # Left column headers

    for j in range(5):
        conversion_rates[i + 1][j + 1] = tk.Label(top_right_frame, text="N/A", borderwidth=1, relief="solid", width=15,
                                                  height=2)
        conversion_rates[i + 1][j + 1].grid(row=i + 2, column=j + 1, sticky="nsew")  # Main matrix

# Label for arbitrage information
arbitrage_info = tk.StringVar(value="No arbitrage opportunity detected.")
arbitrage_label = tk.Label(bottom_left_frame, textvariable=arbitrage_info, wraplength=400, background="white",
                           font=('Arial', 10))
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
bestpath_label = tk.Label(bottom_right_frame, textvariable=bestpath_info, background="white",
                           font=('Arial', 10))
bestpath_label.grid(row=2, column=0)

# Bind the selection event to the update functions
selected_currency_1.trace('w', update_second_dropdown)
selected_currency_2.trace('w', update_first_dropdown)

exchange_rates_no_arbitrage = {
    'USD': {
        'EUR': 0.85,
        'JPY': 110.0,
        'GBP': 0.75,
        'AUD': 1.40
    },
    'EUR': {
        'USD': 1.18,  # 1 / 0.85
        'JPY': 129.41,  # (1.18 * 110.0)
        'GBP': 0.88,
        'AUD': 1.64
    },
    'JPY': {
        'USD': 0.0091,  # 1 / 110.0
        'EUR': 0.0077,  # 1 / 129.41
        'GBP': 0.0068,
        'AUD': 0.0127
    },
    'GBP': {
        'USD': 1.33,  # 1 / 0.75
        'EUR': 1.14,  # 1 / 0.88
        'JPY': 147.06,  # (1.33 * 110.0)
        'AUD': 1.85
    },
    'AUD': {
        'USD': 0.71,  # 1 / 1.40
        'EUR': 0.61,  # 1 / 1.64
        'JPY': 78.74,  # (0.71 * 110.0)
        'GBP': 0.54054  # Reciprocal of 1.85
    }
}

# Add a button to set the selected currencies to those in the exchange_rates_no_arbitrage dictionary
def set_arbitrage_currencies():
    # Use currencies from exchange_rates_no_arbitrage to update the dropdowns
    available_currencies_in_dict = list(exchange_rates_no_arbitrage.keys())

    # Set the first five available currencies from the dictionary into the dropdowns
    if len(available_currencies_in_dict) >= 5:
        currency1.set(available_currencies_in_dict[0])
        currency2.set(available_currencies_in_dict[1])
        currency3.set(available_currencies_in_dict[2])
        currency4.set(available_currencies_in_dict[3])
        currency5.set(available_currencies_in_dict[4])

        # Update the selected currencies list
        update_selected_currencies()
        update_matrix_view()

# Create and place the button in the bottom-left frame
arbitrage_button = ttk.Button(bottom_left_frame, text="Set Arbitrage Currencies", command=set_arbitrage_currencies)
arbitrage_button.grid(row=1, column=0, padx=10, pady=10, sticky="w")

# refresh matrix view
update_matrix_view()

# Run the application
root.mainloop()
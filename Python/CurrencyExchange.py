import requests

from_currency = str(
    input("Enter in the currency you'd like to convert from: ")).upper()

to_currency = str(
    input("Enter in the currency you'd like to convert to: ")).upper()

amount = float(input("Enter in the amount of money: "))

response = requests.get(
    f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}")

print(
    f"{amount} {from_currency} is {response.json()['rates'][to_currency]} {to_currency}")

class Edge:
    def __init__(self, start, destination, weight):
        self.start = start
        self.destination = destination
        self.weight = weight

class Graph:
    def __init__(self, noVertices, edges):
        self.noVertices = noVertices
        self.edges = edges

def inputType():
    print('1. APi')
    print('2. Custom')
    type = input();

    if input == 1:
        print('API chosen')
        return input;
    elif input == 2:
        print('Custom chosen')
        return input;
    else:
        print('Try again')
        return inputType()
    
    

from py_exchangeratesapi import Api

api = Api('32079035db98992849d78653cbdeadba')

api.get_rates()

print(api.get_rate(target='GBP'))


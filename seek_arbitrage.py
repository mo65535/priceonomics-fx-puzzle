
import collections
import itertools
import json
import requests


def dbg_print(*args, **kwargs):
    return # !!! Uncomment this line to suppress debug ouput
    print(*args, **kwargs)


def get_rates_json(url):
    """Query Priceonomics' exchange rate API endpoint and decode response"""

    # !!! Use these values during testing, so we don't always hit their server.
    return '{"USD_JPY": "92.4744496", "USD_USD": "1.0000000", "JPY_EUR": "0.0083267", "BTC_USD": "132.5605536", "JPY_BTC": "0.0000889", "USD_EUR": "0.7020942", "EUR_USD": "1.1553725", "EUR_JPY": "118.3771999", "JPY_USD": "0.0107040", "BTC_BTC": "1.0000000", "EUR_BTC": "0.0101155", "BTC_JPY": "13569.7220719", "JPY_JPY": "1.0000000", "BTC_EUR": "97.7800300", "EUR_EUR": "1.0000000", "USD_BTC": "0.0074929"}'

    # Read JSON from Priceonomics API.
    req = requests.request('GET', url)

    # Error checking to see if request succeeded.
    #   ...
    # Get text encoding from response header (for now, assume it will always be UTF-8).
    #   ...

    json_str = req.content.decode('UTF-8')
    print('Received the following JSON data on {}:'.format(req.headers['Date']))
    print(json.dumps(json.loads(json_str), indent=4, separators=(',', ': ')))

    return json_str


def parse_rates(json_str):
    """Given a string of JSON indicating the exchange rates,
    generate a map of exchange rates such that:

    rates['USD']['JPY'] = the USD to JPY exchange rate, etc.
    """
    str_map = json.loads(json_str)
    # This map has string-valued keys that match the API JSON, e.g. 'USD_JPY'

    rates = collections.defaultdict(dict) # Dict of dicts

    #print('### Building rates_map')
    for key in str_map.keys():
        #print('### {}'.format(key))

        curr_from, curr_to = key.split('_')
        if curr_to != curr_from:
            rates[curr_from][curr_to] = float(str_map[key])
        #else do nothing if it's the 'conversion' from one currency to the same.

    dbg_print('\n### parsed rates = ')
    dbg_print(json.dumps(rates, sort_keys=True, indent=4, separators=(',', ': ')))

    return rates


def find_all_arbitrage_loops(rates):
    """For each possible starting currency, find all arbitrage loops, which will
    consist of 1 to N-1 exchanges through other currencies, before a final
    exchange back into the starting currency."""
    symbols = set(rates.keys())
    dbg_print('\n### symbols = {}'.format(symbols))

    arbitrage_loops = []

    for symb in symbols: # Loop over all possible starting currencies.
        dbg_print('\n### Starting from {}:'.format(symb))

        for nex in range(1, len(symbols)): # nex = number of exchanges in loop
            perms = itertools.permutations((symbols-set([symb])), r=nex)

            for p in perms: # Test all permutations of exchanges.
                seq = (symb,) + p + (symb,)
                dbg_print('### {}'.format(seq), end=' ')

                coeffs = []
                product = 1
                for i in range(len(seq)-1):
                    coeff = rates[seq[i]][seq[i+1]]
                    coeffs.append(coeff)
                    product *= coeff

                dbg_print(coeffs, end=' ')
                dbg_print('product = {}'.format(product))

                if product > 1: # If value was increased rather than decreased
                    arbitrage_loops.append((seq, coeffs, product))

    return sorted(arbitrage_loops, key=lambda loop: loop[2], reverse=True)


def main():
    json_str = get_rates_json('http://fx.priceonomics.com/v1/rates/')
    rates = parse_rates(json_str)
    arbitrage_loops = find_all_arbitrage_loops(rates)

    if arbitrage_loops:
        """ !!! Use the currency exchange broker's API to place trades based on
        the best loop that we found.

        #place_trades(arbitrage_loops[0])
        """

        print('Arbitrage loops:')
        for loop in arbitrage_loops:
            print(loop)
    else:
        print('No arbitrage loops found.')


# Here is the entry point when the script is run from the command line.
if __name__ == '__main__':
    main()

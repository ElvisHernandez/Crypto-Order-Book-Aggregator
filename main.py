import urllib3
import json
import sys

http = urllib3.PoolManager()

complete_order_book = { "bids": [], "asks": [] }

api_urls = [
    'https://api.pro.coinbase.com/products/BTC-USD/book?level=2',
    'https://api.gemini.com/v1/book/BTCUSD',
    'https://api.kraken.com/0/public/Depth?pair=XBTUSD'
]

def load_api_data(url):
    res = http.request('GET', url)
    json_payload = json.loads(res.data.decode('utf-8'))
    return json_payload

def aggregate_order_book_bids_and_asks(order_book):
    for bid in order_book['bids']:
        complete_order_book['bids'].append({ "price": bid[0], "amount": bid[1] })

    for ask in order_book['asks']:
        complete_order_book['asks'].append({ "price": ask[0], "amount": ask[1] })

def aggregate_complete_order_book():

    coinbase_order_book, gemini_order_book, kraken_order_book = [load_api_data(url) for url in api_urls]

    # merge order books
    aggregate_order_book_bids_and_asks(coinbase_order_book)
    aggregate_order_book_bids_and_asks(kraken_order_book['result']['XXBTZUSD'])
    complete_order_book['bids'] = complete_order_book['bids'] + gemini_order_book['bids']
    complete_order_book['asks'] = complete_order_book['asks'] + gemini_order_book['asks']

    complete_order_book['bids'].sort(key=lambda bid: float(bid['price']), reverse=True)
    complete_order_book['asks'].sort(key=lambda ask: float(ask['price']))

def calculate_price(is_buying, amount):

    total_price = 0
    total_amount = amount

    asksOrBids = complete_order_book['asks'] if is_buying else complete_order_book['bids']

    for askOrBid in asksOrBids:

        price = float(askOrBid['price'])
        amount = float(askOrBid['amount'])

        if (amount < total_amount):

            total_price += price * amount
            total_amount -= amount
        else:
            return price * total_amount + total_price

try:

    buy_and_sell_amount = float(sys.argv[1])

    if (buy_and_sell_amount < 0):
        buy_and_sell_amount = 10
except:
    buy_and_sell_amount = 10

aggregate_complete_order_book()

buying_price = calculate_price(True, buy_and_sell_amount)
selling_price = calculate_price(False, buy_and_sell_amount)

print ("The buying price for {} BTC is {}".format(buy_and_sell_amount, buying_price))
print ("The selling price for {} BTC is {}".format(buy_and_sell_amount, selling_price))

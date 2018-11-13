from alert import Alert

class PricePoint(Alert):
    # TODO: These need to access Exchange, Pair etc. from the data_api folder.
    def __init__(self, exchange: str, pair: str, start_price: float, direction: str):
        assert(direction == 'up' or direction == 'down')

        self.exchange = exchange
        self.pair = pair
        self.start_price = start_price
        self.direction = direction

    # TODO: Have a common interface for passing in continuous data
    def trigger(self, trade) -> bool:
        if trade['tags']['pair'] == self.pair or True: # TODO TODO: Remove True
            if self.direction == 'up':
                if float(trade['fields']['price']) > self.start_price:
                    return True
            elif self.direction == 'down':
                if float(trade['fields']['price']) < self.start_price:
                    return True

        return False


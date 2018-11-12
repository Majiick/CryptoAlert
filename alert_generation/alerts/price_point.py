from alert import Alert

class PricePoint(Alert):
    # TODO: These need to access Exchange, Pair etc. from the data_api folder.
    def __init__(self, price: float, direction: str):
        assert(direction == 'up' or direction == 'down')


    def trigger(self) -> bool:
        pass

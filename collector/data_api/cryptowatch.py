from data_api import DataAPI, Pair, Exchange

class Cryptowatch(DataAPI):
    def get_last_price(pair: Pair, exchange: Exchange) -> float:
        pass

C = Cryptowatch()
C.get_last_price(Pair('btcusd'))

import urllib.parse

class URLs:
    base_url = f"ebinex.com"
    ws = f"wss://ws.{base_url}/ws"         
    api_base_url = f"api.{base_url}" 

    @property
    def parameters(self):
        return f"https://{self.api_base_url}/parameters"

    @property
    def list_accounts(self):
        return f"https://{self.api_base_url}/users/listAccounts"

    @property
    def available_symbols(self):
        return f"https://{self.api_base_url}/orders/availableSymbols"

    @property
    def login(self):
        return f"https://{self.base_url}/login"

    @property
    def aggregated_trades(self):
        return f"https://{self.api_base_url}/dataProvider/aggregatedTrades"

    @property
    def ws_info(self):
        url = urllib.parse.urlparse(self.ws)
        return f"https://{url.netloc}/ws/info"

    @property
    def orders(self):
        return f"https://{self.api_base_url}/orders"

    @property
    def ws_host(self):
        parsed_url = urllib.parse.urlparse(self.ws)
        return parsed_url.netloc


class Events:
    BOOK = "book"
    TRADE = "trade"
    USER_BALANCE = "user_balance"
    SINGLE_USER_ORDER = "single_user_order"

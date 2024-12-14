class URLs:
    ws = 'wss://ws.ebinex.com/ws' 
    listAccounts = 'https://api.ebinex.com/users/listAccounts'  
    availableSymbols = 'https://api.ebinex.com/orders/availableSymbols'
    parameters = 'https://api.ebinex.com/parameters'
    originUrl = 'https://ebinex.com'     
    login = 'https://ebinex.com/login'
    wsInfo = 'https://ws.ebinex.com/ws/info'
    orders = 'https://api.ebinex.com/orders'
    aggregatedTrades = 'https://api.ebinex.com/dataProvider/aggregatedTrades'

    @property
    def ws_host(self):
        import urllib.parse
        parsed_url = urllib.parse.urlparse(self.ws)
        return parsed_url.netloc
    
class Events:
    TRADE = 'trade'
    USER_BALANCE = 'user_balance'
    SINGLE_USER_ORDER = 'single_user_order'

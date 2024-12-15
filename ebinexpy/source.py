import itertools
import threading
import numpy as np
import urllib.parse
import os, base64, time
import atexit, requests
from typing import (
    Any,
    Dict,
    List,
    Tuple,
    Union,
    Callable,
)

import iykyk as tp
from utils import sockthis
from varname import nameof
from signals import Signals
from security import Security
from user_agent import UserAgent
from strings import Events, URLs


class Ebinex:
    def __init__(self, username: str, password: str, keep=False, **kwargs) -> None:
        atexit.register(self.close)

        if not isinstance(username, str) or not isinstance(password, str):
            errors = []
            if not isinstance(username, str):
                errors.append(nameof(username))
            if not isinstance(password, str):
                errors.append(nameof(password))
                raise AttributeError(f'It\'s like they\'re missing that spark or something: {", ".join(errors)}')

        self.username = username
        self.password = password
        self.keep = keep

        self.account_id: Union[str, None] = None
        self.access_token: Union[str, None] = None

        self.subs: List[str] = []
        self.balance: tp.EbinexWebSocketBalance
        self.ords: Dict[str, tp.EbinexOrder] = {}
        self.trades: Dict[str, List[tp.EbinexTrade]] = {}

        self.urls = URLs()
        self.lyap = time.time()
        self.signals = Signals()
        self.requests = requests.Session()
        self.config: tp.EbinexConfig = kwargs.get("config")
        self.security = Security(kwargs.get("vault", tp.DEFAULT_VAULT))

        logger = kwargs.get("logger")
        if not logger:
            log_dir = os.path.join(tp.PACKAGE_DIR, "logs")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            import logging
            from datetime import datetime

            today_date = datetime.now().strftime("%Y-%m-%d")
            logpath = os.path.join(log_dir, f"{today_date}.log")
            logging.basicConfig(
                filename=logpath,
                filemode="a",
                format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
                level=logging.INFO,
            )

        credentials = self.security.load_credentials()
        if credentials:
            account_id = credentials.account_id
            access_token = credentials.access_token
            self.config = self.config or credentials.config

        else:
            try:
                import winreg
                from captcha import Captcha
                from selenium.webdriver.common.by import By
                from selenium.webdriver import Chrome as WebDriver
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.chrome.options import Options as DriverOpts
                from selenium.webdriver.chrome.service import Service as DriverService

                try:
                    registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
                        executable_path, _ = winreg.QueryValueEx(key, "")
                except FileNotFoundError:
                    pass

                options = DriverOpts()
                options.add_argument("--incognito")
                options.add_argument("--no-sandbox")
                options.add_argument("--headless=new")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument(f"user-agent={UserAgent.random()}")
                service = DriverService(executable_path=executable_path)
                driver = WebDriver(options=options, keep_alive=True)

                driver.get(self.urls.login)
                WebDriverWait(driver, 10).until(lambda d: "Entrar" in d.page_source)
                driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(self.username)
                driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys(self.password)
                driver.find_element(By.NAME, "keepLoggedIn").click()
                Captcha(driver).resolve()
                driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

                WebDriverWait(driver, 30).until(lambda d: d.execute_script('return localStorage.getItem("environment") !== null;'))

                account_id = driver.execute_script('return localStorage.getItem("accountId");')
                access_token = driver.execute_script('return localStorage.getItem("accessToken");')
            finally:
                driver.quit()

        if account_id and access_token:
            self.account_id = account_id
            self.access_token = access_token

            if self.keep:
                self.clapback()

        try:
            assert access_token is not None
        except AssertionError as ext:
            raise ConnectionError(f"where the hell is the {nameof(access_token)}") from ext

        server_port = np.random.randint(100, 999)

        letters = np.array(list("abcdefghijklmnopqrstuvwxyz"))
        numbers = np.array(list("0123456789"))

        number_count = np.random.randint(0, 2 + 1)
        letter_count = 8 - number_count

        letter_part = np.random.choice(letters, size=letter_count, replace=True)
        number_part = np.random.choice(numbers, size=number_count, replace=True)

        result = np.concatenate((letter_part, number_part))
        np.random.shuffle(result)

        session_key = "".join(result)

        url_parts = [self.urls.ws, str(server_port), session_key, "websocket"]
        """Composed of a dynamic args, a port and a session key (a length of 8 and 2 numeric chars)"""

        base_url = urllib.parse.urljoin("/".join(url_parts), "")

        params = {
            "authorization": access_token,
            "accountId": account_id,
        }

        url = f"{base_url}?{urllib.parse.urlencode(params)}"

        random_bytes = os.urandom(16)
        websocket_key = base64.b64encode(random_bytes).decode("utf-8")

        header = {
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9,es-ES;q=0.8,es;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "Upgrade",
            "Host": self.urls.ws_host,
            "Origin": self.urls.originUrl,
            "Pragma": "no-cache",
            "Sec-WebSocket-Key": websocket_key,
            "Sec-WebSocket-Version": "13",
            "Upgrade": "websocket",
            "User-Agent": UserAgent.random(),
        }

        from client import StompClient
        from client.frame import Sigma

        def on_connected(client: StompClient):
            """Method to process websocket open"""
            symbol = self.symbol
            timeframe = self.timeframe
            environment = self.environment

            destinations = [
                "/user/topic/{}".format(environment.name),
                r"/topic/graph\\c{}".format(symbol),
                r"/topic/book\\c{}\\c{}\\c{}".format(environment.name, symbol, timeframe.name),
                "/topic/execute",
            ]

            for index, destination in enumerate(destinations):
                sub_id = client.subscribe(destination)
                if index == 0 or index == 2:
                    self.subs.append(sub_id)

            def ping_interval():
                for i in itertools.count():
                    cyap = time.time()
                    if cyap - self.lyap >= 10:
                        payload = f'["{Sigma.LF}"]'
                        client.ws.send(payload)
                        self.lyap = cyap

            ptr = threading.Thread(target=ping_interval)
            ptr.name = nameof(ping_interval)
            ptr.daemon = True
            ptr.start()

        def on_open(client: StompClient):
            """Method to process Stomp open"""
            pass

        def on_close(client: StompClient, code: int):
            """Method to process Stomp close"""
            pass

        @sockthis
        def on_message(client: StompClient, message: Union[Dict, List]):
            """Method to process Stomp messages"""
            if isinstance(message, dict):
                data: Dict[str, Any] = message.get("data", {})
                payload: Dict[str, Any] = data.get("payload", {})

                match data.get("event", None):
                    case Events.TRADE:
                        symbol = self.symbol
                        trade = tp.EbinexWebSocketTrade.from_dict(payload)
                        if symbol not in self.trades:
                            self.trades[symbol] = []
                        self.trades[symbol].append(trade)
                        self.signals.trade.put(self.trades)

                    case Events.USER_BALANCE:
                        self.balance = tp.EbinexWebSocketBalance.from_dict(payload)
                        self.signals.balance.put(self.balance)

                    case Events.SINGLE_USER_ORDER:
                        order = tp.EbinexOrder.from_dict(payload)
                        self.ords[order.id] = order
                        self.signals.order.put(order)

        @sockthis
        def on_error(client: StompClient, error: str):
            """Method to process Stomp errors"""
            pass

        self.stomp = StompClient(
            url,
            on_connected=on_connected,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open,
            header=header,
        )
        """Use me if you know what you're doing, otherwise don't piss me off"""

        self.stomp.connect()
        self.signals.trade.get()
        self.signals.balance.get()

    @property
    def connected(self) -> bool:
        """Determine if the token is still alive"""
        assert self.access_token is not None
        assert self.account_id is not None

        params = {
            "authorization": self.access_token,
            "accountId": self.account_id,
            "t": int(time.time() * 1000),
        }

        response = self.requests.get(self.urls.wsInfo, params=params)
        alive_token = tp.EbinexWebSocketInfo(response.json()).websocket
        return alive_token and self.stomp.connected.is_set()

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accountid": self.account_id,
            "User-Agent": UserAgent.random(),
        }

    @property
    def account(self):
        response = self.requests.get(self.urls.listAccounts, headers=self.headers)
        for account in response.json():
            environment = getattr(self.config, "environment", tp.Environment.TEST)
            if account.get("environment") == environment.name:
                return tp.EbinexAccount.from_dict(account)
        return None

    @property
    def symbols(self):
        response = self.requests.get(self.urls.availableSymbols, headers=self.headers)
        return [tp.EbinexSymbol.from_dict(symbol) for symbol in response.json()]

    @property
    def parameters(self):
        response = self.requests.get(self.urls.parameters, headers=self.headers)
        return tp.EbinexParameters.from_list(response.json())

    @property
    def environment(self):
        return self.account.environment

    @property
    def symbol(self) -> str:
        if not isinstance(self.config, tp.EbinexConfig):
            return next(iter(self.symbols)).symbol
        return self.config.symbol

    @property
    def timeframe(self) -> tp.Timeframe:
        if not isinstance(self.config, tp.EbinexConfig):
            return tp.Timeframe[self.parameters.default_candle_timeframe]
        return self.config.timeframe

    def order(
        self, amount: int, direction: tp.Direction
    ) -> Tuple[tp.EbinexOrder, Callable[[List[tp.Statuses]], None]]:
        """
        Places an order for a specified amount and direction.

        This method retrieves the last trade for the symbol, constructs an order,
        sends it to the execution topic, and returns the order information.
        The callable function provided will block the thread until the order status
        matches the default status or the one specified as an argument. Upon
        unblocking, it updates the order information.

        :param amount: The quantity of the asset to order.
        :param direction: The direction of the trade (BULL or BEAR).

        :return: A tuple containing:
            - An instance of EbinexOrder representing the placed order.
            - A function that waits for the order status to match specified statuses.
        """
        trades = self.trades.get(self.symbol)
        asset = self.balance.asset.upper()
        account_id = self.account.id
        timeframe = self.timeframe
        last_trade = trades[-1]
        symbol = self.symbol

        opts = tp.EbinexTrade(
            account_id=account_id,
            price=round(last_trade.price, 3),
            timeframe=timeframe,
            direction=direction,
            symbol=symbol,
            amount=amount,
            asset=asset,
        )

        payload = opts.to_dict()
        body = self.stomp.dumpy(payload)
        self.stomp.send("/topic/execute", body=body, headers={"content-length": 144})

        order: tp.EbinexOrder = self.signals.order.get()

        def wait(until: List[tp.Statuses] = [tp.Statuses.OPEN]):
            event = threading.Event()

            def opawaiter():
                if any(self.ords[order.id].status == status for status in until):
                    event.set()
                else:
                    order_timer = threading.Timer(1, opawaiter)
                    order_timer.name = f"opawaiter-{order.id}"
                    order_timer.daemon = True
                    order_timer.start()

            resolve = threading.Thread(target=opawaiter)
            resolve.name = f"order-{order.id}"
            resolve.daemon = True
            resolve.start()

            event.wait()

            cap_order = self.ords.get(order.id)
            order.update(cap_order)

        return order, wait

    def change_environment(self, environment: tp.Environment):
        if self.environment == environment:
            return

        for sub_id in self.subs:
            self.stomp.unsubscribe(sub_id)
        self.subs.clear()

        destinations = [
            f"/user/topic/{environment.name}",
            r"/topic/book\\c{}\\c{}\\c{}".format(environment.name, self.symbol, self.timeframe.name),
        ]

        for destination in destinations:
            sub_id = self.stomp.subscribe(destination)
            self.subs.append(sub_id)

        self.signals.balance.get()
        setattr(self.config, nameof(self.environment), environment)

    def orders(
        self,
        timeframes: List[tp.Timeframe],
        symbols: List[str],
        statuses: List[tp.Statuses],
        page: int = 0,
        size: int = 10,
    ):
        params = {
            "candleTimeFrames": ",".join([t.name for t in timeframes]),
            "symbols": ",".join(symbols),
            "statuses": ",".join([s.name for s in statuses]),
            "page": page,
            "size": size,
        }

        url = f"{self.urls.orders}?{urllib.parse.urlencode(params)}"
        response = self.requests.get(url, headers=self.headers)

        return response.json()

    def aggregated_trades(
        self, symbol: str, timeframe: tp.Timeframe, fm: int, to: int, limit: int = 1000
    ) -> List[tp.EbinexPriceData]:
        params = {
            "symbol": symbol,
            "candleTimeFrame": timeframe.name,
            "from": fm,
            "to": to,
            "limit": limit,
        }

        url = f"{self.urls.aggregatedTrades}?{urllib.parse.urlencode(params)}"
        response = self.requests.get(url, headers=self.headers)

        return [tp.EbinexPriceData(data) for data in response.json()]

    def clapback(self):
        """Ignore me, what I do doesn't matter to you"""
        credentials = tp.Credentials(
            access_token=self.access_token,
            account_id=self.account_id,
            config=tp.EbinexConfig(
                symbol=self.symbol,
                timeframe=self.timeframe,
                environment=self.environment,
            ),
        )

        self.security.save_credentials(**credentials.to_dict())

    def close(self):
        try:
            self.clapback()
            self.stomp.ws.close()
        except AttributeError:
            pass

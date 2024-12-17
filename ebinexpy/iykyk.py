"""if you know, you know, types basically"""

import os
from enum import Enum, auto
from selenium.webdriver import Chrome
from datetime import datetime, timedelta
from selenium.common.exceptions import NoSuchElementException as NSEE
from typing import Union, Optional, Any, Dict, List, Callable, TYPE_CHECKING

WebDriver = Chrome
NoSuchElementException = NSEE

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FUNC: Callable[..., None] = lambda *args, **kwargs: None

DEFAULT_VAULT = os.path.join(PACKAGE_DIR, "vault.json")
DEFAULT_EXPIRATION = (datetime.now() + timedelta(days=30)).timestamp()

if TYPE_CHECKING:
    from ebinexpy.source import Ebinex
else:
    Ebinex = Any


class Direction(Enum):
    BULL = auto()
    BEAR = auto()


class Timeframe(Enum):
    M1 = 1
    M5 = 5
    M15 = 15

    def __eq__(self, other: Optional["Timeframe"]):
        if hasattr(other, "name"):
            return self.name == other.name
        return NotImplemented

    def __ne__(self, other: Optional["Timeframe"]):
        if hasattr(other, "name"):
            return self.name != other.name
        return NotImplemented

class Statuses(Enum):
    WIN = auto()
    LOSE = auto()
    OPEN = auto()
    PENDING = auto()
    CANCELED = auto()
    REFUNDED = auto()

    def __eq__(self, other: Optional["Statuses"]):
        """
        Same shit happens here, lots of mosquitoes in my room so I'll just do
        the same as with Environment and go to sleep.
        """
        if hasattr(other, "name"):
            return self.name == other.name
        return NotImplemented

    def __ne__(self, other: Optional["Statuses"]):
        if hasattr(other, "name"):
            return self.name != other.name
        return NotImplemented
    
class Environment(Enum):
    REAL = auto()
    TEST = auto()

    def __eq__(self, other: Optional["Environment"]):
        """
        This method has been overriden (today, twenty-three days after the first year of the eleventh
        mandate of the bastard Nicolás Maduro) to improve the comparison of instances of this enum.

        I'm too drunk to find the bug.

        It may be a Python bug or mine (most likely) if I've forgotten something, please let me know.

        As a result, I've opted to implement the equality check based on the names of the enum members
        and although it's not ideal due to runtime risks (no fella, you won't be hacked) such as
        type errors in some functions, at least it works.

        To illustrate, see an example involving two classes and the boolean result of their
        comparison at the following [link](https://pastebin.com/AfqYLkvd).
        """
        if hasattr(other, "name"):
            return self.name == other.name
        return NotImplemented
    
    def __ne__(self, other: Optional["Environment"]):
        if hasattr(other, "name"):
            return self.name != other.name
        return NotImplemented

class Credentials:
    def __init__(
        self,
        sign: str,
        account_id: str,
        access_token: str,
        config: "EbinexConfig",
        expiration=DEFAULT_EXPIRATION,
    ):
        self.sign = sign    
        self.account_id = account_id
        self.access_token = access_token
        self.config = config
        self.expiration = expiration

    def to_dict(self) -> Dict:
        return {
            "sign": self.sign,
            "account_id": self.account_id,
            "access_token": self.access_token,
            "config": self.config.to_dict(),
            "expiration": self.expiration,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Credentials":
        return cls(
            sign=data.get("sign"),
            account_id=data.get("account_id"),
            access_token=data.get("access_token"),
            config=EbinexConfig.from_dict(data.get("config", {})),
            expiration=data.get("expiration"),
        )


class EbinexBook:
    class Investment:
        def __init__(self, id: str, accountId: str, invest: float, createdAt: int):
            self.id = id
            self.accountId = accountId
            self.invest = invest
            self.createdAt = createdAt

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> "EbinexBook.Investment":
            return cls(
                id=data["id"],
                accountId=data["accountId"],
                invest=data["invest"],
                createdAt=data["createdAt"],
            )

    def __init__(self, timeframe: Timeframe, symbol: str, bull: List[Investment], bear: List[Investment]):
        self.timeframe = timeframe
        self.symbol = symbol
        self.bull = bull
        self.bear = bear

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EbinexBook":
        bull_investments = [EbinexBook.Investment.from_dict(b) for b in data["bull"]]
        bear_investments = [EbinexBook.Investment.from_dict(b) for b in data["bear"]]
        return cls(
            timeframe=Timeframe[data["candleTimeFrame"]],
            symbol=data["symbol"],
            bull=bull_investments,
            bear=bear_investments,
        )


class EbinexOrder:
    def __init__(
        self,
        id: str,
        user_email: str,
        account_id: str,
        environment: Environment,
        candle_time_frame: str,
        candle_start_time: int,
        symbol: str,
        direction: str,
        price: float,
        cop: float,
        ccp: float,
        asset: str,
        invest: float,
        fee_rate: float,
        used_bonus: float,
        fees: float,
        refund: float,
        accept: float,
        profit: float,
        loss: float,
        platform_liquidity: float,
        status: Statuses,
        referral_id: Optional[str],
        referral_commission: Optional[float],
        created_at: int,
        created_at_broker_time: int,
        influencer_order: bool,
    ):

        self.id = id
        self.user_email = user_email
        self.account_id = account_id
        self.environment = environment
        self.candle_time_frame = candle_time_frame
        self.candle_start_time = candle_start_time
        self.symbol = symbol
        self.direction = direction
        self.price = price
        self.cop = cop
        self.ccp = ccp
        self.asset = asset
        self.invest = invest
        self.fee_rate = fee_rate
        self.used_bonus = used_bonus
        self.fees = fees
        self.refund = refund
        self.accept = accept
        self.profit = profit
        self.loss = loss
        self.platform_liquidity = platform_liquidity
        self.status = status
        self.referral_id = referral_id
        self.referral_commission = referral_commission
        self.created_at = created_at
        self.created_at_broker_time = created_at_broker_time
        self.influencer_order = influencer_order

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_email": self.user_email,
            "account_id": self.account_id,
            "environment": self.environment.name,
            "candle_time_frame": self.candle_time_frame,
            "candle_start_time": self.candle_start_time,
            "symbol": self.symbol,
            "direction": self.direction,
            "price": self.price,
            "cop": self.cop,
            "ccp": self.ccp,
            "asset": self.asset,
            "invest": self.invest,
            "fee_rate": self.fee_rate,
            "used_bonus": self.used_bonus,
            "fees": self.fees,
            "refund": self.refund,
            "accept": self.accept,
            "profit": self.profit,
            "loss": self.loss,
            "platform_liquidity": self.platform_liquidity,
            "status": self.status.name,
            "referral_id": self.referral_id,
            "referral_commission": self.referral_commission,
            "created_at": self.created_at,
            "created_at_broker_time": self.created_at_broker_time,
            "influencer_order": self.influencer_order,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EbinexOrder":
        return cls(
            id=data.get("id"),
            user_email=data.get("userEmail"),
            account_id=data.get("accountId"),
            environment=Environment[data.get("environment")],
            candle_time_frame=data.get("candleTimeFrame"),
            candle_start_time=data.get("candleStartTime"),
            symbol=data.get("symbol"),
            direction=data.get("direction"),
            price=data.get("price"),
            cop=data.get("cop"),
            ccp=data.get("ccp"),
            asset=data.get("asset"),
            invest=data.get("invest"),
            fee_rate=data.get("feeRate"),
            used_bonus=data.get("usedBonus"),
            fees=data.get("fees"),
            refund=data.get("refund"),
            accept=data.get("accept"),
            profit=data.get("profit"),
            loss=data.get("loss"),
            platform_liquidity=data.get("platformLiquidity"),
            status=Statuses[data.get("status")],
            referral_id=data.get("referralId"),
            referral_commission=data.get("referralCommission"),
            created_at=data.get("createdAt"),
            created_at_broker_time=data.get("createdAtBrokerTime"),
            influencer_order=data.get("influencerOrder"),
        )

    def update(self, other: "EbinexOrder"):
        self.__dict__.update(other.__dict__)


class EbinexTrade:
    def __init__(
        self,
        account_id: str,
        timeframe: Timeframe,
        symbol: str,
        direction: Direction,
        amount: int,
        asset: str,
        price: float,
    ):
        self.account_id = account_id
        self.timeframe = timeframe
        self.symbol = symbol
        self.direction = direction
        self.amount = amount
        self.asset = asset
        self.price = price

    def to_dict(self) -> Dict:
        return {
            "accountId": self.account_id,
            "candleTimeFrame": self.timeframe.name,
            "symbol": self.symbol,
            "direction": self.direction.name,
            "invest": self.amount,
            "asset": self.asset,
            "price": self.price,
        }


class EbinexConfig:
    def __init__(
        self, symbol: str, timeframe: Timeframe, environment: Environment
    ):
        self.symbol = symbol
        self.timeframe = timeframe
        self.environment = environment

    def to_dict(self) -> Dict[str, str]:
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe.name,            
            "environment": self.environment.name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EbinexConfig":
        return cls(
            symbol=data.get("symbol"),
            timeframe=Timeframe[data.get("timeframe")],
            environment=Environment[data.get("environment")],
        )


class EbinexSymbol:
    def __init__(
        self,
        symbol: str,
        symbolType: str,
        symbolLabel: str,
        marketStatus: str,
        openMarketTime: Optional[str],
        closeMarketTime: Optional[str],
        payout: float,
        hrs24PercentualChange: float,
    ):
        self.symbol = symbol
        self.symbolType = symbolType
        self.symbolLabel = symbolLabel
        self.marketStatus = marketStatus
        self.openMarketTime = openMarketTime
        self.closeMarketTime = closeMarketTime
        self.payout = payout
        self.hrs24PercentualChange = hrs24PercentualChange

    @classmethod
    def from_dict(cls, data: dict) -> "EbinexSymbol":
        return cls(
            symbol=data["symbol"],
            symbolType=data["symbolType"],
            symbolLabel=data["symbolLabel"],
            marketStatus=data["marketStatus"],
            openMarketTime=data.get("openMarketTime"),
            closeMarketTime=data.get("closeMarketTime"),
            payout=data["payout"],
            hrs24PercentualChange=data["hrs24PercentualChange"],
        )


class EbinexAccount:
    def __init__(
        self,
        id: str,
        environment: Environment,
        user_role: str,
        default_coin_balance: float,
        label: str,
    ):
        self.id = id
        self.environment = environment
        self.user_role = user_role
        self.default_coin_balance = default_coin_balance
        self.label = label

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "environment": self.environment,
            "userRole": self.user_role,
            "defaultCoinBalance": self.default_coin_balance,
            "label": self.label,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EbinexAccount":
        return cls(
            id=data.get("id"),
            environment=Environment[data.get("environment")],
            user_role=data.get("userRole"),
            default_coin_balance=data.get("defaultCoinBalance", 0.0),
            label=data.get("label"),
        )


class EbinexPriceData:
    def __init__(
        self,
        timestamp: int,
        open: float,
        high: float,
        low: float,
        close: float,
        n: Optional[int] = None,
        v: Optional[float] = None,
        vw: Optional[float] = None,
    ):
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.n = n
        self.v = v
        self.vw = vw

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EbinexPriceData":
        return cls(
            timestamp=data["t"],
            open=data["o"],
            high=data["h"],
            low=data["l"],
            close=data["c"],
            n=data.get("n"),
            v=data.get("v"),
            vw=data.get("vw"),
        )


class EbinexParameters:
    def __init__(
        self,
        fee_rate: str,
        withdrawal_percentual_fee_rate: str,
        candle_time_frames: List[Dict[str, str]],
        default_coin: str,
        public_api_url: str,
        user_registration_on_hold: bool,
        liquidity_user_active: bool,
        default_referral_percentual_commission: float,
        liquidity_user_max_liquidity: float,
        kyc_enabled: bool,
        randomized_book: Dict[str, Any],
        liquidity_user_max_liquidity_per_user: float,
        scoped_randomized_book: List[Dict[str, Any]],
        automatic_withdrawal_config: Dict[str, Any],
        dynamic_rlp_parameters: Dict[str, Any],
        default_gateway_deposit: str,
        default_gateway_withdrawal: str,
        symbols_config: Dict[str, Any],
        user_language: str,
        user_timezone: str,
        default_operation_qty: float,
        default_candle_timeframe: Timeframe,
        default_symbol: str,
        withdrawal_min_amount: float,
    ):

        self.fee_rate = fee_rate
        self.withdrawal_percentual_fee_rate = withdrawal_percentual_fee_rate
        self.candle_time_frames = candle_time_frames
        self.default_coin = default_coin
        self.public_api_url = public_api_url
        self.user_registration_on_hold = user_registration_on_hold
        self.liquidity_user_active = liquidity_user_active
        self.default_referral_percentual_commission = default_referral_percentual_commission
        self.liquidity_user_max_liquidity = liquidity_user_max_liquidity
        self.kyc_enabled = kyc_enabled
        self.randomized_book = randomized_book
        self.liquidity_user_max_liquidity_per_user = liquidity_user_max_liquidity_per_user
        self.scoped_randomized_book = scoped_randomized_book
        self.automatic_withdrawal_config = automatic_withdrawal_config
        self.dynamic_rlp_parameters = dynamic_rlp_parameters
        self.default_gateway_deposit = default_gateway_deposit
        self.default_gateway_withdrawal = default_gateway_withdrawal
        self.symbols_config = symbols_config
        self.user_language = user_language
        self.user_timezone = user_timezone
        self.default_operation_qty = default_operation_qty
        self.default_candle_timeframe = default_candle_timeframe
        self.default_symbol = default_symbol
        self.withdrawal_min_amount = withdrawal_min_amount

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fee_rate": self.fee_rate,
            "withdrawal_percentual_fee_rate": self.withdrawal_percentual_fee_rate,
            "candle_time_frames": self.candle_time_frames,
            "default_coin": self.default_coin,
            "public_api_url": self.public_api_url,
            "user_registration_on_hold": self.user_registration_on_hold,
            "liquidity_user_active": self.liquidity_user_active,
            "default_referral_percentual_commission": self.default_referral_percentual_commission,
            "liquidity_user_max_liquidity": self.liquidity_user_max_liquidity,
            "kyc_enabled": self.kyc_enabled,
            "randomized_book": self.randomized_book,
            "liquidity_user_max_liquidity_per_user": self.liquidity_user_max_liquidity_per_user,
            "scoped_randomized_book": self.scoped_randomized_book,
            "automatic_withdrawal_config": self.automatic_withdrawal_config,
            "dynamic_rlp_parameters": self.dynamic_rlp_parameters,
            "default_gateway_deposit": self.default_gateway_deposit,
            "default_gateway_withdrawal": self.default_gateway_withdrawal,
            "symbols_config": self.symbols_config,
            "user_language": self.user_language,
            "user_timezone": self.user_timezone,
            "default_operation_qty": self.default_operation_qty,
            "default_candle_timeframe": self.default_candle_timeframe,
            "default_symbol": self.default_symbol,
            "withdrawal_min_amount": self.withdrawal_min_amount,
        }

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> "EbinexParameters":
        import json

        data_dict = {item["key"]: item["value"] for item in data}

        return cls(
            fee_rate=data_dict.get("FEE_RATE"),
            withdrawal_percentual_fee_rate=data_dict.get("WITHDRAWAL_PERCENTUAL_FEE_RATE"),
            candle_time_frames=json.loads(data_dict.get("CANDLE_TIME_FRAMES", "[]")),
            default_coin=data_dict.get("DEFAULT_COIN"),
            public_api_url=data_dict.get("PUBLIC_API_URL"),
            user_registration_on_hold=data_dict.get("USER_REGISTRATION_ON_HOLD") == "true",
            liquidity_user_active=data_dict.get("LIQUIDITY_USER_ACTIVE") == "true",
            default_referral_percentual_commission=float(data_dict.get("DEFAULT_REFERRAL_PERCENTUAL_COMISSION", 0.0)),
            liquidity_user_max_liquidity=float(data_dict.get("LIQUIDITY_USER_MAX_LIQUIDITY", 0.0)),
            kyc_enabled=data_dict.get("KYC_ENABLED") == "true",
            randomized_book=json.loads(data_dict.get("RANDOMIZED_BOOK", "{}")),
            liquidity_user_max_liquidity_per_user=float(data_dict.get("LIQUIDITY_USER_MAX_LIQUIDITY_PER_USER", 0.0)),
            scoped_randomized_book=json.loads(data_dict.get("SCOPED_RANDOMIZED_BOOK", "[]")),
            automatic_withdrawal_config=json.loads(data_dict.get("AUTOMATIC_WITHDRAWAL_CONFIG", "{}")),
            dynamic_rlp_parameters=json.loads(data_dict.get("DYNAMIC_RLP_PARAMETERS", "{}")),
            default_gateway_deposit=data_dict.get("DEFAULT_GATEWAY_DEPOSIT"),
            default_gateway_withdrawal=data_dict.get("DEFAULT_GATEWAY_WITHDRAWAL"),
            symbols_config=json.loads(data_dict.get("SYMBOLS_CONFIG", "{}")),
            user_language=data_dict.get("USER_LANGUAGE"),
            user_timezone=data_dict.get("USER_TIMEZONE"),
            default_operation_qty=float(data_dict.get("DEFAULT_OPERATION_QTY", 0.0)),
            default_candle_timeframe=Timeframe[data_dict.get("DEFAULT_CANDLE_TIMEFRAME")],
            default_symbol=data_dict.get("DEFAULT_SYMBOL"),
            withdrawal_min_amount=float(data_dict.get("WITHDRAWAL_MIN_AMOUNT", 0.0)),
        )


class EbinexWebSocketInfo:
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    @property
    def entropy(self) -> int:
        return self.data.get("entropy")

    @property
    def origins(self) -> List[str]:
        return self.data.get("origins")

    @property
    def cookie_needed(self) -> bool:
        return self.data.get("cookie_needed")

    @property
    def websocket(self) -> bool:
        return self.data.get("websocket")


class EbinexWebSocketTrade:
    def __init__(self, timestamp: int, volume: float, price: float):
        self.timestamp = timestamp
        self.volume = volume
        self.price = price

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EbinexWebSocketTrade":
        return cls(
            timestamp=data.get("t"),
            volume=data.get("v"),
            price=data.get("p"),
        )


class EbinexWebSocketBalance:
    def __init__(self, amount: float, asset: str):
        self.amount = amount
        self.asset = asset

    @classmethod
    def from_dict(cls, data: Dict[str, float]):
        return cls(
            amount=next(iter(data.values()), 0.0), asset=next(iter(data.keys()), "")
        )

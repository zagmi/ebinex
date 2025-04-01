"""if you know, you know, types basically"""

import os
import sys
import json
from enum import Enum, auto
from selenium.webdriver import Chrome
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from selenium.common.exceptions import NoSuchElementException as NSEE
from typing import Any, Dict, List, Callable, Optional, TypedDict, TYPE_CHECKING

WebDriver = Chrome
NoSuchElementException = NSEE

PACKAGE_DIR = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
DEFAULT_FUNC: Callable[..., None] = lambda *args, **kwargs: None

DEFAULT_VAULT = os.path.join(PACKAGE_DIR, "vault.json")
DEFAULT_EXPIRATION = (datetime.now() + timedelta(days=30)).timestamp()

if TYPE_CHECKING:
    from ebinexpy.source import Ebinex
else:
    pass


class Direction(Enum):
    BULL = auto()
    BEAR = auto()

    def __eq__(self, other: Optional["Direction"]):
        if hasattr(other, "name"):
            return self.name == other.name
        return NotImplemented

    def __ne__(self, other: Optional["Direction"]):
        if hasattr(other, "name"):
            return self.name != other.name
        return NotImplemented
    
    def __hash__(self):
        return hash(self.name)
    
class OrderType(Enum):
    OPTION = auto()
    RETRACTION_ENDTIME = auto()

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

    def __hash__(self):
        return hash(self.name)

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
    
    def __hash__(self):
        return hash(self.name)

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

    def __hash__(self):
        return hash(self.name)

@dataclass
class Credentials:
    sign: str
    account_id: str
    access_token: str
    config: "EbinexConfig"
    expiration: int = field(default=DEFAULT_EXPIRATION)

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
            expiration=data.get("expiration", DEFAULT_EXPIRATION),
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
        bull_investments = [EbinexBook.Investment.from_dict(b) for b in (data.get("bull") or [])]
        bear_investments = [EbinexBook.Investment.from_dict(b) for b in (data.get("bear") or [])]

        return cls(
            timeframe=Timeframe[data["candleTimeFrame"]],
            symbol=data["symbol"],
            bull=bull_investments,
            bear=bear_investments,
        )


@dataclass
class EbinexOrder:
    id: str
    user_email: str
    account_id: str
    environment: 'Environment'
    candle_time_frame: str
    candle_start_time: int
    symbol: str
    direction: 'Direction'
    price: float
    cop: float
    ccp: float
    asset: str
    invest: float
    fee_rate: float
    used_bonus: float
    fees: float
    refund: float
    accept: float
    profit: float
    loss: float
    platform_liquidity: float
    status: 'Statuses'
    referral_id: Optional[str] = None
    referral_commission: Optional[float] = None
    created_at: int = field(default_factory=int)
    created_at_broker_time: int = field(default_factory=int)
    influencer_order: bool = False

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
            direction=Direction[data.get("direction")],
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


@dataclass
class EbinexTrade:
    binary_order_type: OrderType
    candle_end_time: int
    account_id: str
    timeframe: Timeframe
    symbol: str
    direction: Direction
    amount: int
    asset: str
    price: float

    def to_dict(self) -> Dict:
        return {
            "binaryOrderType": self.binary_order_type.name,
            "accountId": self.account_id,
            "candleTimeFrame": self.timeframe.name,
            "candleEndTime": self.candle_end_time,
            "symbol": self.symbol,
            "direction": self.direction.name,
            "invest": self.amount,
            "asset": self.asset,
            "price": self.price,
        }


@dataclass
class EbinexConfig:
    symbol: str
    timeframe: "Timeframe"
    environment: "Environment"

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

class ConfigMode(TypedDict):
    orderType: str
    status: str
    payout: float

@dataclass
class EbinexSymbol:
    symbol: str
    symbolType: str
    symbolLabel: str
    marketStatus: str
    openMarketTime: Optional[str]
    closeMarketTime: Optional[str]
    payout: float
    hrs24PercentualChange: float
    configModes: Dict[OrderType, ConfigMode]  

    @classmethod
    def from_dict(cls, data: dict) -> "EbinexSymbol":
        config_modes = {
            OrderType(mode_key): mode_value 
            for mode_key, mode_value in data.get("configModes", {}).items()
        }
        
        return cls(
            symbol=data["symbol"],
            symbolType=data["symbolType"],
            symbolLabel=data["symbolLabel"],
            marketStatus=data["marketStatus"],
            openMarketTime=data.get("openMarketTime"),
            closeMarketTime=data.get("closeMarketTime"),
            payout=data["payout"],
            hrs24PercentualChange=data["hrs24PercentualChange"],
            configModes=config_modes
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


@dataclass
class EbinexPriceData:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    n: Optional[int] = None
    v: Optional[float] = None
    vw: Optional[float] = None

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


@dataclass
class EbinexParameters:
    fee_rate: str
    withdrawal_percentual_fee_rate: str
    candle_time_frames: List[Dict[str, str]]
    default_coin: str
    public_api_url: str
    user_registration_on_hold: bool
    liquidity_user_active: bool
    default_referral_percentual_commission: float
    liquidity_user_max_liquidity: float
    kyc_enabled: bool
    randomized_book: Dict[str, Any]
    liquidity_user_max_liquidity_per_user: float
    scoped_randomized_book: List[Dict[str, Any]]
    automatic_withdrawal_config: Dict[str, Any]
    dynamic_rlp_parameters: Dict[str, Any]
    default_gateway_deposit: str
    default_gateway_withdrawal: str
    symbols_config: Dict[str, "SymbolConfig"]
    user_language: str
    user_timezone: str
    default_operation_qty: float
    default_candle_timeframe: Timeframe
    default_symbol: str
    withdrawal_min_amount: float

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> "EbinexParameters":
        data_dict = {item["key"]: item["value"] for item in data}

        for key, value in data_dict.items():
            if isinstance(value, str):
                try:
                    data_dict[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    pass  

        return cls(
            fee_rate=data_dict.get("FEE_RATE"),
            withdrawal_percentual_fee_rate=data_dict.get("WITHDRAWAL_PERCENTUAL_FEE_RATE"),
            candle_time_frames=data_dict.get("CANDLE_TIME_FRAMES", []),
            default_coin=data_dict.get("DEFAULT_COIN"),
            public_api_url=data_dict.get("PUBLIC_API_URL"),
            user_registration_on_hold=data_dict.get("USER_REGISTRATION_ON_HOLD"),
            liquidity_user_active=data_dict.get("LIQUIDITY_USER_ACTIVE"),
            default_referral_percentual_commission=float(data_dict.get("DEFAULT_REFERRAL_PERCENTUAL_COMISSION", 0.0)),
            liquidity_user_max_liquidity=float(data_dict.get("LIQUIDITY_USER_MAX_LIQUIDITY", 0.0)),
            kyc_enabled=data_dict.get("KYC_ENABLED"),
            randomized_book=data_dict.get("RANDOMIZED_BOOK", {}),
            liquidity_user_max_liquidity_per_user=float(data_dict.get("LIQUIDITY_USER_MAX_LIQUIDITY_PER_USER", 0.0)),
            scoped_randomized_book=data_dict.get("SCOPED_RANDOMIZED_BOOK", []),
            automatic_withdrawal_config=data_dict.get("AUTOMATIC_WITHDRAWAL_CONFIG", {}),
            dynamic_rlp_parameters=data_dict.get("DYNAMIC_RLP_PARAMETERS", {}),
            default_gateway_deposit=data_dict.get("DEFAULT_GATEWAY_DEPOSIT"),
            default_gateway_withdrawal=data_dict.get("DEFAULT_GATEWAY_WITHDRAWAL"),
            symbols_config={key: SymbolConfig.from_dict(value) for key, value in data_dict.get("SYMBOLS_CONFIG", {}).items()},
            user_language=data_dict.get("USER_LANGUAGE"),
            user_timezone=data_dict.get("USER_TIMEZONE"),
            default_operation_qty=float(data_dict.get("DEFAULT_OPERATION_QTY", 0.0)),
            default_candle_timeframe=Timeframe[data_dict.get("DEFAULT_CANDLE_TIMEFRAME")],
            default_symbol=data_dict.get("DEFAULT_SYMBOL"),
            withdrawal_min_amount=float(data_dict.get("WITHDRAWAL_MIN_AMOUNT", 0.0)),
        )

    def to_list(self) -> List[Dict[str, Any]]:
        return [
            {"key": "FEE_RATE", "value": self.fee_rate},
            {"key": "WITHDRAWAL_PERCENTUAL_FEE_RATE", "value": self.withdrawal_percentual_fee_rate},
            {"key": "CANDLE_TIME_FRAMES", "value": json.dumps(self.candle_time_frames)},
            {"key": "DEFAULT_COIN", "value": self.default_coin},
            {"key": "PUBLIC_API_URL", "value": self.public_api_url},
            {"key": "USER_REGISTRATION_ON_HOLD", "value": self.user_registration_on_hold},
            {"key": "LIQUIDITY_USER_ACTIVE", "value": self.liquidity_user_active},
            {"key": "DEFAULT_REFERRAL_PERCENTUAL_COMMISSION", "value": self.default_referral_percentual_commission},
            {"key": "LIQUIDITY_USER_MAX_LIQUIDITY", "value": self.liquidity_user_max_liquidity},
            {"key": "KYC_ENABLED", "value": self.kyc_enabled},
            {"key": "RANDOMIZED_BOOK", "value": json.dumps(self.randomized_book)}, 
            {"key": "LIQUIDITY_USER_MAX_LIQUIDITY_PER_USER", "value": self.liquidity_user_max_liquidity_per_user},
            {"key": "SCOPED_RANDOMIZED_BOOK", "value": json.dumps(self.scoped_randomized_book)},  
            {"key": "AUTOMATIC_WITHDRAWAL_CONFIG", "value": json.dumps(self.automatic_withdrawal_config)}, 
            {"key": "DYNAMIC_RLP_PARAMETERS", "value": json.dumps(self.dynamic_rlp_parameters)}, 
            {"key": "DEFAULT_GATEWAY_DEPOSIT", "value": self.default_gateway_deposit},
            {"key": "DEFAULT_GATEWAY_WITHDRAWAL", "value": self.default_gateway_withdrawal},
            {"key": "SYMBOLS_CONFIG", "value": {key: value.to_dict() for key, value in self.symbols_config.items()}}, 
            {"key": "USER_LANGUAGE", "value": self.user_language},
            {"key": "USER_TIMEZONE", "value": self.user_timezone},
            {"key": "DEFAULT_OPERATION_QTY", "value": self.default_operation_qty},
            {"key": "DEFAULT_CANDLE_TIMEFRAME", "value": self.default_candle_timeframe.name if self.default_candle_timeframe else None},
            {"key": "DEFAULT_SYMBOL", "value": self.default_symbol},
            {"key": "WITHDRAWAL_MIN_AMOUNT", "value": self.withdrawal_min_amount},
        ]


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


@dataclass
class EbinexWebSocketTrade:
    timestamp: int
    volume: float
    price: float

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

@dataclass
class ConfigMode:
    orderType: str
    status: str
    payout: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConfigMode':
        return cls(
            orderType=data['orderType'],
            status=data['status'],
            payout=data['payout']
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'orderType': self.orderType,
            'status': self.status,
            'payout': self.payout
        }
    
@dataclass
class SymbolConfig:
    symbol: str
    configModes: Dict[str, ConfigMode]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SymbolConfig':
        return cls(
            symbol=data['symbol'],
            configModes={key: ConfigMode.from_dict(value) for key, value in data['configModes'].items()}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'configModes': {key: value.to_dict() for key, value in self.configModes.items()}
        }
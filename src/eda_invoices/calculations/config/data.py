import datetime
from dataclasses import field
from typing import List
from typing import Optional
from typing import Union

from pydantic.dataclasses import dataclass


@dataclass
class Address:
    line: str
    post_code: str
    city: str

    @property
    def post_city(self):
        return f"{self.post_code} {self.city}"

    @property
    def short(self):
        return f"{self.line}, {self.post_city}"


@dataclass
class MeteringPoint:
    point_id: str
    name: Optional[str] = None
    active_tariff: Optional[str] = None


@dataclass
class Customer:
    email: str
    name: str
    customer_id: str
    address: Address
    default_tariff: Optional[str] = None
    metering_points: Optional[List[MeteringPoint]] = field(default_factory=lambda: [])


@dataclass
class TariffPricepoint:
    price: float
    date: Union[datetime.datetime, datetime.date]


@dataclass
class Tariff:
    name: str
    prices: List[TariffPricepoint] = field(default_factory=lambda: [])


@dataclass
class Sender:
    name: str
    vat_id: str
    address: Address
    email: str
    phone: str
    web: Optional[str]


@dataclass
class Config:
    sender: Sender
    customers: List[Customer]
    tariffs: List[Tariff] = field(default_factory=lambda: [])
    bcc: List[str] = field(default_factory=lambda: [])

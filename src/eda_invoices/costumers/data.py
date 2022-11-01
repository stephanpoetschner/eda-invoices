from dataclasses import field
from pydantic.dataclasses import dataclass
from typing import Optional, List


@dataclass
class Address:
    line: str
    post_code: str
    city: str


@dataclass
class Customer:
    email: str
    name: str
    customer_id: str
    address: Address
    metering_points: Optional[List[str]] = field(default_factory=lambda: [])


@dataclass
class Sender:
    name: str
    vat_id: str
    address: Address
    email: str
    phone: str
    web: Optional[str]

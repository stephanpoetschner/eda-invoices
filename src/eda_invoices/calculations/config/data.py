from dataclasses import field
from typing import List
from typing import Optional

from pydantic.dataclasses import dataclass

from eda_invoices.calculations.config.enums import EnergyDirection


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
    name: str
    direction: Optional[EnergyDirection] = None
    # data: Optional[pd.DataFrame] = None


@dataclass
class Customer:
    email: str
    name: str
    customer_id: str
    address: Address
    metering_points: Optional[List[MeteringPoint]] = field(default_factory=lambda: [])


@dataclass
class Sender:
    name: str
    vat_id: str
    address: Address
    email: str
    phone: str
    web: Optional[str]

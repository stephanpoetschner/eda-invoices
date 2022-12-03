import dataclasses
import json

import pandas
from django.core.serializers.json import DjangoJSONEncoder

from eda_invoices.calculations.config import data


class MyJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, (data.Customer, data.Sender, data.MeteringPoint)):
            return dataclasses.asdict(obj)
        elif isinstance(obj, pandas.DataFrame):
            return json.loads(obj.to_json(date_format="iso", orient="split"))
        return super().default(obj)

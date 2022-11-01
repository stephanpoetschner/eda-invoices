# ! python3

import yaml
import dataclasses

yaml_data = """
name: VERBUND AG.
vat_id: ATU14703908
address:
line: Postfach 8400
post_code: 1011
city: Wien
email: service@verbund.at
web: https://www.verbund.at/
phone: Mo-Fr 7-18 Uhr  0800 210 210
"""

def read_yaml_into_dataclass(yaml_data):
    data = yaml.safe_load(yaml_data)

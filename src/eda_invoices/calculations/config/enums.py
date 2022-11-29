from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class EnergyDirection(TextChoices):
    CONSUMPTION = "CONSUMPTION", _("Verbrauch")
    PRODUCTION = "PRODUCTION", _("Erzeugung")
    UNKNOWN = "UNKNOWN", _("Nicht bekannt")

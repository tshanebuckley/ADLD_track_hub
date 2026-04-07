from pydantic import Field
from adld_track_hub.utils.models import RowData
from typing import final

@final
class Schema(RowData):
    origin: str | None = Field(alias = "Origin")
    number: str | None = Field(alias = "Number of Individuals Affected ")
    age: str | None = Field(alias = "Age of Onset (years)")
    symptoms: str | None = Field(alias = "Reported Symptoms")

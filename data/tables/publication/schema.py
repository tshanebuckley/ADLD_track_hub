from pydantic import Field
from adld_track_hub.utils.models import RowData
from typing import final

@final
class Schema(RowData):
    pubmed: str | None = Field(alias = "Pubmed link")
    authors: str | None = Field(alias = "Authors")
    aka: str | None = Field(alias = "AKA")
    pedigree: str | None = Field(alias = "Pedigree")

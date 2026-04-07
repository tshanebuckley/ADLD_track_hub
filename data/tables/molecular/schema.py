from pydantic import Field
from adld_track_hub.utils.models import RowData
from typing import final

@final
class Schema(RowData):
    start: int = Field(alias = "Start position")
    end: int = Field(alias = "End position")
    size: str | None = Field(alias = "Size (bp)")
    orientation: str | None = Field(alias = "Orientation")
    microhomology: str | None = Field(alias = "Microhomology")

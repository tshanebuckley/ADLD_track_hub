from pydantic import Field
from adld_track_hub.utils.models import RowData
from typing import final

from adld_track_hub.utils.models import RowData


@final
class Schema(RowData):
    summary: str | None = Field(alias = "Summary")

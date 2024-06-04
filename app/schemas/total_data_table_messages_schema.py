from typing import ClassVar

import pydantic  # type: ignore


class TotalDataTableMessageSchema(pydantic.BaseModel):
    INBOX_COST: ClassVar[str] = "inbox_cost"
    LATENCY_AVERAGE: ClassVar[str] = "latency_average"

    inbox_cost: int
    latency_average: float
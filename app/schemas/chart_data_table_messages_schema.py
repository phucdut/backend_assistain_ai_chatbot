from typing import ClassVar

import pydantic  # type: ignore


class ChartDataTableMessageSchema(pydantic.BaseModel):
    TIME_POINT: ClassVar[str] = "time_point"
    INBOX_COST: ClassVar[str] = "inbox_cost"
    LATENCY_AVERAGE: ClassVar[str] = "latency_average"

    time_point: int
    inbox_cost: int
    latency_average: float
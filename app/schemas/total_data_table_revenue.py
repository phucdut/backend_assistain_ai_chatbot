from typing import ClassVar

import pydantic  # type: ignore


class TotalDataTableRevenueSchema(pydantic.BaseModel):
    REVENUE_COST: ClassVar[str] = "revenue"
    # LATENCY_AVERAGE: ClassVar[str] = "latency_average"

    revenue: int
    # latency_average: float
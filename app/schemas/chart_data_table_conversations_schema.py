from typing import ClassVar

import pydantic  # type: ignore


class ChartDataTableConversationSchema(pydantic.BaseModel):
    TIME_POINT: ClassVar[str] = "time_point"
    VISITOR_COST: ClassVar[str] = "visitor_cost"
    RATING_AVERAGE: ClassVar[str] = "rating_average"

    time_point: int
    visitor_cost: int
    rating_average: float

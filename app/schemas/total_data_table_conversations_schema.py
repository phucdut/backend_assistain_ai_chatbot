from typing import ClassVar

import pydantic  # type: ignore


class TotalDataTableConversationSchema(pydantic.BaseModel):
    VISITOR_COST: ClassVar[str] = "visitor_cost"
    RATING_AVERAGE: ClassVar[str] = "rating_average"

    visitor_cost: int
    rating_average: float

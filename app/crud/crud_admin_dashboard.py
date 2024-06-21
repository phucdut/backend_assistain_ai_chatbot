from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.common.logger import setup_logger
from app.schemas.chart_data_table_conversations_schema import (
    ChartDataTableConversationSchema,
)
from app.schemas.total_data_table_conversations_schema import (
    TotalDataTableConversationSchema,
)
from app.schemas.chart_data_table_messages_schema import (
    ChartDataTableMessageSchema,
)
from app.schemas.total_data_table_messages_schema import (
    TotalDataTableMessageSchema,
)
from app.schemas.total_data_table_revenue import (
    TotalDataTableRevenueSchema,
)


logger = setup_logger()

# Statistic inboxes, latency average by hour of a specific day
GET_TABLE_MESSAGE_BY_HOUR_OF_SPECIFIC_DAY = f"""
WITH HourReference AS (
    SELECT 0 AS hour_of_day
    UNION SELECT 1 UNION SELECT 2 UNION SELECT 3
    UNION SELECT 4 UNION SELECT 5 UNION SELECT 6
    UNION SELECT 7 UNION SELECT 8 UNION SELECT 9
    UNION SELECT 10 UNION SELECT 11 UNION SELECT 12
    UNION SELECT 13 UNION SELECT 14 UNION SELECT 15
    UNION SELECT 16 UNION SELECT 17 UNION SELECT 18
    UNION SELECT 19 UNION SELECT 20 UNION SELECT 21
    UNION SELECT 22 UNION SELECT 23
)
SELECT
    hr.hour_of_day AS {ChartDataTableMessageSchema.TIME_POINT},
    COALESCE(conv.message_count, 0) AS  {ChartDataTableMessageSchema.INBOX_COST},
    COALESCE(rate.latency_average, 0) AS {ChartDataTableMessageSchema.LATENCY_AVERAGE}
FROM
    HourReference hr
LEFT JOIN (
    SELECT
        EXTRACT(HOUR FROM created_at) AS hour_of_day,
        COUNT(*) AS message_count
    FROM
        messages
    WHERE
        conversation_id = :conversation_id
        AND TO_CHAR(created_at, 'YYYY-MM-DD') = :date
    GROUP BY
        EXTRACT(HOUR FROM created_at)
) conv ON hr.hour_of_day = conv.hour_of_day
LEFT JOIN (
    SELECT
        EXTRACT(HOUR FROM created_at) AS hour_of_day,
        AVG(latency) AS latency_average
    FROM
        messages
    WHERE
        conversation_id = :conversation_id
        AND TO_CHAR(created_at, 'YYYY-MM-DD') = :date
    GROUP BY
        EXTRACT(HOUR FROM created_at)
) rate ON hr.hour_of_day = rate.hour_of_day
ORDER BY
    hr.hour_of_day;
"""


# Statistic inboxes, latency average by day of a specific month
GET_TABLE_MESSAGE_BY_DAY_OF_SPECIFIC_MONTH = f"""
WITH RECURSIVE DayReference AS ( 
    SELECT 1 AS day_of_month 
    UNION ALL 
    SELECT day_of_month + 1 
    FROM DayReference 
    WHERE day_of_month < EXTRACT(DAY FROM DATE_TRUNC('month', TO_DATE('2024-05', 'YYYY-MM')) + INTERVAL '1 month' - INTERVAL '1 day') 
) 
SELECT
    dr.day_of_month AS {ChartDataTableMessageSchema.TIME_POINT},
    COALESCE(SUM(conv.message_count), 0) AS  {ChartDataTableMessageSchema.INBOX_COST},
    COALESCE(AVG(rate.latency_average), 0) AS {ChartDataTableMessageSchema.LATENCY_AVERAGE}
FROM
    DayReference dr
LEFT JOIN (
    SELECT
        EXTRACT(MONTH FROM created_at) AS day_of_month,
        COUNT(*) AS message_count
    FROM
        messages
    WHERE
        conversation_id = :conversation_id
        AND TO_CHAR(created_at, 'YYYY-MM') = :month  
    GROUP BY
        EXTRACT(MONTH FROM created_at)
) conv ON dr.day_of_month = conv.day_of_month
LEFT JOIN (
    SELECT
        EXTRACT(MONTH FROM created_at) AS day_of_month,
        AVG(latency) AS latency_average
    FROM
        messages
    WHERE
        conversation_id = :conversation_id
        AND TO_CHAR(created_at, 'YYYY-MM') = :month  
    GROUP BY
        EXTRACT(MONTH FROM created_at)
) rate ON dr.day_of_month = rate.day_of_month
GROUP BY
    dr.day_of_month
ORDER BY
    dr.day_of_month;
"""

# Statistic inboxes, latency average by day of a specific month
GET_TABLE_MESSAGE_BY_MONTH_OF_SPECIFIC_YEAR = f"""
WITH MonthReference AS ( 
        SELECT 1 AS month_of_year 
        UNION ALL 
        SELECT 2 UNION SELECT 3 UNION SELECT 4 
        UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 
        UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 
        UNION SELECT 11 UNION SELECT 12 
)
SELECT
    mr.month_of_year AS {ChartDataTableMessageSchema.TIME_POINT},
    COALESCE(SUM(conv.message_count), 0) AS  {ChartDataTableMessageSchema.INBOX_COST},
    COALESCE(AVG(rate.latency_average), 0) AS {ChartDataTableMessageSchema.LATENCY_AVERAGE}
FROM
    MonthReference mr
LEFT JOIN (
    SELECT
        EXTRACT(MONTH FROM created_at) AS month_of_year,
        COUNT(*) AS message_count
    FROM
        messages
    WHERE
        conversation_id = :conversation_id
        AND TO_CHAR(created_at, 'YYYY') = :year  
    GROUP BY
        EXTRACT(MONTH FROM created_at)
) conv ON mr.month_of_year = conv.month_of_year
LEFT JOIN (
    SELECT
        EXTRACT(MONTH FROM created_at) AS month_of_year,
        AVG(latency) AS latency_average
    FROM
        messages
    WHERE
        conversation_id = :conversation_id
        AND TO_CHAR(created_at, 'YYYY') = :year 
    GROUP BY
        EXTRACT(MONTH FROM created_at)
) rate ON mr.month_of_year = rate.month_of_year
GROUP BY
    mr.month_of_year
ORDER BY
    mr.month_of_year;
"""


# Statistic visitor, rating average by hour of a specific day
GET_TABLE_CONVERSATION_BY_HOUR_OF_SPECIFIC_DAY = f"""
WITH HourReference AS (
    SELECT 0 AS hour_of_day
    UNION SELECT 1 UNION SELECT 2 UNION SELECT 3
    UNION SELECT 4 UNION SELECT 5 UNION SELECT 6
    UNION SELECT 7 UNION SELECT 8 UNION SELECT 9
    UNION SELECT 10 UNION SELECT 11 UNION SELECT 12
    UNION SELECT 13 UNION SELECT 14 UNION SELECT 15
    UNION SELECT 16 UNION SELECT 17 UNION SELECT 18
    UNION SELECT 19 UNION SELECT 20 UNION SELECT 21
    UNION SELECT 22 UNION SELECT 23
)
SELECT
    hr.hour_of_day AS {ChartDataTableConversationSchema.TIME_POINT},
    COALESCE(SUM(conv.visitor_count), 0) AS  {ChartDataTableConversationSchema.VISITOR_COST},
    COALESCE(AVG(rate.rating_average), 0) AS {ChartDataTableConversationSchema.RATING_AVERAGE}
FROM
    HourReference hr
LEFT JOIN (
    SELECT
        EXTRACT(HOUR FROM created_at) AS hour_of_day,
        COUNT(*) AS visitor_count
    FROM
        conversations
    WHERE
        chatbot_id = :chatbot_id
        AND TO_CHAR(created_at, 'YYYY-MM-DD') = :date
    GROUP BY
        EXTRACT(HOUR FROM created_at), chatbot_id
) conv ON hr.hour_of_day = conv.hour_of_day
LEFT JOIN (
    SELECT
        EXTRACT(HOUR FROM created_at) AS hour_of_day,
        AVG(rating_score) AS rating_average
    FROM
        conversations
    WHERE
        chatbot_id = :chatbot_id
        AND TO_CHAR(created_at, 'YYYY-MM-DD') = :date
    GROUP BY
        EXTRACT(HOUR FROM created_at), chatbot_id
) rate ON hr.hour_of_day = rate.hour_of_day
GROUP BY
    hr.hour_of_day
ORDER BY
    hr.hour_of_day;
"""

# Statistic visitor, rating average by day of a specific month
GET_TABLE_CONVERSATION_BY_DAY_OF_SPECIFIC_MONTH = f"""
WITH RECURSIVE DayReference AS ( 
    SELECT 1 AS day_of_month 
    UNION ALL 
    SELECT day_of_month + 1 
    FROM DayReference 
    WHERE day_of_month < EXTRACT(DAY FROM DATE_TRUNC('month', TO_DATE('2024-05', 'YYYY-MM')) + INTERVAL '1 month' - INTERVAL '1 day') 
) 
SELECT
    dr.day_of_month AS {ChartDataTableMessageSchema.TIME_POINT},
    COALESCE(SUM(conv.visitor_count), 0) AS  {ChartDataTableConversationSchema.VISITOR_COST},
    COALESCE(AVG(rate.rating_average), 0) AS {ChartDataTableConversationSchema.RATING_AVERAGE}
FROM
    DayReference dr
LEFT JOIN (
    SELECT
        EXTRACT(MONTH FROM created_at) AS day_of_month,
        COUNT(*) AS visitor_count
    FROM
        conversations
    WHERE
        chatbot_id = :chatbot_id
        AND TO_CHAR(created_at, 'YYYY-MM') = :month  
    GROUP BY
        EXTRACT(MONTH FROM created_at), chatbot_id
) conv ON dr.day_of_month = conv.day_of_month
LEFT JOIN (
    SELECT
        EXTRACT(MONTH FROM created_at) AS day_of_month,
        AVG(rating_score) AS rating_average
    FROM
        conversations
    WHERE
        chatbot_id = :chatbot_id
        AND TO_CHAR(created_at, 'YYYY-MM') = :month  
    GROUP BY
        EXTRACT(MONTH FROM created_at), chatbot_id
) rate ON dr.day_of_month = rate.day_of_month
GROUP BY
    dr.day_of_month
ORDER BY
    dr.day_of_month;
"""


# Statistic visitor, rating average by month of a specific year
GET_TABLE_CONVERSATION_BY_MONTH_OF_SPECIFIC_YEAR = f"""
WITH MonthReference AS ( 
        SELECT 1 AS month_of_year 
        UNION ALL 
        SELECT 2 UNION SELECT 3 UNION SELECT 4 
        UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 
        UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 
        UNION SELECT 11 UNION SELECT 12 
)
SELECT
    mr.month_of_year AS {ChartDataTableConversationSchema.TIME_POINT},
    COALESCE(SUM(conv.visitor_count), 0) AS  {ChartDataTableConversationSchema.VISITOR_COST},
    COALESCE(AVG(rate.rating_average), 0) AS {ChartDataTableConversationSchema.RATING_AVERAGE}
FROM
    MonthReference mr
LEFT JOIN (
    SELECT
        EXTRACT(MONTH FROM created_at) AS month_of_year,
        COUNT(*) AS visitor_count
    FROM
        conversations
    WHERE
        chatbot_id = :chatbot_id
        AND TO_CHAR(created_at, 'YYYY') = :year  
    GROUP BY
        EXTRACT(MONTH FROM created_at), chatbot_id
) conv ON mr.month_of_year = conv.month_of_year
LEFT JOIN (
    SELECT
        EXTRACT(MONTH FROM created_at) AS month_of_year,
        AVG(rating_score) AS rating_average
    FROM
        conversations
    WHERE
        chatbot_id = :chatbot_id
        AND TO_CHAR(created_at, 'YYYY') = :year  
    GROUP BY
        EXTRACT(MONTH FROM created_at), chatbot_id
) rate ON mr.month_of_year = rate.month_of_year
GROUP BY
    mr.month_of_year
ORDER BY
    mr.month_of_year;
"""


# Average rating score of a specific day
GET_RATING_SCORE_OF_SPECIFIC_DAY = f"""
SELECT
    TO_CHAR(created_at, 'YYYY-MM-DD') AS selected_day,
    COALESCE(COUNT(*), 0) AS {ChartDataTableConversationSchema.VISITOR_COST},
    COALESCE(AVG(rating_score), 0) AS {ChartDataTableConversationSchema.RATING_AVERAGE}
FROM
    conversations
WHERE
    chatbot_id = :chatbot_id
    AND TO_CHAR(created_at, 'YYYY-MM-DD') = :date
GROUP BY
    TO_CHAR(created_at, 'YYYY-MM-DD')
ORDER BY
    selected_day;

"""

# Average rating score of a specific month
GET_RATING_SCORE_OF_SPECIFIC_MONTH = f"""
SELECT
    TO_CHAR(created_at, 'YYYY-MM') AS selected_month,
    COALESCE(COUNT(*), 0) AS {ChartDataTableConversationSchema.VISITOR_COST},
    COALESCE(AVG(rating_score), 0) AS {ChartDataTableConversationSchema.RATING_AVERAGE}
FROM
    conversations
WHERE
    chatbot_id = :chatbot_id
    AND TO_CHAR(created_at, 'YYYY-MM') = :month
GROUP BY
    TO_CHAR(created_at, 'YYYY-MM')
ORDER BY
    selected_month;

"""

# Average rating score of a specific year
GET_RATING_SCORE_OF_SPECIFIC_YEAR = f"""

SELECT
    TO_CHAR(created_at, 'YYYY') AS selected_year,
    COALESCE(COUNT(*), 0) AS {ChartDataTableConversationSchema.VISITOR_COST},
    COALESCE(AVG(rating_score), 0) AS {ChartDataTableConversationSchema.RATING_AVERAGE}
FROM
    conversations
WHERE
    chatbot_id = :chatbot_id
    AND TO_CHAR(created_at, 'YYYY') = :year
GROUP BY
    TO_CHAR(created_at, 'YYYY')
ORDER BY
    selected_year;


"""


# # Average latency  of a specific day
# GET_LATENCY_OF_SPECIFIC_DAY = f"""
# SELECT
# 	TO_CHAR(created_at, 'YYYY-MM-DD') AS selected_day,
#     COALESCE(AVG(rate.latency_average), 0) AS {ChartDataTableMessageSchema.LATENCY_AVERAGE}
# FROM
#     messages
# WHERE
#     latency IS NOT NULL
#     AND TO_CHAR(created_at, 'YYYY-MM-DD') = :date
# GROUP BY
#     TO_CHAR(created_at, 'YYYY-MM-DD')
# ORDER BY
#     selected_day
# """

# # Average latency  of a specific day
# GET_LATENCY_OF_SPECIFIC_MONTH = f"""
# SELECT
# 	TO_CHAR(created_at, 'YYYY-MM') AS selected_month,
#     COALESCE(AVG(rate.latency_average), 0) AS {ChartDataTableMessageSchema.LATENCY_AVERAGE}
# FROM
#     messages
# WHERE
#     latency IS NOT NULL
#     AND TO_CHAR(created_at, 'YYYY-MM') = :month
# GROUP BY
#     TO_CHAR(created_at, 'YYYY-MM')
# ORDER BY
#     selected_month

# """

# # Average latency  of a specific day
# GET_LATENCY_OF_SPECIFIC_YEAR = f"""
# SELECT
# 	TO_CHAR(created_at, 'YYYY') AS selected_year,
#     COALESCE(AVG(rate.latency_average), 0) AS {ChartDataTableMessageSchema.LATENCY_AVERAGE}
# FROM
#     conversations
# WHERE
#     latency IS NOT NULL
#     AND TO_CHAR(created_at, 'YYYY') = :year
# GROUP BY
#     TO_CHAR(ended_at, 'YYYY')
# ORDER BY
#     selected_year

# """


# Average latency  of a specific day
GET_REVENUE_OF_SPECIFIC_DAY = f"""
SELECT
	TO_CHAR(created_at, 'YYYY-MM-DD') AS selected_day,
    COALESCE(SUM(income), 0) AS {TotalDataTableRevenueSchema.REVENUE_COST}
FROM
    revenue
WHERE
    income IS NOT NULL
    AND TO_CHAR(created_at, 'YYYY-MM-DD') = :date
GROUP BY
    TO_CHAR(created_at, 'YYYY-MM-DD')
ORDER BY
    selected_day
"""

# Average latency  of a specific day
GET_REVENUE_OF_SPECIFIC_MONTH = f"""
SELECT
	TO_CHAR(created_at, 'YYYY-MM') AS selected_month,
    COALESCE(SUM(income), 0) AS {TotalDataTableRevenueSchema.REVENUE_COST}
FROM
    revenue
WHERE
    income IS NOT NULL
    AND TO_CHAR(created_at, 'YYYY-MM') = :month
GROUP BY
    TO_CHAR(created_at, 'YYYY-MM')
ORDER BY
    selected_month

"""

# Average latency  of a specific day
GET_REVENUE_OF_SPECIFIC_YEAR = f"""
SELECT
	TO_CHAR(created_at, 'YYYY') AS selected_year,
    COALESCE(SUM(income), 0) AS {TotalDataTableRevenueSchema.REVENUE_COST}
FROM
    revenue
WHERE
    income IS NOT NULL
    AND TO_CHAR(created_at, 'YYYY') = :year
GROUP BY
    TO_CHAR(created_at, 'YYYY')
ORDER BY
    selected_year

"""


class CRUDAdminDashboard:
    def get_table_message_capital_by_filter(
        self, db: Session, filter: str, value: str, conversation_id: str
    ) -> Optional[List[ChartDataTableMessageSchema]]:
        if filter == "day":
            result_proxy = db.execute(
                text(GET_TABLE_MESSAGE_BY_HOUR_OF_SPECIFIC_DAY),
                {"date": value, "conversation_id": conversation_id},
            )
        elif filter == "month":
            result_proxy = db.execute(
                text(GET_TABLE_MESSAGE_BY_DAY_OF_SPECIFIC_MONTH),
                {"month": value, "conversation_id": conversation_id},
            )
        elif filter == "year":
            result_proxy = db.execute(
                text(GET_TABLE_MESSAGE_BY_MONTH_OF_SPECIFIC_YEAR),
                {"year": value, "conversation_id": conversation_id},
            )
        else:
            logger.error(f"Filter {filter} is not valid")
            return None

        column_names = result_proxy.keys()
        results = result_proxy.fetchall()
        list_result = []
        for result in results:
            result_dict = dict(zip(column_names, result))

            chart_data = ChartDataTableMessageSchema(
                time_point=result_dict[ChartDataTableMessageSchema.TIME_POINT],
                inbox_cost=result_dict[ChartDataTableMessageSchema.INBOX_COST],
                latency_average=result_dict[
                    ChartDataTableMessageSchema.LATENCY_AVERAGE
                ],
            )
            list_result.append(chart_data)
        logger.info(
            f"Get statistic inboxes, average latency by {filter} {value} successfully with: {len(list_result)}"
        )
        return list_result

    def get_table_conversation_capital_by_filter(
        self, db: Session, filter: str, value: str, chatbot_id: str
    ) -> Optional[List[ChartDataTableConversationSchema]]:
        if filter == "day":
            result_proxy = db.execute(
                text(GET_TABLE_CONVERSATION_BY_HOUR_OF_SPECIFIC_DAY),
                {"date": value, "chatbot_id": chatbot_id},
            )
        elif filter == "month":
            result_proxy = db.execute(
                text(GET_TABLE_CONVERSATION_BY_DAY_OF_SPECIFIC_MONTH),
                {"month": value, "chatbot_id": chatbot_id},
            )
        elif filter == "year":
            result_proxy = db.execute(
                text(GET_TABLE_CONVERSATION_BY_MONTH_OF_SPECIFIC_YEAR),
                {"year": value, "chatbot_id": chatbot_id},
            )
        else:
            logger.error(f"Filter {filter} is not valid")
            return None

        column_names = result_proxy.keys()
        results = result_proxy.fetchall()
        list_result = []
        for result in results:
            result_dict = dict(zip(column_names, result))

            chart_data = ChartDataTableConversationSchema(
                time_point=result_dict[
                    ChartDataTableConversationSchema.TIME_POINT
                ],
                visitor_cost=result_dict[
                    ChartDataTableConversationSchema.VISITOR_COST
                ],
                rating_average=result_dict[
                    ChartDataTableConversationSchema.RATING_AVERAGE
                ],
            )
            list_result.append(chart_data)
        logger.info(
            f"Get statistic visitor, average rating by {filter} {value} successfully with: {len(list_result)}"
        )
        return list_result

    def get_total_rating_score_by_filter(
        self, db: Session, filter: str, value: str, chatbot_id: str
    ) -> Optional[TotalDataTableConversationSchema]:
        if filter == "day":
            result_proxy = db.execute(
                text(GET_RATING_SCORE_OF_SPECIFIC_DAY),
                {"date": value, "chatbot_id": chatbot_id},
            )
        elif filter == "month":
            result_proxy = db.execute(
                text(GET_RATING_SCORE_OF_SPECIFIC_MONTH),
                {"month": value, "chatbot_id": chatbot_id},
            )
        elif filter == "year":
            result_proxy = db.execute(
                text(GET_RATING_SCORE_OF_SPECIFIC_YEAR),
                {"year": value, "chatbot_id": chatbot_id},
            )
        else:
            logger.error(f"Filter {filter} is not valid")
            return None

        column_names = result_proxy.keys()
        results = result_proxy.fetchone()
        if results is None:
            return None
        result_dict = dict(zip(column_names, results))
        total_data = TotalDataTableConversationSchema(
            visitor_cost=result_dict[
                TotalDataTableConversationSchema.VISITOR_COST
            ],
            rating_average=result_dict[
                TotalDataTableConversationSchema.RATING_AVERAGE
            ],
        )
        logger.info(
            f"Get total visitor, average rating score by {filter} {value} successfully"
        )
        return total_data

    def get_total_revenue_by_filter(
        self, db: Session, filter: str, value: str
    ) -> Optional[TotalDataTableRevenueSchema]:
        if filter == "day":
            result_proxy = db.execute(
                text(GET_REVENUE_OF_SPECIFIC_DAY),
                {"date": value},
            )
        elif filter == "month":
            result_proxy = db.execute(
                text(GET_REVENUE_OF_SPECIFIC_MONTH),
                {"month": value},
            )
        elif filter == "year":
            result_proxy = db.execute(
                text(GET_REVENUE_OF_SPECIFIC_YEAR),
                {"year": value},
            )
        else:
            logger.error(f"Filter {filter} is not valid")
            return None

        column_names = result_proxy.keys()
        results = result_proxy.fetchone()
        if results is None or not results:
            return None
        result_dict = dict(zip(column_names, results))
        if not result_dict:
            return None
        total_data = TotalDataTableRevenueSchema(
            revenue = result_dict[TotalDataTableRevenueSchema.REVENUE_COST],
        )
        logger.info(f"Get total revenue by {filter} {value} successfully")
        return total_data


crud_admin_dashboard = CRUDAdminDashboard()

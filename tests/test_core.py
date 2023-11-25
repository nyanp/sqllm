from datetime import date

import duckdb
import pandas as pd
from numpy.testing import assert_array_equal

from sqllm.core import query


def test_query_no_ai_function_simple():
    conn = duckdb.connect()

    df = pd.DataFrame(
        {
            "a": [1, 2, 3],
            "b": ["a", "b", "c"],
            "c": [date(2021, 1, 1), date(2022, 6, 15), date(2023, 12, 31)],
        }
    )

    conn.register("df", df)

    result = query(conn, "SELECT a, c FROM df WHERE a > 1")

    assert len(result) == 2
    assert list(result.columns) == ["a", "c"]


def test_query_no_ai_function_with_join():
    conn = duckdb.connect()

    user = pd.DataFrame({"user_id": [1, 2, 3, 4, 5], "age": [24, 58, 33, 40, 15]})
    orders = pd.DataFrame(
        {
            "order_id": [1, 2, 3, 4, 5, 6, 7],
            "user_id": [3, 4, 3, 2, 1, 1, 3],
            "item_id": [1, 2, 3, 1, 2, 3, 4],
            "price": [100, 200, 300, 100, 200, 350, 150],
        }
    )
    item = pd.DataFrame({"item_id": [1, 2, 3, 4], "name": ["a", "b", "c", "d"]})

    conn.register("user", user)
    conn.register("orders", orders)
    conn.register("item", item)

    result = query(
        conn,
        """
    SELECT
        user.user_id AS user_id,
        SUM(price) AS total_purchase,
        COUNT(DISTINCT item.item_id) AS item_variety,
    FROM
        orders
        LEFT JOIN user on orders.user_id = user.user_id
        LEFT JOIN item on orders.item_id = item.item_id
    GROUP BY
        user.user_id;
    """,
    )

    result = result.sort_values(by="user_id").reset_index(drop=True)

    assert_array_equal(result["user_id"], [1, 2, 3, 4])
    assert_array_equal(result["total_purchase"], [550, 100, 550, 200])
    assert_array_equal(result["item_variety"], [2, 1, 3, 1])


def test_query_ai_function():
    conn = duckdb.connect()

    df = pd.DataFrame(
        {
            "a": [1, 2, 3],
            "b": ["a", "b", "c"],
            "c": [date(2021, 1, 1), date(2022, 6, 15), date(2023, 12, 31)],
        }
    )

    conn.register("df", df)

    result = query(conn, "SELECT a, c, ai('hello!') FROM df WHERE a > 1")
    assert list(result.columns) == ["a", "c", "ai('hello!')"]
    assert "hello" in result[result.columns[-1]].iloc[0].lower()

import duckdb
import pandas as pd

from sqllm.core import query
from sqllm.functions import sentiment


def test_sentiment():
    df = pd.DataFrame(
        {"text": ["this is awesome", "shit", "いいですね", None], "id": [1, 2, 3, 4]}
    )

    conn = duckdb.connect()
    conn.register("df", df)

    result = query(conn, "SELECT id, sentiment(text) as sentiment FROM df", [sentiment])

    assert result["sentiment"].values.tolist() == [
        "positive",
        "negative",
        "positive",
        None,
    ]


def test_ai():
    df = pd.DataFrame({"text": ["meow", "ワンワン", "bowwow", None], "id": [1, 2, 3, 4]})

    conn = duckdb.connect()
    conn.register("df", df)

    result = query(
        conn,
        'SELECT id, ai(\'If the next text is a dog sound, output "dog"; if it is a cat sound, output "cat". text: \' || text) as result FROM df',
    )

    assert result["result"].values.tolist() == ["cat", "dog", "dog", None]

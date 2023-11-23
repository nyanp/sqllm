import random
import string
from contextlib import contextmanager
from typing import Any, Callable

import duckdb
import pandas as pd

from sqllm._extract_table_names import extract_tables
from sqllm.functions import ai


def randomname(n: int) -> str:
    return "".join([random.choice(string.ascii_letters) for i in range(n)])


@contextmanager
def temp_schema(conn: Any):
    name = randomname(8)
    conn.sql(f"CREATE SCHEMA {name}")
    try:
        yield name
    finally:
        conn.sql(f"DROP SCHEMA {name} CASCADE")


def query(
    conn: Any, sql: str, functions: list[Callable[..., Any]] | None = None
) -> pd.DataFrame:
    tables = extract_tables(sql)

    functions = functions or []
    functions.append(ai)

    duckdb_conn = duckdb.connect()
    for function in functions:
        try:
            duckdb_conn.create_function(function.__name__, function)
        except Exception:
            pass

    with temp_schema(duckdb_conn) as temp:
        for table in tables:
            df = pd.read_sql(f"SELECT * FROM {table}", conn)
            duckdb_conn.register("tmp_df", df)
            duckdb_conn.sql(f"CREATE TABLE {temp}.{table} AS SELECT * FROM tmp_df")
            sql = sql.replace(table, f"{temp}.{table}")

        result = duckdb_conn.sql(sql)
        return result.df()


def query_df(
    df: pd.DataFrame, sql: str, functions: list[Callable[..., Any]] | None = None
) -> pd.DataFrame:
    conn = duckdb.connect()
    conn.register("df", df)
    return query(conn, sql, functions)

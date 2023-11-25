import os
import tempfile
from typing import Any, Callable

import duckdb
import pandas as pd

from sqllm.functions import ai


def query(
    conn: Any,
    sql: str,
    functions: list[Callable[..., Any]] | None = None,
    null_on_error: bool = True,
) -> pd.DataFrame:
    """
    Executes an SQL query and returns the results in a DataFrame.
    The query can contain the `AI` function or user-defined functions (specified in the `functions` argument).

    :param conn: A database connection object (this is passed to pd.read_sql).
    :param sql: SQL query to be executed. Note that the query must conform to the SQL syntax of duckdb, not your DB.
    :param functions: List of user-defined functions. Functions must be type-annotated.
    :param null_on_error: Determines how query execution behaves when an error occurs inside a user-defined function;
                          if True (default), null is set to the result; if False, an exception is propagated.
    :return: Result of query.
    """
    functions = functions or []
    functions.append(ai)

    with tempfile.TemporaryDirectory() as dir:
        duckdb_conn = duckdb.connect(os.path.join(dir, "duckdb.db"))
        for function in functions:
            try:
                duckdb_conn.create_function(
                    function.__name__,
                    function,
                    null_handling="special",  # type: ignore
                    exception_handling="return_null" if null_on_error else "default",  # type: ignore
                )
            except Exception:
                pass
        tables = duckdb_conn.get_table_names(sql)

        for table in tables:
            df = pd.read_sql(f"SELECT * FROM {table}", conn)
            duckdb_conn.register("tmp_df", df)
            duckdb_conn.sql(f"CREATE TABLE {table} AS SELECT * FROM tmp_df")

        result = duckdb_conn.sql(sql)
        return result.df()


def query_df(
    df: pd.DataFrame,
    sql: str,
    functions: list[Callable[..., Any]] | None = None,
    null_on_error: bool = True,
) -> pd.DataFrame:
    """
    Executes an SQL query over the dataframe and returns the results in a DataFrame.
    The query can contain the `AI` function or user-defined functions (specified in the `functions` argument).

    :param df: A dataframe. In the query, you can refer to it as "df".
    :param sql: SQL query to be executed. Note that the query must conform to the SQL syntax of duckdb, not your DB.
    :param functions: List of user-defined functions. Functions must be type-annotated.
    :param null_on_error: Determines how query execution behaves when an error occurs inside a user-defined function;
                          if True (default), null is set to the result; if False, an exception is propagated.
    :return: Result of query.
    """
    conn = duckdb.connect()
    conn.register("df", df)
    return query(conn, sql, functions, null_on_error)

import sqlite3
import re

import pandas as pd

import config


def split_queries(sql_text: str) -> dict[int, str]:
    parts = re.split(r"--\s*Query\s+(\d+)[^\n]*\n", sql_text)
    queries = {}
    for i in range(1, len(parts), 2):
        number = int(parts[i])
        body = parts[i + 1]
        statement = body.split(";")[0] + ";"
        queries[number] = statement
    return queries


def main():
    conn = sqlite3.connect(config.DB_PATH)
    sql_text = (config.BASE_DIR / "sql" / "queries.sql").read_text()
    queries = split_queries(sql_text)

    for number in sorted(queries):
        print(f"--- Query {number} ---")
        print(queries[number])
        df = pd.read_sql_query(queries[number], conn)
        print(df)
        print()


if __name__ == "__main__":
    main()
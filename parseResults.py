import re
import sqlite3
from contextlib import contextmanager


@contextmanager
def db_connection(db_name: str, commit: bool = False):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    yield cur
    cur.close()
    if commit:
        conn.commit()
    conn.close()


def parse_element(line):
    name = r"(.*)(?=;\d+ ордер)"
    order = r"(\d+) ордер*"
    completed = r"(\d+\.\d{0,2})"
    price = r";(\d+\.\d+);"
    available = r"Доступно;(.*\.\d+) "
    limit_lower = r"Лимит;.;(.*\.\d{0,2});-"
    limit_upper = r"Лимит;.*;(.+\.\d{0,2})"
    ways_to_purchase = r".*\.\d{2};(.*);Купить"
    expressions = [name, order, completed, price, available, limit_lower, limit_upper, ways_to_purchase]

    result = []
    for expr in expressions:
        match = re.search(expr, line)
        if match:
            result += match.groups()
    return result


def main():
    with open("results", 'r') as file:
        lines = file.read().split('\n')
    with db_connection('db.sqlite', commit=True) as cur:
        cur.execute("""
            create table if not exists exchange_rates(
                id Integer primary key autoincrement,
                name Text(80),
                orders Integer,
                completed Float,
                price FLoat,
                available Float,
                limit_lower Float,
                limit_upper Float,
                ways_to_purchase Text(100)
            );
        """)
        for line in lines:
            values = parse_element(line)
            cur.execute(f"""
                insert into exchange_rates(name, orders, completed, price, available, limit_lower, limit_upper, ways_to_purchase)
                values {tuple(values)}
            """)


if __name__ == "__main__":
    main()


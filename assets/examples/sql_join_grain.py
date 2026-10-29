"""Synthetic examples for /sql-join-grain/. Validated with DuckDB 1.4.5."""

from decimal import Decimal
import duckdb


SETUP = """
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    region VARCHAR,
    order_amount DECIMAL(12, 2)
);
CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    item_amount DECIMAL(12, 2)
);
CREATE TABLE attachments (
    attachment_id INTEGER PRIMARY KEY,
    order_id INTEGER
);
INSERT INTO orders VALUES (101, 'north', 100), (102, 'north', 100), (103, 'south', 80);
INSERT INTO order_items VALUES (11, 101, 60), (12, 101, 40), (21, 102, 100), (31, 103, 80);
INSERT INTO attachments VALUES (1, 101), (2, 101), (3, 102);
"""

WRONG = """
SELECT o.region,
       COUNT(*) AS joined_rows,
       COUNT(DISTINCT o.order_id) AS order_count,
       SUM(o.order_amount) AS order_amount,
       SUM(i.item_amount) AS item_amount
FROM orders o
JOIN order_items i ON o.order_id = i.order_id
JOIN attachments a ON o.order_id = a.order_id
GROUP BY o.region
ORDER BY o.region;
"""

HEADER_ONLY = """
SELECT o.region,
       COUNT(*) AS order_count,
       SUM(o.order_amount) AS order_amount
FROM orders o
WHERE EXISTS (
    SELECT 1 FROM attachments a
    WHERE a.order_id = o.order_id
)
GROUP BY o.region
ORDER BY o.region;
"""

CORRECT = """
WITH item_total AS (
    SELECT order_id, SUM(item_amount) AS item_amount
    FROM order_items
    GROUP BY order_id
)
SELECT o.region,
       COUNT(*) AS order_count,
       SUM(o.order_amount) AS order_amount,
       SUM(i.item_amount) AS item_amount,
       SUM(CASE WHEN i.order_id IS NULL THEN 1 ELSE 0 END) AS missing_item_orders
FROM orders o
LEFT JOIN item_total i ON o.order_id = i.order_id
WHERE EXISTS (
    SELECT 1 FROM attachments a
    WHERE a.order_id = o.order_id
)
GROUP BY o.region
ORDER BY o.region;
"""


def main():
    con = duckdb.connect(":memory:")
    try:
        con.execute(SETUP)
        baseline = con.execute("SELECT COUNT(*), SUM(order_amount) FROM orders").fetchall()
        assert baseline == [(3, Decimal("280.00"))], baseline
        print("all orders:", baseline)

        wrong = con.execute(WRONG).fetchall()
        assert wrong == [("north", 5, 2, Decimal("500.00"), Decimal("300.00"))], wrong
        print("wrong join:", wrong)

        rows = con.execute("""
            SELECT o.order_id, i.item_id, a.attachment_id, o.order_amount, i.item_amount
            FROM orders o
            JOIN order_items i ON o.order_id = i.order_id
            JOIN attachments a ON o.order_id = a.order_id
            ORDER BY o.order_id, i.item_id, a.attachment_id
        """).fetchall()
        assert [row[:3] for row in rows] == [(101, 11, 1), (101, 11, 2), (101, 12, 1), (101, 12, 2), (102, 21, 3)]

        distinct_amount = con.execute("""
            SELECT SUM(DISTINCT o.order_amount)
            FROM orders o
            JOIN order_items i ON o.order_id = i.order_id
            JOIN attachments a ON o.order_id = a.order_id
        """).fetchone()[0]
        assert distinct_amount == Decimal("100.00"), distinct_amount
        print("SUM(DISTINCT amount):", distinct_amount)

        distinct_after_sum = con.execute("""
            SELECT DISTINCT o.region, SUM(o.order_amount)
            FROM orders o
            JOIN order_items i ON o.order_id = i.order_id
            JOIN attachments a ON o.order_id = a.order_id
            GROUP BY o.region
        """).fetchall()
        assert distinct_after_sum == [("north", Decimal("500.00"))], distinct_after_sum

        header = con.execute(HEADER_ONLY).fetchall()
        assert header == [("north", 2, Decimal("200.00"))], header
        print("EXISTS, order grain:", header)

        correct = con.execute(CORRECT).fetchall()
        assert correct == [("north", 2, Decimal("200.00"), Decimal("200.00"), 0)], correct
        print("pre-aggregation + EXISTS:", correct)

        con.execute("INSERT INTO orders VALUES (104, 'north', 50)")
        con.execute("INSERT INTO attachments VALUES (4, 104)")
        missing = con.execute(CORRECT).fetchall()
        assert missing == [("north", 3, Decimal("250.00"), Decimal("200.00"), 1)], missing
        print("missing detail counterexample:", missing)

        con.execute("DELETE FROM attachments")
        empty = con.execute(CORRECT).fetchall()
        assert empty == [], empty
        print("no qualifying orders:", empty)
        print("PASS: all assertions; DuckDB", duckdb.__version__)
    finally:
        con.close()


if __name__ == "__main__":
    main()

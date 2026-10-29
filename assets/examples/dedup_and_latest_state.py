#!/usr/bin/env python3
"""Synthetic event-log example for /dedup-and-latest-state/.

Verified with Python 3.9.6 and DuckDB 1.4.5 on 2026-10-29.
Run: python3 dedup_and_latest_state.py
All data stays in an in-memory database; no external service is accessed.
"""

import duckdb


EVENT_CONFLICTS = """
SELECT tenant_id, event_id
FROM (
    SELECT DISTINCT tenant_id, event_id, order_id, request_id,
           source_version, status, amount, event_time
    FROM raw_events
) AS payloads
GROUP BY tenant_id, event_id
HAVING COUNT(*) > 1
ORDER BY tenant_id, event_id
"""

VERSION_CONFLICTS = """
SELECT tenant_id, order_id, source_version
FROM events
GROUP BY tenant_id, order_id, source_version
HAVING COUNT(*) > 1
ORDER BY tenant_id, order_id, source_version
"""

LATEST = """
SELECT tenant_id, order_id, request_id, source_version, status, amount
FROM (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY tenant_id, order_id
        ORDER BY source_version DESC
    ) AS state_rank
    FROM events
) AS ranked
WHERE state_rank = 1
"""

FILTER_FIRST = """
SELECT tenant_id, order_id, source_version, amount
FROM (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY tenant_id, order_id
        ORDER BY source_version DESC
    ) AS state_rank
    FROM events
    WHERE status = 'ACTIVE'
) AS ranked
WHERE state_rank = 1
"""

INGESTION_FIRST = """
SELECT tenant_id, order_id, source_version, status, amount
FROM (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY tenant_id, order_id
        ORDER BY ingested_at DESC, event_id DESC
    ) AS state_rank
    FROM events
) AS ranked
WHERE state_rank = 1
"""


def main():
    con = duckdb.connect(":memory:")
    con.execute("""
    CREATE TABLE raw_events (
        tenant_id VARCHAR NOT NULL,
        event_id VARCHAR NOT NULL,
        order_id VARCHAR NOT NULL,
        request_id VARCHAR NOT NULL,
        source_version INTEGER NOT NULL CHECK (source_version > 0),
        status VARCHAR NOT NULL CHECK (status IN ('ACTIVE', 'CANCELLED')),
        amount DECIMAL(12, 2) NOT NULL,
        event_time TIMESTAMP NOT NULL,
        ingested_at TIMESTAMP NOT NULL
    );
    """)
    con.executemany("INSERT INTO raw_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", [
        ("T1", "E01", "O100", "R100", 1, "ACTIVE", 100, "2024-06-01 10:00:00", "2024-06-01 10:00:05"),
        ("T1", "E02", "O100", "R100", 2, "CANCELLED", 100, "2024-06-01 10:10:00", "2024-06-01 10:10:05"),
        ("T1", "E02", "O100", "R100", 2, "CANCELLED", 100, "2024-06-01 10:10:00", "2024-06-01 10:12:00"),
        ("T1", "E03", "O101", "R100", 1, "ACTIVE", 100, "2024-06-01 10:20:00", "2024-06-01 10:20:05"),
        ("T1", "E04", "O200", "R200", 1, "ACTIVE", 80, "2024-06-01 11:00:00", "2024-06-01 11:30:00"),
        ("T1", "E05", "O200", "R200", 2, "CANCELLED", 80, "2024-06-01 11:10:00", "2024-06-01 11:10:05"),
        ("T1", "E06", "O300", "R300", 1, "ACTIVE", 50, "2024-06-01 12:00:00", "2024-06-01 12:00:03"),
        ("T1", "E07", "O300", "R300", 2, "CANCELLED", 50, "2024-06-01 12:05:00", "2024-06-01 12:05:01"),
        ("T1", "E08", "O300", "R300", 3, "ACTIVE", 50, "2024-06-01 12:05:00", "2024-06-01 12:05:02"),
        ("T2", "E01", "O100", "R900", 1, "ACTIVE", 200, "2024-06-01 13:00:00", "2024-06-01 13:00:05"),
    ])

    assert con.execute(EVENT_CONFLICTS).fetchall() == []
    con.execute("""
    CREATE VIEW events AS
    SELECT tenant_id, event_id, order_id, request_id,
           source_version, status, amount, event_time, ingested_at
    FROM (
        SELECT *, ROW_NUMBER() OVER (
            PARTITION BY tenant_id, event_id
            ORDER BY ingested_at ASC
        ) AS replay_rank
        FROM raw_events
    ) AS ranked
    WHERE replay_rank = 1
    """)
    assert con.execute(VERSION_CONFLICTS).fetchall() == []

    counts = con.execute("""
    SELECT (SELECT COUNT(*) FROM raw_events),
           (SELECT COUNT(*) FROM (SELECT DISTINCT * FROM raw_events)),
           (SELECT COUNT(*) FROM events)
    """).fetchone()
    assert counts == (10, 10, 9), counts
    print("raw / full-row DISTINCT / unique events:", counts)

    con.execute("CREATE VIEW latest_state AS " + LATEST)
    states = con.execute("""
    SELECT tenant_id, order_id, source_version, status
    FROM latest_state ORDER BY tenant_id, order_id
    """).fetchall()
    expected_states = [
        ("T1", "O100", 2, "CANCELLED"),
        ("T1", "O101", 1, "ACTIVE"),
        ("T1", "O200", 2, "CANCELLED"),
        ("T1", "O300", 3, "ACTIVE"),
        ("T2", "O100", 1, "ACTIVE"),
    ]
    assert states == expected_states, states
    print("latest states:", states)

    correct = con.execute("""
    SELECT COUNT(*), SUM(amount) FROM latest_state WHERE status = 'ACTIVE'
    """).fetchone()
    wrong_filter = con.execute("SELECT COUNT(*), SUM(amount) FROM (" + FILTER_FIRST + ")").fetchone()
    wrong_arrival = con.execute("""
    SELECT COUNT(*), SUM(amount) FROM (
    """ + INGESTION_FIRST + ") WHERE status = 'ACTIVE'").fetchone()
    assert correct == (3, 350), correct
    assert wrong_filter == (5, 530), wrong_filter
    assert wrong_arrival == (4, 430), wrong_arrival
    print("latest then filter:", correct)
    print("filter then latest (wrong):", wrong_filter)
    print("latest arrival (wrong):", wrong_arrival)

    # An identical replay must not change the state or total amount.
    con.execute("BEGIN TRANSACTION")
    con.execute("INSERT INTO raw_events SELECT * FROM raw_events WHERE tenant_id = 'T1' AND event_id = 'E08'")
    replayed = con.execute("SELECT COUNT(*), SUM(amount) FROM latest_state WHERE status = 'ACTIVE'").fetchone()
    assert replayed == correct
    con.execute("ROLLBACK")

    # Two different payloads for one event ID must be rejected before dedup.
    con.execute("BEGIN TRANSACTION")
    con.execute("""
    INSERT INTO raw_events
    SELECT tenant_id, event_id, order_id, request_id, source_version,
           status, amount + 1, event_time, ingested_at
    FROM raw_events WHERE tenant_id = 'T1' AND event_id = 'E03'
    """)
    assert con.execute(EVENT_CONFLICTS).fetchall() == [("T1", "E03")]
    con.execute("ROLLBACK")

    # A deterministic tie-breaker cannot establish which source state is true.
    con.execute("BEGIN TRANSACTION")
    con.execute("""
    INSERT INTO raw_events
    SELECT tenant_id, 'E99', order_id, request_id, source_version,
           'CANCELLED', amount, event_time, ingested_at
    FROM raw_events WHERE tenant_id = 'T1' AND event_id = 'E08'
    """)
    assert con.execute(EVENT_CONFLICTS).fetchall() == []
    assert con.execute(VERSION_CONFLICTS).fetchall() == [("T1", "O300", 3)]
    con.execute("ROLLBACK")

    # A later delivery of an older source version must not roll the state back.
    con.execute("BEGIN TRANSACTION")
    con.execute("DELETE FROM raw_events WHERE tenant_id = 'T1' AND event_id = 'E04'")
    before_late = con.execute("SELECT source_version, status FROM latest_state WHERE tenant_id = 'T1' AND order_id = 'O200'").fetchone()
    con.execute("""
    INSERT INTO raw_events VALUES
    ('T1', 'E04', 'O200', 'R200', 1, 'ACTIVE', 80,
     '2024-06-01 11:00:00', '2024-06-01 11:30:00')
    """)
    after_late = con.execute("SELECT source_version, status FROM latest_state WHERE tenant_id = 'T1' AND order_id = 'O200'").fetchone()
    assert before_late == after_late == (2, "CANCELLED")
    con.execute("ROLLBACK")

    print("Replay, conflicting payload, version conflict and late-arrival checks passed.")
    con.close()


if __name__ == "__main__":
    main()

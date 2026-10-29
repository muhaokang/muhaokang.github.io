"""A small data-readiness gate using synthetic batch metadata only.

Run with Python 3.9+: python3 data_readiness.py
No network access, database connection, scheduling or production writes.
"""

from dataclasses import dataclass, replace
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class Snapshot:
    business_date: str
    publish_state: str
    manifest_snapshot: str
    observed_snapshot: str
    expected_rows: Optional[int]
    observed_rows: Optional[int]
    query_ok: bool = True


@dataclass(frozen=True)
class Verdict:
    status: str
    reasons: Tuple[str, ...]


def check_readiness(
    business_date: str,
    required_sources: Tuple[str, ...],
    snapshots: Dict[str, Snapshot],
) -> Verdict:
    """Assume snapshots is a successful, complete query of the batch catalog.

    query_ok describes whether a source snapshot could be inspected. If the
    catalog query itself fails, the caller must return UNKNOWN instead of
    passing an empty dictionary. A known BLOCK takes priority over UNKNOWN,
    while reasons retain both kinds of evidence. Only PASS permits consumption.
    """
    blocked = []
    unknown = []
    for source in required_sources:
        snapshot = snapshots.get(source)
        if snapshot is None:
            blocked.append(source + ": missing readiness record")
            continue
        # Catalog evidence remains usable even if inspecting the data fails.
        if snapshot.business_date != business_date:
            blocked.append(source + ": wrong business date")
        if snapshot.publish_state != "COMPLETE":
            blocked.append(source + ": batch not published")
        if not snapshot.manifest_snapshot:
            unknown.append(source + ": manifest snapshot identity unavailable")
        if snapshot.expected_rows is None:
            unknown.append(source + ": expected row count unavailable")
        elif snapshot.expected_rows < 0:
            unknown.append(source + ": invalid expected row count")

        if not snapshot.query_ok:
            unknown.append(source + ": snapshot query failed")
            continue
        if not snapshot.observed_snapshot:
            unknown.append(source + ": observed snapshot identity unavailable")
        elif snapshot.manifest_snapshot and snapshot.manifest_snapshot != snapshot.observed_snapshot:
            blocked.append(source + ": manifest/snapshot mismatch")
        if snapshot.observed_rows is None:
            unknown.append(source + ": observed row count unavailable")
        elif snapshot.observed_rows < 0:
            unknown.append(source + ": invalid observed row count")
        elif snapshot.expected_rows is not None and snapshot.expected_rows >= 0 and snapshot.expected_rows != snapshot.observed_rows:
            blocked.append(source + ": row count mismatch")
    reasons = tuple("BLOCK " + item for item in blocked)
    reasons += tuple("UNKNOWN " + item for item in unknown)
    status = "BLOCK" if blocked else "UNKNOWN" if unknown else "PASS"
    return Verdict(status, reasons)


def main():
    target_date = "2025-09-13"
    required_sources = ("orders", "settlements")
    baseline = {
        "orders": Snapshot(target_date, "COMPLETE", "orders-v2", "orders-v2", 100, 100),
        "settlements": Snapshot(target_date, "COMPLETE", "settlements-v1", "settlements-v1", 80, 80),
    }

    def change_settlements(**changes):
        return dict(baseline, settlements=replace(baseline["settlements"], **changes))

    cases = [
        ("ready", baseline, "PASS"),
        ("stale_partition", change_settlements(business_date="2025-09-12"), "BLOCK"),
        ("partition_created", change_settlements(publish_state="RUNNING", observed_rows=0), "BLOCK"),
        ("partial_load", change_settlements(observed_rows=50), "BLOCK"),
        ("wrong_snapshot", change_settlements(observed_snapshot="settlements-v0"), "BLOCK"),
        ("missing_source", {"orders": baseline["orders"]}, "BLOCK"),
        ("query_failed", change_settlements(query_ok=False, observed_rows=None), "UNKNOWN"),
        ("empty_without_evidence", change_settlements(expected_rows=None, observed_rows=0), "UNKNOWN"),
        ("valid_empty_batch", change_settlements(expected_rows=0, observed_rows=0), "PASS"),
    ]
    for name, snapshots, expected in cases:
        verdict = check_readiness(target_date, required_sources, snapshots)
        assert verdict.status == expected, (name, verdict, expected)
        print(name + ": " + verdict.status)

    # A known defect remains a BLOCK even if another source cannot be inspected.
    mixed = {
        "orders": replace(baseline["orders"], business_date="2025-09-12"),
        "settlements": replace(baseline["settlements"], query_ok=False),
    }
    verdict = check_readiness(target_date, required_sources, mixed)
    assert verdict.status == "BLOCK"
    assert any(reason.startswith("BLOCK ") for reason in verdict.reasons)
    assert any(reason.startswith("UNKNOWN ") for reason in verdict.reasons)
    print("mixed_evidence: " + verdict.status + " (both reasons retained)")

    # Both known catalog defects and failed inspection can belong to one source.
    same_source = change_settlements(
        business_date="2025-09-12", publish_state="RUNNING", query_ok=False,
        observed_snapshot="", observed_rows=None,
    )
    verdict = check_readiness(target_date, required_sources, same_source)
    assert verdict.status == "BLOCK"
    assert "BLOCK settlements: wrong business date" in verdict.reasons
    assert "BLOCK settlements: batch not published" in verdict.reasons
    assert "UNKNOWN settlements: snapshot query failed" in verdict.reasons
    assert not any("observed" in reason for reason in verdict.reasons)
    print("same_source_mixed_evidence: " + verdict.status + " (all known reasons retained)")
    print("All 11 scenarios passed.")


if __name__ == "__main__":
    main()

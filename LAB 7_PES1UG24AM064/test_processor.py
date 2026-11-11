"""Lab 7 - Fuzz tests for processor.py using Hypothesis.

The first three tests are the ones from the starter file: they feed random
Unicode text (and None) into each function and check that it never crashes
and that the returned value has the expected type/shape.

The last two tests build "almost valid" inputs (CSV of numbers, Driver:Days:
Category records) so Hypothesis can also reach edge cases that plain random
text rarely hits, such as nan/inf/negative mileage or zero/negative days.
"""
import math
import re

from hypothesis import given, settings, strategies as st

from processor import sanitize_license_plate, parse_trip_mileage, format_rental_invoice

DELIMITERS = ['-', ' ', '_', '#']
INVOICE_TAIL = re.compile(r"for (-?\d+) days: Total \$(-?\d+\.\d+)$")


# ---------------------------------------------------------------------------
# 1. sanitize_license_plate
# ---------------------------------------------------------------------------
@settings(max_examples=500)
@given(st.text() | st.none())
def test_sanitize_license_plate_no_crash(s):
    try:
        result = sanitize_license_plate(s)
    except Exception as e:
        assert False, f"sanitize_license_plate crashed on {s!r} with: {type(e).__name__}: {e}"

    assert isinstance(result, str), f"expected str, got {type(result).__name__}"
    for ch in DELIMITERS:
        assert ch not in result, f"delimiter {ch!r} left in output {result!r}"


# ---------------------------------------------------------------------------
# 2. parse_trip_mileage
# ---------------------------------------------------------------------------
def check_mileage_list(s, result):
    assert isinstance(result, list), f"expected list, got {type(result).__name__}"
    for m in result:
        assert isinstance(m, float), f"non-float value {m!r} in result for {s!r}"
        assert math.isfinite(m), f"non-finite mileage {m!r} accepted from {s!r}"
        assert m >= 0, f"negative mileage {m!r} accepted from {s!r}"


@settings(max_examples=500)
@given(st.text() | st.none())
def test_parse_trip_mileage_safe(s):
    try:
        result = parse_trip_mileage(s)
    except Exception as e:
        assert False, f"parse_trip_mileage crashed on {s!r} with: {type(e).__name__}: {e}"

    check_mileage_list(s, result)


# CSV built from real floats (including nan, inf, negatives), random words and
# empty fields, joined with commas and optional spaces.
mileage_token = st.floats(allow_nan=True, allow_infinity=True).map(str) | st.text(max_size=5)
mileage_csv = st.lists(mileage_token, max_size=6).map(", ".join)


@settings(max_examples=500)
@given(mileage_csv)
def test_parse_trip_mileage_csv_like(s):
    try:
        result = parse_trip_mileage(s)
    except Exception as e:
        assert False, f"parse_trip_mileage crashed on {s!r} with: {type(e).__name__}: {e}"

    check_mileage_list(s, result)


# ---------------------------------------------------------------------------
# 3. format_rental_invoice
# ---------------------------------------------------------------------------
@settings(max_examples=500)
@given(st.text() | st.none())
def test_format_rental_invoice_safe(s):
    try:
        result = format_rental_invoice(s)
    except Exception as e:
        assert False, f"format_rental_invoice crashed on {s!r} with: {type(e).__name__}: {e}"

    assert isinstance(result, str), f"expected str, got {type(result).__name__}"


# Records shaped like Driver:Days:Category with random parts, so the days
# field is often a real (possibly zero or negative) integer.
days_field = st.integers(min_value=-1000, max_value=1000).map(str) | st.text(max_size=4)
record = st.tuples(st.text(max_size=8), days_field,
                   st.sampled_from(["SUV", "suv", "Sedan", "", " "]) | st.text(max_size=6))


@settings(max_examples=500)
@given(record)
def test_format_rental_invoice_record_like(parts):
    s = ":".join(parts)
    try:
        result = format_rental_invoice(s)
    except Exception as e:
        assert False, f"format_rental_invoice crashed on {s!r} with: {type(e).__name__}: {e}"

    assert isinstance(result, str), f"expected str, got {type(result).__name__}"
    # A zero/negative rental must never produce a bill (or a negative total).
    billed = INVOICE_TAIL.search(result)
    if billed:
        days, total = int(billed.group(1)), float(billed.group(2))
        assert days > 0, f"non-positive rental ({days} days) billed for {s!r}: {result!r}"
        assert total > 0, f"non-positive total ${total} billed for {s!r}: {result!r}"

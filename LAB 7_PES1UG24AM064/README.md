# LAB 7 — Fuzzing for Input Validation Bugs (PES1UG24AM064)

Assigned program: **L6_L7_02 — Car Rental Rate** (`Lab 7/processor.py`)

## Deliverables

| File | Description |
|------|-------------|
| `PES1UG24AM064_SE_LAB7_Report.pdf` | Report with screenshots for Steps 1–6 |
| `processor.py` | Fixed (hardened) application script |
| `test_processor.py` | Completed Hypothesis fuzz tests |
| `screenshots/` | Terminal output screenshots used in the report |

The original buggy starter `processor.py` is in this folder's first commit.

## Results

| Run | Result |
|-----|--------|
| `python processor.py` (buggy) | Crashes with `ValueError` on `100.5,,80.0` and `Ravi:three:SUV` |
| `python -m pytest test_processor.py` (buggy) | **5 failed** |
| `python processor.py` (fixed) | Malformed input handled with clear messages |
| `python -m pytest test_processor.py` (fixed) | **5 passed** |

## Bugs found by Hypothesis

- `sanitize_license_plate(None)` → `AttributeError`
- `parse_trip_mileage(None)` / `''` / `'100.5,,80.0'` → `AttributeError` / `ValueError`
- `parse_trip_mileage('INF')`, `('-1.0')` → non-finite / negative mileage accepted
- `format_rental_invoice(None)`, `''`, `':'`, `'::SUV'` → `AttributeError` / `IndexError` / `ValueError`
- `format_rental_invoice(':0:SUV')`, `(':-1:SUV')` → zero/negative rental billed

## How to run

```bash
pip install hypothesis pytest
python processor.py
python -m pytest test_processor.py
```

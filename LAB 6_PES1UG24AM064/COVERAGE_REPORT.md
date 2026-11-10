# Lab 6 – Code and Branch Coverage Analysis

**Name:** Bandugula Sai Rithesh Reddy  **SRN:** PES1UG24AM064
**Program:** `car_rental_rate.py` (repo `L6_L7_02_car_rental_rate`)

## Results (`car_rental_rate.py`)

| Test file | Tests | Line coverage | Branch coverage |
|-----------|-------|---------------|-----------------|
| `test_car_rental.py` (starter) | 1 | 47% (27 of 51 lines missed) | 44% (10 partial branches) |
| `CodeCoverageTest_PES1UG24AM064_application.py` | 9 | **100%** | 100% |
| `BranchCoverageTest_PES1UG24AM064_application.py` | 32 | **100%** | **100%** (36/36 branches, 0 partial) |

Screenshots of the terminal output:
- `screenshots/code_coverage_line_report.png`
- `screenshots/branch_coverage_report.png`

## Commands

```bash
pip install coverage pytest

# Code (line) coverage
coverage run -m pytest CodeCoverageTest_PES1UG24AM064_application.py
coverage report -m

# Branch coverage
coverage run --branch -m pytest BranchCoverageTest_PES1UG24AM064_application.py
coverage report -m
```

## Approach

**Code coverage tests:** one test per group of missed lines from the starter report. The tests cover the invalid-input `raise`, unconfirmed and zero-day rentals, the luxury and SUV rates, negative and long trip segments (with the under-21 penalty and `break`), the under-25 surcharge, the `HIGH_RISK_AUDIT` and `EMPTY_BATCH` statuses, and all three telematics results.

**Branch coverage tests:** every decision is tested for both its True and False outcome, using boundary values:
- Input check: `rentals` not a list, a dict instead of a list, `base_admin_fee < 0`, and a valid empty list with fee 0.
- `is_confirmed`: False, missing (defaults to False) and True. Missing fields fall back to their defaults.
- `days <= 0`: days 0, -3 and 1.
- Vehicle type: luxury, SUV, economy and an unknown type (else branch).
- Trip segments: miles -1, 0, 300 (not > 300) and 301. Age 20 vs 21 for the long-trip penalty and `break`. An empty segment list, so the loop body is skipped.
- Under-25 surcharge: age 24 vs 25, and both sides of the luxury ternary.
- Final status: exactly 4 flags vs 5 flags, an audit with zero revenue, and several rentals summed and rounded.
- Telematics: empty list and `None`, speed 100 vs 101, a streak that resets, a streak of 1 at the end of a log, a streak of 2, a streak in the second vehicle, and streaks that reset between vehicles.

## Line vs branch coverage
The starter test shows the gap: line coverage was 47% but branch coverage was only 44%, because 10 decisions were taken in only one direction.

In this module, the 9 line-coverage tests also happen to take every branch both ways, so coverage.py reports 100% for both. They do not test the edges of each condition, though. There is no test for `miles == 300`, `driver_age == 21`/`25`, `days == 0` vs `1`, exactly 4 vs 5 risk flags, speed `100` vs `101`, missing dictionary keys, a `None` telematics matrix, or a streak that resets between vehicles. The branch coverage file tests each decision on purpose, on both sides of its boundary. That catches mistakes such as `>` written instead of `>=`, which coverage percentages alone would not reveal.

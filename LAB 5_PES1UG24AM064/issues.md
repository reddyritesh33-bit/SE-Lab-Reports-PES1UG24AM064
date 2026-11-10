# Lab 5 – Issue Table

**Name:** Bandugula Sai Rithesh Reddy  **SRN:** PES1UG24AM064
**Program:** `pos_system.py` (Retail Point of Sale & Discount Tracker, repo `L5_02_retail_pos`)

Line numbers refer to the original `pos_system.py`. High and medium severity issues are listed first.

| # | Issue | Type | Tool / Code | Severity | Line(s) | Description | Fix Approach |
|---|-------|------|-------------|----------|---------|-------------|--------------|
| 1 | Use of `eval()` on user input | Security | Bandit B307, Pylint W0123 | **High** (Bandit: Medium, High confidence) | 27, 51-52 | The promo code from `input()` was passed straight to `eval()`, so a user could run any Python code (e.g. `__import__('os').system(...)`). | Replaced `eval` with a regex (`total <op> <number>`) and an `operator` lookup table that allows only `*` and `-`. Invalid codes are logged and ignored. |
| 2 | Mutable default argument | Bug | Pylint W0102 | Medium | 10 | `receipts=[]` is created once and shared by every call, so receipts leaked between checkouts. | Default changed to `None` and a new list is created inside the method. |
| 3 | Bare `except:` hides errors (wrong totals) | Bug | Pylint W0702, Flake8 E722 | Medium | 16-17 | Any error, including an unknown item (`laptop`) or a string quantity (`"2"`), was silently turned into `+ 0`, giving wrong bills. | Removed the try/except and added explicit checks: unknown items and non-positive or non-integer quantities are skipped with a logged warning. |
| 4 | `try/except Exception: pass` and no-op stock update | Security/Bug | Bandit B110, Pylint W0718 | Medium | 29-34 | `update_stock` assigned `price_list[item]` to itself (so it never changed stock) and hid every exception. | Added a real `STOCK` dict, `STOCK[item] += qty`, and catch only `KeyError`, logging a warning. |
| 5 | Negative quantity / negative tax accepted | Logic bug | Found by running the program (not flagged by tools) | Medium | 47-48 | `("bottle", -4)` gave a bill of **-630.0**, and `tax_rate=-1` was allowed. | Quantities must be positive ints; tax rate must be between 0 and 1, otherwise the default 5% is used. Promo results are clamped at 0. |
| 6 | File opened without `with` / encoding | Bug (resource leak) | Pylint R1732, W1514 | Medium | 37 | The log file was never closed and used the platform's default encoding. | `with open(file, "a", encoding="utf-8") as log_file:` |
| 7 | Use of `global` and mutable module state | Design | Pylint W0603, C0103 | Low | 7-8, 11 | `sales_total` was modified through `global`, which makes the code hard to test. | Moved the state into a `PosRegister` class (`sales_total`, `receipt_lines`, receipt counter). Constants renamed to UPPER_CASE. |
| 8 | Insecure pseudo-random receipt numbers | Security | Bandit B311 | Low | 21 | `random.randint` was used for receipt IDs, which can collide and is predictable. | Sequential unique IDs from `itertools.count(1001)`. |
| 9 | Unused imports / unused variable | Style | Pylint W0611/W0612, Flake8 F401/F841 | Low | 1, 3, 26 | `json` was imported but never used. `logging` was imported but unused, and `total` in `apply_promo_code` was unused. | Removed `json` and the unused variable. `logging` is now actually used for warnings. |
| 10 | Missing docstrings, camelCase name, `%` formatting | Style | Pylint C0114/C0116/C0103/C0209 | Low | 1, 10-44 | No module or function docstrings, `printSales` was not snake_case, and old `%` string formatting was used. | Added docstrings, renamed to `print_sales`, and used f-strings. |
| 11 | PEP 8 formatting | Style | Flake8 E302, E305, E501 | Low | 10-56 | One blank line between functions, a line over 79 characters, and `main()` called at import time. | Two blank lines around definitions, lines wrapped, and an `if __name__ == "__main__":` guard added. |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 5.65/10 (20 messages) | **10.00/10** |
| Bandit | 3 issues (1 Medium, 2 Low) | **0 issues** |
| Flake8 | 12 violations | **0 violations** |

Reports: `pylint_report_before.txt`, `bandit_report_before.txt`, `flake8_report_before.txt` and the matching `*_after.txt` files.

## Commits (one per tool)
1. `Fix Bandit issues: replace eval, insecure random and try/except/pass`
2. `Fix Pylint issues and checkout logic bugs (score 5.65 -> 10.00)`
3. `Fix Flake8 issues: PEP 8 blank lines, line length and main guard`

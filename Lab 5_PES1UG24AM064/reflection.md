# Lab 5 – Reflection

**Name:** Bandugula Sai Rithesh Reddy  **SRN:** PES1UG24AM064

### 1. Which issues were the easiest to fix, and which were the hardest? Why?
The easiest were the style issues from Flake8 and Pylint: unused imports, missing blank lines (E302/E305), long lines, missing docstrings and the camelCase `printSales` name. Each one points at an exact line and has one obvious fix.

The hardest was the `eval()` call in `apply_promo_code` (Bandit B307). Deleting it would break the promo feature, so I had to write a small safe parser: a regex for `total * x` / `total - x` plus an operator table. Removing the bare `except:` was also tricky. Once the error-hiding was gone I had to decide what *should* happen for an unknown item, a string quantity or a negative quantity. That turned a style warning into real validation logic. Removing `global sales_total` required moving the state into a `PosRegister` class.

### 2. Did the static analysis tools report any false positives? If so, describe one example.
There were no true false positives, but some findings matter less in this context. Bandit B311 (pseudo-random generator) is meant for cryptographic use, and a receipt number is not a secret. I still changed it to a sequential counter because unique, ordered receipt numbers are better for a shop anyway. Pylint W0603 (`global`) is also a design opinion rather than a bug in a script this small.

The tools also missed the most visible bug: `process_checkout([("bottle", -4)])` returned a bill of **-630.0**, and a negative `tax_rate` was accepted. I only found this by running the program and reading the output. Static analysis does not replace testing.

### 3. How would you integrate static analysis tools into your actual software development workflow?
- **Locally:** run Flake8 and Pylint automatically through a `pre-commit` hook and in the editor (VS Code Pylance/Flake8 extensions), so style issues are fixed before code is committed.
- **CI pipeline:** add a GitHub Actions job that runs `flake8`, `pylint --fail-under=9.5` and `bandit -r . -ll` on every push and pull request. The build fails on Medium/High Bandit findings or a Pylint score below the threshold.
- **Shared configuration:** keep a `.pylintrc`/`setup.cfg` in the repo so the whole team uses the same rules, and use `# nosec` / `# pylint: disable=` only with a written reason.

### 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?
- **Security:** the program no longer executes arbitrary user input. Entering `__import__('os')` as a promo code is now rejected instead of being run.
- **Correctness:** bills can't go negative, unknown items and invalid quantities are reported with a warning instead of being silently priced at 0, receipts no longer leak between calls (mutable default fixed), and `update_stock` really updates stock.
- **Robustness:** the log file is always closed (`with` + `utf-8`), and only specific exceptions are caught.
- **Readability and maintainability:** a `PosRegister` class replaces global state, every function has a docstring, names follow PEP 8, and the module can be imported without running `main()`.
- **Measured results:** Pylint went from 5.65 to 10.00/10, Bandit from 3 issues to 0, and Flake8 from 12 violations to 0.

"""Retail point-of-sale script.

Totals carts with tax, applies promo codes and logs receipts.
"""
import itertools
import logging
import operator
import re

PRICE_LIST = {"pen": 10, "notebook": 45, "bag": 799, "bottle": 150}
STOCK = {"pen": 100, "notebook": 50, "bag": 10, "bottle": 30}
PROMO_PATTERN = re.compile(r"^\s*total\s*([*\-])\s*(\d+(?:\.\d+)?)\s*$")
PROMO_OPERATORS = {"*": operator.mul, "-": operator.sub}
DEFAULT_TAX_RATE = 0.05

logging.basicConfig(level=logging.WARNING,
                    format="%(levelname)s: %(message)s")


class PosRegister:
    """Keeps the running sales total and the receipts of one register."""

    def __init__(self):
        self.sales_total = 0.0
        self.receipt_lines = []
        self._receipt_counter = itertools.count(1001)

    def process_checkout(self, cart_items, tax_rate=DEFAULT_TAX_RATE,
                         receipts=None):
        """Total a cart of (item, quantity) pairs and record the receipt."""
        if receipts is None:
            receipts = []
        if not 0 <= tax_rate <= 1:
            logging.warning("Invalid tax rate %r, using default %.2f",
                            tax_rate, DEFAULT_TAX_RATE)
            tax_rate = DEFAULT_TAX_RATE
        subtotal = 0
        for name, qty in cart_items:
            if name not in PRICE_LIST:
                logging.warning("Unknown item %r skipped", name)
                continue
            if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
                logging.warning("Invalid quantity %r for %r skipped",
                                qty, name)
                continue
            subtotal += PRICE_LIST[name] * qty
        total = round(subtotal * (1 + tax_rate), 2)
        receipts.append(total)
        self.sales_total = round(self.sales_total + total, 2)
        receipt_no = next(self._receipt_counter)
        self.receipt_lines.append(f"Receipt #{receipt_no} total={total:.2f}")
        return total

    def apply_promo_code(self, code_str):
        """Apply a promo code like "total * 0.9" or "total - 50".

        The code is parsed safely instead of being passed to eval().
        """
        match = PROMO_PATTERN.match(code_str)
        if not match:
            logging.warning("Invalid promo code %r ignored", code_str)
            return self.sales_total
        op_symbol, value = match.groups()
        new_total = PROMO_OPERATORS[op_symbol](self.sales_total, float(value))
        return round(max(new_total, 0), 2)

    def save_receipt_log(self, file="pos_log.txt"):
        """Append all receipts to the log file."""
        with open(file, "a", encoding="utf-8") as log_file:
            for line in self.receipt_lines:
                log_file.write(line + "\n")

    def print_sales(self):
        """Print the running sales total."""
        print(f"Sales so far: {self.sales_total:.2f}")


def update_stock(item, qty):
    """Add qty units of item to the stock."""
    try:
        STOCK[item] += qty
        print("Stock updated for", item, "by", qty)
    except KeyError:
        logging.warning("Cannot update stock: unknown item %r", item)


def main():
    """Run a sample day of sales."""
    register = PosRegister()
    print("Bill 1:", register.process_checkout([("pen", 3), ("notebook", 2)]))
    print("Bill 2:", register.process_checkout([("bag", 1), ("laptop", 1)]))
    print("Bill 3:", register.process_checkout([("bottle", -4)]))
    print("Bill 4:", register.process_checkout([("pen", "2")], tax_rate=-1))
    update_stock("laptop", 5)
    print("After promo:", register.apply_promo_code("total * 0.9"))
    code = input("Enter promo code (e.g. total - 50): ") or "total - 50"
    print("After your promo:", register.apply_promo_code(code))
    register.save_receipt_log()
    register.print_sales()


if __name__ == "__main__":
    main()

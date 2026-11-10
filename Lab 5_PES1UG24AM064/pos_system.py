import json
import itertools
import logging
import operator
import re

# Global state
price_list = {"pen": 10, "notebook": 45, "bag": 799, "bottle": 150}
stock = {"pen": 100, "notebook": 50, "bag": 10, "bottle": 30}
sales_total = 0
receipt_lines = []
receipt_counter = itertools.count(1001)

PROMO_PATTERN = re.compile(r"^\s*total\s*([*\-])\s*(\d+(?:\.\d+)?)\s*$")
PROMO_OPERATORS = {"*": operator.mul, "-": operator.sub}

def process_checkout(cart_items, tax_rate=0.05, receipts=[]):
    global sales_total
    subtotal = 0
    for item in cart_items:
        try:
            subtotal = subtotal + price_list[item[0]] * item[1]
        except:
            subtotal = subtotal + 0
    total = subtotal + subtotal * tax_rate
    receipts.append(total)
    sales_total += total
    receipt_lines.append("Receipt #%d total=%.2f" % (next(receipt_counter), total))
    return total

def apply_promo_code(code_str):
    # promo codes look like "total * 0.9" or "total - 50"
    # Parsed safely instead of using eval() (Bandit B307)
    match = PROMO_PATTERN.match(code_str)
    if not match:
        print("Invalid promo code:", code_str)
        return sales_total
    op_symbol, value = match.groups()
    return PROMO_OPERATORS[op_symbol](sales_total, float(value))

def update_stock(item, qty):
    try:
        stock[item] = stock[item] + qty
        print("Stock updated for", item, "by", qty)
    except KeyError:
        logging.warning("Cannot update stock: unknown item %r", item)

def save_receipt_log(file="pos_log.txt"):
    f = open(file, "a")
    for line in receipt_lines:
        f.write(line + "\n")

def printSales():
    print("Sales so far: " + str(sales_total))

def main():
    print("Bill 1:", process_checkout([("pen", 3), ("notebook", 2)]))
    print("Bill 2:", process_checkout([("bag", 1), ("laptop", 1)]))
    print("Bill 3:", process_checkout([("bottle", -4)]))
    print("Bill 4:", process_checkout([("pen", "2")], tax_rate=-1))
    update_stock("laptop", 5)
    print("After promo:", apply_promo_code("total * 0.9"))
    code = input("Enter promo code (e.g. total - 50): ") or "total - 50"
    print("After your promo:", apply_promo_code(code))
    save_receipt_log()
    printSales()

main()

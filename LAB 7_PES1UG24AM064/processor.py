"""Car rental input processor - hardened version (Lab 7).

Every function validates its input and returns a safe value instead of
raising, so random / malformed input found by fuzzing can no longer crash it.
"""
import math

PLATE_DELIMITERS = ['-', ' ', '_', '#']
SUV_DAILY_RATE = 50.0
DEFAULT_DAILY_RATE = 30.0
MAX_RENTAL_DAYS = 365
INVALID_RECORD = "Invalid rental record"


def sanitize_license_plate(plate):
    """Remove delimiters/whitespace and upper-case the plate.

    Non-string input (e.g. None) returns an empty string.
    """
    if not isinstance(plate, str):
        return ""
    plate = plate.strip()
    for ch in PLATE_DELIMITERS:
        plate = plate.replace(ch, '')
    # Drop any remaining whitespace such as tabs or newlines inside the plate.
    plate = "".join(plate.split())
    return plate.upper()


def parse_trip_mileage(mileage_csv):
    """Parse a comma separated list of mileages.

    Empty fields, non-numeric text, nan/inf and negative values are skipped.
    Non-string input returns an empty list.
    """
    if not isinstance(mileage_csv, str):
        return []
    mileages = []
    for part in mileage_csv.split(','):
        part = part.strip()
        if not part:
            continue
        try:
            value = float(part)
        except ValueError:
            continue
        if not math.isfinite(value) or value < 0:
            continue
        mileages.append(value)
    return mileages


def format_rental_invoice(record):
    """Build an invoice line from a 'Driver:Days:Category' record.

    Malformed records return a message starting with 'Invalid rental record'
    instead of raising.
    """
    if not isinstance(record, str):
        return f"{INVALID_RECORD}: input must be text"

    parts = record.split(':')
    if len(parts) != 3:
        return f"{INVALID_RECORD}: expected Driver:Days:Category"

    driver = parts[0].strip()
    days_text = parts[1].strip()
    category = parts[2].strip()

    if not driver:
        return f"{INVALID_RECORD}: driver name is missing"
    if not category:
        return f"{INVALID_RECORD}: category is missing"
    if not (days_text.isascii() and days_text.isdigit()):
        return f"{INVALID_RECORD}: days must be a whole number"

    days = int(days_text)
    if days < 1 or days > MAX_RENTAL_DAYS:
        return f"{INVALID_RECORD}: days must be between 1 and {MAX_RENTAL_DAYS}"

    daily_rate = SUV_DAILY_RATE if category.lower() == "suv" else DEFAULT_DAILY_RATE
    total = days * daily_rate
    return f"Driver {driver} booked {category} for {days} days: Total ${total:.2f}"


def main():
    print("==== Running sanitize_license_plate ====")
    raw_plate = input("Enter license plate with delimiters (-, _, #): ")
    clean_plate = sanitize_license_plate(raw_plate)
    if clean_plate:
        print("Sanitized Plate:", clean_plate)
    else:
        print("Sanitized Plate: <empty> (no valid characters entered)")

    print("\n==== Running parse_trip_mileage ====")
    csv_input = input("Enter CSV of mileages (e.g. 100.5, 45.2, 80.0): ")
    mileage_list = parse_trip_mileage(csv_input)
    print("Parsed Mileage List:", mileage_list)
    skipped = len(csv_input.split(',')) - len(mileage_list)
    if skipped:
        print(f"Note: {skipped} empty/invalid value(s) skipped")

    print("\n==== Running format_rental_invoice ====")
    record_input = input("Enter rental record (Driver:Days:Category): ")
    invoice = format_rental_invoice(record_input)
    print("Rental Invoice:", invoice)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nInput ended - exiting.")

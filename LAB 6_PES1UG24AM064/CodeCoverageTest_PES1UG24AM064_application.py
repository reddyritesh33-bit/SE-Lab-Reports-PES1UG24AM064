"""Code (line/statement) coverage tests for car_rental_rate.py.

Name: Bandugula Sai Rithesh Reddy    SRN: PES1UG24AM064

Each test is aimed at executing statements that the starter test
did not reach, so that every line of the module runs at least once.
Run with:
    coverage run -m pytest CodeCoverageTest_PES1UG24AM064_application.py
    coverage report -m
"""
import pytest

from car_rental_rate import process_rental_fleet, check_fleet_telematics


# ---------------------------------------------------------------- starter
def test_single_economy_rental():
    """Starter test: one confirmed economy rental (lines 5-27, 40, 51)."""
    rentals = [{
        "is_confirmed": True,
        "vehicle_type": "economy",
        "driver_age": 30,
        "days": 2,
        "trip_segments": [100],
    }]
    result = process_rental_fleet(rentals, 10.0)
    assert result["total_revenue"] == 110.0
    assert result["status"] == "STANDARD"


# ---------------------------------------------------------- input checks
def test_invalid_rental_list_raises():
    """Line 3: rentals that is not a list raises ValueError."""
    with pytest.raises(ValueError):
        process_rental_fleet("not a list", 10.0)


# ------------------------------------------------- process_rental_fleet
def test_unconfirmed_and_zero_day_rentals_give_empty_batch():
    """Lines 10, 17-18 and 50: skipped rentals leave an empty batch."""
    rentals = [
        {"is_confirmed": False, "vehicle_type": "suv", "days": 3},
        {"is_confirmed": True, "days": 0},
    ]
    result = process_rental_fleet(rentals, 5.0)
    assert result == {"total_revenue": 0.0, "status": "EMPTY_BATCH"}


def test_luxury_young_driver_long_trip_breaks():
    """Lines 21, 34-37 and 43: luxury car, driver under 21, trip > 300."""
    rentals = [{
        "is_confirmed": True,
        "vehicle_type": "luxury",
        "driver_age": 19,
        "days": 1,
        "trip_segments": [350, 50],
    }]
    result = process_rental_fleet(rentals, 0.0)
    # 120 (rate) + 250 (underage long-trip penalty) + 50 (luxury surcharge)
    assert result == {"total_revenue": 420.0, "status": "STANDARD"}


def test_suv_negative_and_long_segments():
    """Lines 23, 31-32 and 38: SUV, negative segment, long trip >= 21."""
    rentals = [{
        "is_confirmed": True,
        "vehicle_type": "suv",
        "driver_age": 40,
        "days": 2,
        "trip_segments": [-10, 400],
    }]
    result = process_rental_fleet(rentals, 10.0)
    # 70*2 + 10 + 400*0.40
    assert result == {"total_revenue": 310.0, "status": "STANDARD"}


def test_many_risk_flags_trigger_audit():
    """Line 48: more than 4 risk flags returns HIGH_RISK_AUDIT."""
    rentals = [{
        "is_confirmed": True,
        "vehicle_type": "economy",
        "driver_age": 30,
        "days": 1,
        "trip_segments": [-1, -2, -3, -4, -5],
    }]
    result = process_rental_fleet(rentals, 0.0)
    assert result == {"total_revenue": 40.0, "status": "HIGH_RISK_AUDIT"}


# ----------------------------------------------- check_fleet_telematics
def test_telematics_no_data():
    """Line 56: empty matrix returns NO_DATA."""
    assert check_fleet_telematics([]) == "NO_DATA"


def test_telematics_ground_vehicle():
    """Lines 58-64: two consecutive speeds > 100 ground the vehicle."""
    assert check_fleet_telematics([[90, 110, 120]]) == "GROUND_VEHICLE"


def test_telematics_safe():
    """Lines 66-67: streak resets and the fleet is SAFE."""
    assert check_fleet_telematics([[110, 90, 110]]) == "SAFE"

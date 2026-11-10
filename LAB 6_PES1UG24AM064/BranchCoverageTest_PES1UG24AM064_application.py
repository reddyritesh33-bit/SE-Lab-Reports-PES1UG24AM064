"""Branch coverage tests for car_rental_rate.py.

Name: Bandugula Sai Rithesh Reddy    SRN: PES1UG24AM064

Every decision in the module is driven to both its True and its False
outcome, including loop entry/exit and boundary values (days 0/1,
miles 0/300/301, age 20/21/24/25, risk flags 4/5, speed 100/101).
Run with:
    coverage run --branch -m pytest BranchCoverageTest_PES1UG24AM064_application.py
    coverage report -m
"""
import pytest

from car_rental_rate import process_rental_fleet, check_fleet_telematics


def rental(**overrides):
    """Build a confirmed, adult, 1-day economy rental with no trips."""
    data = {"is_confirmed": True, "vehicle_type": "economy",
            "driver_age": 30, "days": 1, "trip_segments": []}
    data.update(overrides)
    return data


# ------------------------------------------------ line 2: input validation
@pytest.mark.parametrize("rentals, fee", [
    ("not a list", 10.0),          # not isinstance -> True
    ({"days": 1}, 0.0),            # dict is not a list
    ([], -0.01),                   # list ok, fee < 0 -> True
])
def test_invalid_input_raises(rentals, fee):
    """Both parts of the `or` condition raise ValueError."""
    with pytest.raises(ValueError, match="Invalid rental list or admin fee"):
        process_rental_fleet(rentals, fee)


def test_valid_empty_list_zero_fee():
    """Condition False with fee == 0 boundary; loop body never runs."""
    assert process_rental_fleet([], 0.0) == {"total_revenue": 0.0,
                                             "status": "EMPTY_BATCH"}


# ------------------------------------------------ line 9: is_confirmed
def test_unconfirmed_and_missing_flag_are_skipped():
    """is_confirmed False and missing (defaults to False) are skipped."""
    rentals = [rental(is_confirmed=False), {"vehicle_type": "suv"}]
    assert process_rental_fleet(rentals, 10.0)["status"] == "EMPTY_BATCH"


def test_defaults_for_missing_fields():
    """Missing vehicle_type/age/days/segments use economy, 25, 1, []."""
    result = process_rental_fleet([{"is_confirmed": True}], 5.0)
    assert result == {"total_revenue": 45.0, "status": "STANDARD"}


# ------------------------------------------------ line 16: days <= 0
@pytest.mark.parametrize("days, expected", [(0, 0.0), (-3, 0.0), (1, 40.0)])
def test_days_boundary(days, expected):
    """days 0 and negative are flagged and skipped; 1 is billed."""
    result = process_rental_fleet([rental(days=days)], 0.0)
    assert result["total_revenue"] == expected


# ------------------------------------------------ lines 20-25: vehicle type
@pytest.mark.parametrize("vehicle, rate", [
    ("luxury", 120.0), ("suv", 70.0), ("economy", 40.0), ("compact", 40.0),
])
def test_vehicle_rates(vehicle, rate):
    """luxury / suv / else (economy and unknown types)."""
    result = process_rental_fleet([rental(vehicle_type=vehicle, days=2)], 0.0)
    assert result == {"total_revenue": rate * 2, "status": "STANDARD"}


# ------------------------------------------------ lines 29-40: trip segments
def test_segment_boundaries_adult():
    """miles -1 (flag), 0 and 300 (short rate), 301 (long rate)."""
    result = process_rental_fleet(
        [rental(trip_segments=[-1, 0, 300, 301])], 0.0)
    # 40 + 0 + 300*0.20 + 301*0.40
    assert result == {"total_revenue": 220.4, "status": "STANDARD"}


def test_age_21_long_trip_not_penalised():
    """driver_age 21 -> `< 21` False: long trip billed per mile, no break."""
    result = process_rental_fleet(
        [rental(driver_age=21, trip_segments=[400, 100])], 0.0)
    # 40 + 400*0.40 + 100*0.20 + 20 (under-25 surcharge)
    assert result["total_revenue"] == 240.0


def test_age_20_long_trip_penalty_and_break():
    """driver_age 20 -> `< 21` True: flat 250 penalty, later segments ignored."""
    result = process_rental_fleet(
        [rental(driver_age=20, trip_segments=[100, 500, 200])], 0.0)
    # 40 + 100*0.20 + 250 + 20 (under-25 surcharge); 200 never billed
    assert result["total_revenue"] == 330.0


# ------------------------------------------------ lines 42-43: age surcharge
@pytest.mark.parametrize("vehicle, age, expected", [
    ("luxury", 24, 120.0 * 2 + 50.0 * 2),   # young + luxury
    ("suv", 24, 70.0 * 2 + 20.0 * 2),       # young + not luxury
    ("luxury", 25, 120.0 * 2),              # boundary: no surcharge
])
def test_underage_surcharge(vehicle, age, expected):
    """`driver_age < 25` True/False and the luxury ternary both ways."""
    result = process_rental_fleet(
        [rental(vehicle_type=vehicle, driver_age=age, days=2)], 0.0)
    assert result["total_revenue"] == expected


# ------------------------------------------------ lines 47-51: final status
def test_exactly_four_flags_is_standard():
    """risk_flags == 4 -> `> 4` False, revenue > 0 -> STANDARD."""
    result = process_rental_fleet(
        [rental(trip_segments=[-1, -1, -1, -1])], 0.0)
    assert result == {"total_revenue": 40.0, "status": "STANDARD"}


def test_five_flags_is_high_risk_audit():
    """risk_flags == 5 (mixed sources) -> HIGH_RISK_AUDIT."""
    rentals = [rental(days=0), rental(days=-1),
               rental(trip_segments=[-5, 301, 350])]
    result = process_rental_fleet(rentals, 2.5)
    # 40 + 2.5 + 301*0.40 + 350*0.40
    assert result == {"total_revenue": 302.9, "status": "HIGH_RISK_AUDIT"}


def test_high_risk_even_with_zero_revenue():
    """Audit check comes before the empty-batch check."""
    rentals = [rental(days=0) for _ in range(5)]
    assert process_rental_fleet(rentals, 0.0) == {
        "total_revenue": 0.0, "status": "HIGH_RISK_AUDIT"}


def test_multiple_rentals_summed_and_rounded():
    """Several confirmed rentals are summed and rounded to 2 places."""
    rentals = [rental(trip_segments=[0.333]), rental(vehicle_type="suv"),
               rental(is_confirmed=False, vehicle_type="luxury")]
    result = process_rental_fleet(rentals, 1.0)
    assert result == {"total_revenue": 112.07, "status": "STANDARD"}


# ------------------------------------------------ check_fleet_telematics
@pytest.mark.parametrize("matrix", [[], None])
def test_telematics_no_data(matrix):
    """`not telematics_matrix` True for empty list and None."""
    assert check_fleet_telematics(matrix) == "NO_DATA"


@pytest.mark.parametrize("matrix, expected", [
    ([[]], "SAFE"),                          # inner loop never runs
    ([[100, 100, 100]], "SAFE"),             # 100 is not > 100
    ([[101, 99, 101]], "SAFE"),              # streak resets to 0
    ([[101]], "SAFE"),                       # streak 1, then loop ends
    ([[101, 101]], "GROUND_VEHICLE"),        # streak reaches 2
    ([[50, 60], [90, 150, 160]], "GROUND_VEHICLE"),  # second vehicle
    ([[101], [101]], "SAFE"),                # streak resets per vehicle
])
def test_telematics_streaks(matrix, expected):
    """speed > 100 True/False and streak >= 2 True/False."""
    assert check_fleet_telematics(matrix) == expected

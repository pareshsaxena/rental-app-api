from datetime import datetime, timedelta

from rental_be.controllers.compute import (
    calculate_total_rent,
)


def test_calculate_total_rent():
    # Case 0: [Booked from: -3 days | (now) | Booked to: +3 days]
    rent_0, penalty_0 = calculate_total_rent(
        product_price=500,
        minimum_rent_period=2,
        booked_from_date=datetime.utcnow()-timedelta(days=3),
        booked_to_date=datetime.utcnow()+timedelta(days=3),
    )
    expected_rent_0, expected_penalty_0 = 1500, 0
    assert expected_rent_0 == rent_0
    assert expected_penalty_0 == penalty_0

    # Case 1: [(now) | Booked from: +3 days | Booked to: +6 days]
    rent_1, penalty_1 = calculate_total_rent(
        product_price=500,
        minimum_rent_period=2,
        booked_from_date=datetime.utcnow()+timedelta(days=3),
        booked_to_date=datetime.utcnow()+timedelta(days=6),
    )
    expected_rent_1, expected_penalty_1 = 1000, 0
    assert expected_rent_1 == rent_1
    assert expected_penalty_1 == penalty_1

    # Case 2: [Booked from: -3 days | (now) | Booked to: +3 days]
    rent_2, penalty_2 = calculate_total_rent(
        product_price=500,
        minimum_rent_period=5,
        booked_from_date=datetime.utcnow()-timedelta(days=3),
        booked_to_date=datetime.utcnow()+timedelta(days=3),
    )
    expected_rent_2, expected_penalty_2 = 2500, 0
    assert expected_rent_2 == rent_2
    assert expected_penalty_2 == penalty_2

    # Case 2: [Booked from: -9 days | Booked to: -3 days | (now)]
    rent_3, penalty_3 = calculate_total_rent(
        product_price=500,
        minimum_rent_period=5,
        booked_from_date=datetime.utcnow()-timedelta(days=9),
        booked_to_date=datetime.utcnow()-timedelta(days=3),
    )
    expected_rent_3, expected_penalty_3 = 500 * 6, round(500 * 3 * 1.1)
    assert expected_rent_3 == rent_3
    assert expected_penalty_3 == round(penalty_3)

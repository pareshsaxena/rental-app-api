from datetime import datetime, timedelta
from typing import Tuple, Union

from rental_be.models.product import ProductType


def calculate_durability(
        product_type: ProductType,
        durability: int,
        rent_period: int,
        mileage: Union[int, None] = None,
    ) -> int:                                                                   # noqa E125
    """Calculate durability reduction over period

    NOTE:
    * For the plain type, durability will be decreased 1 point per every day.
    * For the meter type, durability will be decreased 2 points per every day,
        and also decreased 2 points per 10 miles.
    """
    # NOTE: It is assumed that durability of a product cannot be negative
    if product_type == ProductType.plain:
        return max(0, durability - rent_period)
    elif product_type == ProductType.meter:
        if not mileage:
            raise ValueError('`mileage` cannot be None for `meter` product type')
        return max(0, round(durability - (2 * rent_period) - 2 * (mileage / 10)))
    else:
        raise Exception('Invalid product type: %s', product_type)


def calculate_rent(
        product_price: float,
        minimum_rent_period: int,
        rent_period: int,
        discount_rate: float = 0,
    ) -> float:                                                                 # noqa E125
    """Calculate product rent over period

    NOTE:
    "Rent is calculated by multiplying the product's price by the date.
    If the product has a discount rate and minimum rental period, you
    need to consider it. Discount can be applied if the user borrows
    the product beyond the minimum rental period. If a product has no
    discount rate and only has a minimum rental period, the user can
    only borrow the product over that minimum rental period."
    """
    if discount_rate < 0 or discount_rate > 1:
        raise ValueError('Expected `discount_rate` to be in the range [0, 1.0]')

    if rent_period > minimum_rent_period:
        rent = round(product_price * (1 - discount_rate) * rent_period, 2)
    else:
        rent = round(product_price * minimum_rent_period, 2)
    return rent


def calculate_total_rent(
        product_price: float,                   # from product record
        minimum_rent_period: int,               # from product record
        booked_from_date: datetime,             # from booking ref
        booked_to_date: datetime,               # from booking ref
        discount_rate: float = 0,               # from product record; naive implementation             # noqa E501
        penalty_rate: float = 0.1               # from business logic
    ) -> Tuple[float, float]:                                                   # noqa E125
    """Calculate total rent and penalty charges, if any, over actual rental period
    """
    dt_now = datetime.utcnow()
    effective_rent_dt = min(
        max(booked_from_date+timedelta(days=minimum_rent_period), dt_now),
        booked_to_date
    )
    actual_rent_period = max(0, (effective_rent_dt - booked_from_date).days)
    rent = calculate_rent(
        product_price=product_price,
        minimum_rent_period=minimum_rent_period,
        rent_period=actual_rent_period,
        discount_rate=discount_rate
    )
    # Check if product is overdue
    overdue_period = max(0, (datetime.utcnow() - booked_to_date).days)
    effective_rent_per_day = rent / actual_rent_period
    penalty = round(effective_rent_per_day * overdue_period * (1 + penalty_rate))
    return rent, penalty

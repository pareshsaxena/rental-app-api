"""Ops business logic
"""


def is_product_returnable(
        product_code: str,
        availability: bool,
        durability: int,
    ) -> bool:                                                                  # noqa E125
    """Checks if a product is returnable

    Assumption: a product can only be returned if
        * it is not available in the inventory AND
        * its `durability` score is not zero (which implies that it is
        not undergoing repair/maintenance)
    """
    if not availability and durability > 0:
        return True
    else:
        return False


def is_product_bookable(
        product_code: str,
        availability: bool,
        durability: int,
    ) -> bool:                                                                  # noqa E125
    """Checks if a product is available for booking
    """
    # Quick and dirty check
    if availability and durability > 0:
        return True
    else:
        return False

import logging
from datetime import datetime
from typing import Optional

import mongoengine as ME
from mongoengine.queryset.visitor import Q


class ProductBooking(ME.Document):
    """Model for storing product booking information
    """
    # NOTE: For a realistic app you would want to capture user ID
    # user_id: str
    product_code = ME.StringField()
    timestamp = ME.DateTimeField(default=datetime.utcnow)
    from_date = ME.DateTimeField()
    to_date = ME.DateTimeField()

    meta = {
        'indexes': [
            'timestamp',
            'from_date',
            'to_date',
        ]
    }


class ProductReturn(ME.Document):
    """Model for storing product return information
    """
    # NOTE: For a realistic app you would want to capture user ID
    # user_id: str
    booking_id = ME.StringField(unique=True)
    product_code = ME.StringField()
    timestamp = ME.DateTimeField(default=datetime.utcnow)
    total_fee = ME.FloatField()

    meta = {
        'indexes': [
            'timestamp',
            'total_fee',
        ]
    }


# -----------------------------------------------------------------------------


# CRUD Operations =============================================================

# NOTE: As project complexity increases DB query functions should be
# moved in to a separate `crud` package which implements all
# relavant CRUD operations on resources available through the API

def create_booking(
        product_code,
        from_date,
        to_date,
        timestamp=datetime.utcnow()
    ) -> str:                                                                   # noqa E125
    booking_doc = ProductBooking(
        product_code=product_code,
        from_date=from_date,
        to_date=to_date,
        timestamp=timestamp
    ).save()
    return f'{booking_doc.pk}'


def get_booking(booking_id) -> Optional[ProductBooking]:
    return ProductBooking.objects(pk=booking_id).first()


def is_product_booked(
        product_code: str,
        from_date: datetime,
        to_date: datetime,
    ) -> bool:                                                                  # noqa E125
    """
    """
    # BR0: Booking request start date
    # BR1: Booking request end date
    # B0: Existing booking start date
    # B1: Existing booking end date
    # Find an overlapping existing booking
    bookings = ProductBooking.objects(
        # Case 0: [B0----[BR0----(B1)]----BR1]
        (Q(to_date__lte=to_date) & Q(to_date__gte=from_date)) |
        # Case 1: [BR0----[(B0)----BR1]----B1]
        (Q(from_date__lte=to_date) & Q(from_date__gte=from_date)) |
        # Case 2: [(B0)----[BR0----BR1]----(B1)]
        (Q(from_date__lte=from_date) & Q(to_date__gte=to_date))
    ).all()
    if bookings:
        booking_ids = [str(x.pk) for x in bookings]
        return_docs = ProductReturn.objects(booking_id__in=booking_ids).all()
        if len(bookings) > len(return_docs):        
            return True
        else:
            return False
    else:
        return False


def create_return(
        booking_id: str,
        product_code: str,
        total_fee: float,
        timestamp: datetime = datetime.utcnow()
    ) -> str:                                                                   # noqa E125
    return_doc = ProductReturn(
        booking_id=booking_id,
        product_code=product_code,
        total_fee=total_fee,
        timestamp=timestamp
    ).save()
    return f'{return_doc.pk}'


def get_return(booking_id) -> Optional[ProductReturn]:
    return ProductReturn.objects(booking_id=booking_id).first()

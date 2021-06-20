from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator


# Request Schema ==========================================

class ProductBookingRequest(BaseModel):
    """Schema for booking a product and estimating fees

    NOTE: "The request body would be the product's basic information,
    and rental period."
    """
    code: str
    from_date: datetime
    to_date: datetime

    @validator('to_date')
    def to_date_validator(cls, v, values):
        # NOTE: Max rental period can be defined here and validated against
        # Validate date range: `to_date` > `from_date`
        if v < values.get('from_date'):
            raise ValueError('Expected `to_date` > `from_date`')
        else:
            return v


class ProductReturnRequest(BaseModel):
    """Schema for accepting product returns

    NOTE: "The request body would be the product's basic information,
    rental period, mileage used if it has mileage and the alert
    whether the product is needed to repair."
    """
    booking_id: str
    code: str
    mileage: Optional[int]

    @validator('mileage')
    def mileage_validator(cls, v):
        if v and v < 1:
            raise ValueError('Expected `mileage` to be greater than zero')
        else:
            return v

# ---------------------------------------------------------


# Response Schema =========================================

class FeeEstimateResponse(BaseModel):
    """Schema for estimated fee endpoint

    NOTE: "Price value is per day."
    """
    code: str
    rent_period: int
    rental_fee: float


class FeeTotalResponse(BaseModel):
    """Schema for total fee endpoint
    """
    code: str
    rental_fee: float
    overdue_period: int
    late_charges: float
    needing_repair: bool


class ProductBookingResponse(FeeEstimateResponse):
    """Schema for product booking endpoint
    """
    booking_id: str


class ProductReturnResponse(FeeTotalResponse):
    """Schema for product return endpoint
    """
    return_id: str

# ---------------------------------------------------------

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, validator


# Enums ===================================================

class ProductSortEnum(str, Enum):
    name = 'name'
    code = 'code'
    durability = 'durability'
    mileage = 'mileage'

# ---------------------------------------------------------


# Entity Schema ===========================================

class ProductSchema(BaseModel):
    """Schema for product
    """
    code: str
    name: str
    type: str
    availability: bool
    needing_repair: bool
    durability: int
    max_durability: int
    mileage: Optional[int]
    price: float
    discount_rate: float = 0.0
    minimum_rent_period: int

# ---------------------------------------------------------


# Request Schema ==========================================

class ProductRequest(ProductSchema):
    """Schema for the product endpoint
    """
    # NOTE: Except `mileage` and `discount_rate`, all are
    # required to create a record
    pass


class ProductInventoryRequest(BaseModel):
    """Schema for the product inventory endpoint
    """
    search_term: str = ''
    sort_by: ProductSortEnum = ProductSortEnum.name
    ascending: bool = True
    page: int = 1
    items_per: int = 15

    @validator('page')
    def page_validator(cls, v):
        if v < 1:
            return 1
        else:
            return v

    @validator('items_per')
    def items_per_validator(cls, v):
        if v < 1:
            return 15
        else:
            return v

# ---------------------------------------------------------


# Response Schema =========================================

class ProductResponse(ProductSchema):
    """Schema for product
    """
    pass


class ProductView(BaseModel):
    """Schema for product view
    """
    code: str
    name: str
    availability: bool
    needing_repair: bool
    durability: int
    mileage: Optional[int]


class ProductInventorytResponse(BaseModel):
    """Schema for product list endpoint
    """
    current_page: int
    total_pages: int
    total_products: int
    product_views: List[Optional[ProductView]]

# ---------------------------------------------------------

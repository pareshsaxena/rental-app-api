from typing import Dict, List, Optional

from pydantic import BaseModel, validator


class ProductInventory(BaseModel):
    """Internal schema for tracking product inventory
    """
    product_count: int
    products: List[Optional[Dict]]

    @validator('product_count')
    def product_count_positive(cls, v):
        if v < 0:
            raise ValueError('Expected positive `product_count`')
        else:
            return v

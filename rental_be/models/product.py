from enum import Enum

import mongoengine as ME
from mongoengine.queryset.visitor import Q

from rental_be.schema.internal import ProductInventory


# Enum Classes ================================================================

class ProductType(str, Enum):
    plain = 'plain'
    meter = 'meter'

# -----------------------------------------------------------------------------


# Documents ===================================================================

class Product(ME.Document):
    code = ME.StringField(unique=True)
    name = ME.StringField(null=False)
    type = ME.EnumField(ProductType)
    availability = ME.BooleanField()
    needing_repair = ME.BooleanField()
    durability = ME.IntField()
    max_durability = ME.IntField()
    mileage = ME.IntField()
    price = ME.FloatField()
    discount_rate = ME.FloatField(default=0)
    minimum_rent_period = ME.IntField()

    meta = {
        'indexes': [
            'code',
            'name',
            'availability',
            'needing_repair',
            'durability',
            'max_durability',
            'mileage'
        ]
    }

# -----------------------------------------------------------------------------


# CRUD Operations =============================================================

# NOTE: As project complexity increases DB query functions should be
# moved in to a separate `crud` package which implements all
# relavant CRUD operations on resources available through the API


def get_product(code: str) -> Product:
    """Get a product using product code
    """
    return Product.objects(code=code).first()


def get_product_inventory(
        search_term: str,
        prefix: str,
        sort_by: str,
        item_from: int,
        item_to: int
    ) -> ProductInventory:                                                      # noqa E125
    """
    """
    product_queryset = Product.objects(
        # Case insensitive search on product `name` and `code`
        Q(name__icontains=search_term) |
        Q(code__iexact=search_term)
    ).order_by(prefix + sort_by)
    product_count = product_queryset.count()
    products = product_queryset[item_from:item_to].all()
    return ProductInventory(
        product_count=product_count,
        products=[dict(x.to_mongo()) for x in products]
    )

# -----------------------------------------------------------------------------

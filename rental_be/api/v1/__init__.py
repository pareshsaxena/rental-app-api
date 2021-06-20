"""API blueprint module
"""
from flask import Blueprint
from flask_restful import Api

from rental_be.api.v1.data import SampleData, DataSummary
from rental_be.api.v1.ops import (
    FeeEstimate,
    FeeTotal,
    ProductBooking,
    ProductReturn,
)
from rental_be.api.v1.product import (
    ProductCreate,
    ProductRead,
    ProductInventory,
)


rental_bp = Blueprint(name='api_v1', import_name=__name__, url_prefix='/api/v1')
rental_bp_api = Api(rental_bp)

# Product
rental_bp_api.add_resource(ProductCreate, '/product')
rental_bp_api.add_resource(ProductRead, '/product/<product_code>')
rental_bp_api.add_resource(ProductInventory, '/inventory')

# Product Operations
rental_bp_api.add_resource(ProductBooking, '/product-ops/booking')
rental_bp_api.add_resource(ProductReturn, '/product-ops/return')
rental_bp_api.add_resource(FeeEstimate, '/product-ops/estimate-fee')
rental_bp_api.add_resource(FeeTotal, '/product-ops/total-fee')

# Sample Data
rental_bp_api.add_resource(SampleData, '/data')
rental_bp_api.add_resource(DataSummary, '/data/summary')

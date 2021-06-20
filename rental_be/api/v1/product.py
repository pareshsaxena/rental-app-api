import logging
from math import ceil

from flask_restful import Resource, request

from rental_be.models.product import (
    get_product,
    get_product_inventory,
    Product,
)
from rental_be.schema.v1.inventory import (
    ProductInventoryRequest,
    ProductInventorytResponse,
    ProductRequest,
    ProductResponse,
    ProductView,
)


class ProductRead(Resource):
    def get(self, product_code: str):
        """Read a product record using the product code
        """
        try:
            product = get_product(code=product_code)
            if product:
                response = ProductResponse(**product.to_mongo())
                return response.dict(), 200
            else:
                return {}, 404
        except Exception as excp:
            logging.exception(excp)
            return {'error': str(excp)}, 400


class ProductCreate(Resource):
    def post(self):
        """Create a product record
        """
        try:
            product_data = request.get_json()
            product_req = ProductRequest(**product_data).dict()
            logging.warning(f'{type(product_req)}')
        except Exception as excp:
            logging.exception(excp)
            return {'error': str(excp)}, 400
        try:
            product = Product(**product_req)
            product.save()
            return {'code': product.code}, 200
        except Exception as excp:
            logging.exception(excp)
            return {'error': str(excp)}, 500


class ProductInventory(Resource):
    """Product inventory as a resource
    """
    def get(self):
        """GET a list of products in the inventory
        """
        try:
            # Validate query parameters
            inventory_params = ProductInventoryRequest(
                # Filter query parameters
                search_term=request.args.get('search_term', ''),
                # Sort query parameters
                sort_by=request.args.get('sort_by', 'name'),
                ascending=request.args.get('ascending', True),
                # Pagination query parameters
                page=request.args.get('page', 1),
                items_per=request.args.get('items_per', 0),
            )
        except Exception as excp:
            logging.exception(excp)
            return {'error': str(excp)}, 400
        try:
            item_to = inventory_params.page * inventory_params.items_per
            item_from = item_to - inventory_params.items_per
            if inventory_params.ascending:
                prefix = '+'
            else:
                prefix = '-'
            inventory = get_product_inventory(
                search_term=inventory_params.search_term,
                prefix=prefix,
                sort_by=inventory_params.sort_by,
                item_from=item_from,
                item_to=item_to
            )
            response = ProductInventorytResponse(
                current_page=inventory_params.page,
                total_pages=ceil(inventory.product_count / inventory_params.items_per),
                total_products=inventory.product_count,
                product_views=[ProductView(**x) for x in inventory.products]
            )
            return response.dict(), 200
        except Exception as excp:
            logging.exception(excp)
            return {'error': str(excp)}, 500

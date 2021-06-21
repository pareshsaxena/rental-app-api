"""Product ops resources
"""
import logging
from datetime import datetime

from flask_restful import Resource, request

from rental_be.controllers.compute import (
    calculate_durability,
    calculate_rent,
    calculate_total_rent,
)
from rental_be.models.ops import (
    create_booking,
    create_return,
    get_booking,
    get_return,
    is_product_booked
)
from rental_be.models.product import get_product
from rental_be.schema.v1.product_ops import (
    FeeEstimateResponse,
    FeeTotalResponse,
    ProductBookingRequest,
    ProductBookingResponse,
    ProductReturnRequest,
    ProductReturnResponse,
)


class FeeEstimate(Resource):
    def get(self):
        """Read rent fee estimate
        """
        try:
            booking_info = request.get_json()
            booking_req = ProductBookingRequest(**booking_info)
        except Exception as excp:
            logging.exception(excp)
            return {'error': str(excp)}, 400
        try:
            # --- Business logic ---
            # 0. Rental fee can only be calculated for products in the inventory
            product = get_product(code=booking_req.code)
            if not product:
                return {'error': 'product not found'}, 404
            # 1. Calculate rental period in days
            rent_period = (booking_req.to_date - booking_req.from_date).days
            # 2. Caclulate rental fee
            rent = calculate_rent(
                product_price=product.price,
                minimum_rent_period=product.minimum_rent_period,
                rent_period=rent_period,
                discount_rate=product.discount_rate
            )
            # Construct response
            response = FeeEstimateResponse(
                code=booking_req.code,
                rent_period=rent_period,
                rental_fee=rent
            )
            return response.dict(), 200
        except Exception as excp:
            logging.exception(excp)
            return {'error': str(excp)}, 500


class FeeTotal(Resource):
    def get(self):
        """Final fee amount chargeable
        """
        try:
            return_info = request.get_json()
            return_req = ProductReturnRequest(**return_info)
        except Exception as excp:
            logging.exception(excp)
            return {'error': str(excp)}, 400
        try:
            # --- Business logic ---
            # 0. Total fee can only be calculated for products in the inventory
            product = get_product(code=return_req.code)
            if not product:
                return {'error': 'product not found'}, 404
            # 1. Total fee can only be calculated for products
            # with a valid booking reference
            booking = get_booking(booking_id=return_req.booking_id)
            if not booking:
                return {'error': 'booking does not exist'}, 400
            # 2. Calculate new durability score
            new_durability = calculate_durability(
                product_type=product.type,
                durability=product.durability,
                rent_period=(datetime.utcnow()-booking.from_date).days,
                mileage=return_req.mileage
            )
            # 3. Calculate total rental fee
            rental_fee, penalty = calculate_total_rent(
                product_price=product.price,
                minimum_rent_period=product.minimum_rent_period,
                booked_from_date=booking.from_date,
                booked_to_date=booking.to_date,
            )
            # Construct response
            response = FeeTotalResponse(
                code=product.code,
                rental_fee=rental_fee,
                overdue_period=max(0, (datetime.utcnow() - booking.to_date).days),
                late_charges=penalty,
                needing_repair=False if new_durability > 0 else True
            )
            return response.dict(), 200
        except Exception as excp:
            logging.exception(excp)
            return {'error': str(excp)}, 500


class ProductBooking(Resource):
    def post(self):
        """Create a product booking record
        """
        try:
            booking_info = request.get_json()
            booking_req = ProductBookingRequest(**booking_info)
        except Exception as excp:
            logging.exception(excp)
            return {'error': str(excp)}, 400
        try:
            # --- Business logic ---
            # 0. Only products in the inventory can be booked
            product = get_product(code=booking_req.code)
            if not product:
                return {'error': 'product not found'}, 404
            # 1. Only available products in the inventory can be booked
            if not product.availability:
                return {'error': 'product is not available for booking'}, 400
            # 2. Only products that don't have an overlapping booking can be booked
            if is_product_booked(product_code=product.code,
                                 from_date=booking_req.from_date,
                                 to_date=booking_req.to_date):
                return {'error': 'product is already booked in the requested period'}, 403          # noqa E501
            # 3. Calculate rental period
            rent_period = (booking_req.to_date-booking_req.from_date).days
            # 4. Calculate rental fee estimate
            rent = calculate_rent(
                product_price=product.price,
                minimum_rent_period=product.minimum_rent_period,
                rent_period=rent_period,
                discount_rate=product.discount_rate
            )
            # 5. Create product booking
            booking_id = create_booking(
                product_code=product.code,
                from_date=booking_req.from_date,
                to_date=booking_req.to_date
            )
            product.save()
            # Construct response
            response = ProductBookingResponse(
                booking_id=booking_id,
                code=product.code,
                rent_period=rent_period,
                rental_fee=rent
            )
            return response.dict(), 200
        except Exception as excp:
            logging.exception(excp)
            return {'error': str(excp)}, 500


class ProductReturn(Resource):
    def post(self):
        """Create a product return record
        """
        try:
            return_info = request.get_json()
            return_req = ProductReturnRequest(**return_info)
        except Exception as excp:
            logging.exception(excp)
            return {'error': str(excp)}, 400
        try:
            # --- Business logic ---
            # 0. Only products in the inventory can be returned
            product = get_product(code=return_req.code)
            if not product:
                return {'error': 'product not found'}, 404

            # 1. Products can only be returned if they have been booked earlier
            if get_return(booking_id=return_req.booking_id):
                return {'error': 'return already processed'}, 400

            # 2. Product mileage cannot be lower than what it
            # was when the product was booked
            if product.mileage and return_req.mileage:
                if return_req.mileage < product.mileage:
                    return {'error': 'return mileage cannot be lower than booking mileage'}, 400        # noqa E401

            # 3. Only products with a valid booking ID can be returned
            booking = get_booking(booking_id=return_req.booking_id)
            if not booking:
                return {'error': 'booking does not exist'}, 400
            # 4. Calculate new durability score
            new_durability = calculate_durability(
                product_type=product.type,
                durability=product.durability,
                rent_period=(datetime.utcnow()-booking.from_date).days,
                mileage=return_req.mileage
            )
            # 5. Calculate rent and penalty charges, if any
            rental_fee, penalty = calculate_total_rent(
                product_price=product.price,
                minimum_rent_period=product.minimum_rent_period,
                booked_from_date=booking.from_date,
                booked_to_date=booking.to_date,
            )
            product.durability = max(0, new_durability)
            if product.durability == 0:
                # Product needs repair/maintenance
                product.availability = False
            else:
                product.availability = True
            product.mileage = return_req.mileage
            product.save()
            # 6. Create a return record
            return_id = create_return(
                booking_id=return_req.booking_id,
                product_code=product.code,
                total_fee=rental_fee+penalty,
            )
            # Construct response
            response = ProductReturnResponse(
                code=product.code,
                return_id=return_id,
                rental_fee=rental_fee,
                overdue_period=max(0, (datetime.utcnow() - booking.to_date).days),
                late_charges=penalty,
                needing_repair=False if product.durability > 0 else True
            )
            return response.dict(), 200
        except Exception as excp:
            logging.exception(excp)
            return {'error': str(excp)}, 500

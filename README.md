# Rental Application API

## TL;DR

This is a naive implementation of a backend Flask API for a product rental application. It uses MongoDB (or any database that is compatible with the MongoDB Wire Protocol like Azure CosmosDB) as the persistent data store.

#### Assumptions

* This product rental app operates on a simple check-in, check-out model. Any number of bookings can be made for a product as long as they don't overlap in time.
* Products are uniquely identified by their `code`.
* Every successful product booking generates a `booking_id`.
* A product can be booked if it's available in the inventory and doesn't need repair/maintenance.
* A product needs repair/maintenance when its `durability` score is zero or less.
* A product can only be returned using a valid `booking_id`. 
* Once a product has been returned, it can't be returned again. Duh!
* Rental fee is charged for the actual borrowed period irrespective of the booking period (subject to a minimum rental fee, more on this below). A product is assumed to be borrowed at the start of the booking period.

***Since the product rental business operates on wafer-thin margins, this app charges the customer a minimum product rental fee even on cancellations!***

* Products returned past their due date incur additional late charges of 10% of per day rental fee for the overdue period.

## Sample Product Record

``` json
{
    "code":"p6",
    "name":"Copper Blade 8 inch",
    "type":"plain",
    "availability":true,
    "needing_repair":false,
    "durability":1500,
    "max_durability":2000,
    "mileage":null,
    "price": 300,
    "minimum_rent_period":2
}
```

## Core API Endpoints

#### .../inventory

Get a list of products in the inventory. This endpoint supports:

* **filtering** on product name and code
* **pagination** with configurable products per page
* **sorting** based on product name, code, durability and mileage

Supports HTTP operations: `GET`

Sample request:

``` bash
$ curl -X GET localhost:5000/api/v1/inventory?items_per=2&page=5&sort_by=mileage&ascending=false
```

Sample response:

``` JSON
{
    "current_page": 5,
    "total_pages": 9,
    "total_products": 17,
    "product_views": [
        {
            "code": "p9",
            "name": "Beam Clamp",
            "availability": false,
            "needing_repair": false,
            "durability": 5000,
            "mileage": null
        },
        {
            "code": "p8",
            "name": "Beam Clamp",
            "availability": true,
            "needing_repair": false,
            "durability": 10000,
            "mileage": null
        }
    ]
}
```

#### .../product-ops/estimate-fee

Get the rental fee estimate for a product using product code and rental period.

Supports HTTP operations: `GET`

Sample request:

``` bash
$ curl -X GET --header "Content-Type: application/json" -d "{\"code\": \"m5\", \"from_date\": \"2021-07-18T14:00\", \"to_date\": \"2021-07-22T14:00\"}" localhost:5000/api/v1/product-ops/estimate-fee
```

Sample response:

``` JSON
{
    "code": "m5",
    "rent_period": 4,
    "rental_fee": 2000.0
}
```

#### .../product-ops/booking

Submit a request to book a product using product code and rental period. Multiple bookings can be made for a product as long as they don't overlap. Once a product is booked and subsequently returned, the booking slot is freed and another booking can be made for that slot. This enables booking cancellations.

Supported HTTP operations: `POST`

Sample request:

``` bash
$ curl -X POST --header "Content-Type: application/json" -d "{\"code\": \"m5\", \"from_date\": \"2021-06-18T14:00\", \"to_date\": \"2021-06-22T14:00\"}" localhost:5000/api/v1/product-ops/booking
```

Sample response:

``` JSON
{
    "code": "m5",
    "rent_period": 4,
    "rental_fee": 2000.0,
    "booking_id": "60cfaab4d7697f5b9e05ea18"
}
```
#### .../product-ops/total-fee

Get the total chargeable fee amount for a rented product. This endpoint also provides information if the product needs repairs.

Supports HTTP operations: `GET`

Sample request:

``` bash
$ curl -X GET --header "Content-Type: application/json" -d "{\"booking_id\": \"60cfdf86efdbdf72d67b2992\", \"code\": \"m5\", \"mileage\": \"880\"}" localhost:5000/api/v1/product-ops/return
```

Sample response:

``` JSON
{
    "code": "m5",
    "rental_fee": 6000.0,
    "overdue_period": 0,
    "late_charges": 0.0,
    "needing_repair": false
}
```

#### .../product-ops/return

Submit a request to return a product using booking ID, product code and mileage used, if any. This endpoint validates the product return request against the booking ID. A product cannot be returned more than once against a booking ID.

Supports HTTP operations: `POST`

Sample request:

``` bash
$ curl -X POST --header "Content-Type: application/json" -d "{\"booking_id\": \"60cfdf86efdbdf72d67b2992\", \"code\": \"m5\", \"mileage\": \"880\"}" localhost:5000/api/v1/product-ops/return
```

Sample response:

``` JSON
{
    "code": "m5",
    "rental_fee": 6000.0,
    "overdue_period": 0,
    "late_charges": 0.0,
    "needing_repair": true,
    "return_id": "60cfdd038fd17fe2e605825d"
}
```

## Additional API Endpoints

#### .../product/:id

Get a product from the inventory.

Supports HTTP operations: `GET`

Sample request:

``` bash
$ curl -X GET localhost:5000/api/v1/product/m5
```

Sample response:

``` JSON
{
    "code": "m5",
    "name": "Boom lift 20",
    "type": "meter",
    "availability": false,
    "needing_repair": false,
    "durability": 0,
    "max_durability": 8000,
    "mileage": 20000,
    "price": 500.0,
    "discount_rate": 0.0,
    "minimum_rent_period": 1
}
```

#### .../product

Create a new product.

Supports HTTP operations: `POST`

Sample request:

``` bash
$ curl -X POST --header "Content-Type: application/json" -d "{\"code\": \"qw5\",\"name\": \"Boom lift 20\",\"type\": \"meter\",\"availability\": true,\"needing_repair\": false,\"durability\": 1200,\"max_durability\": 8000,\"mileage\": 600,\"price\": 500.0,\"discount_rate\": 0.0,\"minimum_rent_period\": 1\r\n}" localhost:5000/api/v1/product
```

Sample response:

``` JSON
{
    "code": "qw5"
}
```

## *Nice-to-have* API Endpoints

#### .../product/:id/history

From an anlytics standpoint, it would be great to have an endpoint which shows all the past and future bookings for a product as well as all the returns data.

* *What is the average borrow period for product **X**?*
* *What time of the year is product **X** most in demand?*
* *Can we carry out predictive maintenance for products in the inventory?*

## Test Data API Endpoints

These API endpoints are great for playing around with the app: `delete`, `load`, `repeat`. 😎

#### .../data

Create new products from sample data. This endpoint also `deletes` all product data in the DB.

Supports HTTP operations: `POST`, `DELETE`

``` bash
$ curl -X POST localhost:5000/api/v1/data
```

Sample response:

``` JSON
{
    "p1": "success",
    "p2": "success",
    "p3": "success",
    "p4": "success",
    "p5": "success",
    "p6": "success",
    "p7": "success",
    "p8": "success",
    "p9": "success",
    "m1": "success",
    "m2": "success",
    "m3": "success",
    "m4": "success",
    "m5": "success",
    "m6": "success",
    "m7": "success",
    "m8": "success"
}
```

To delete all data (documents) in the DB...

Sample request:

``` bash
$ curl -X DELETE localhost:5000/api/v1/data
```

Sample response:

``` JSON
{
    "product_delete_count": 17,
    "booking_delete_count": 5,
    "return_delete_count": 3
}
```

#### .../data/summary

Summary view (document counts) of the DB.

Supports HTTP operations: `GET`

Sample request:

``` bash
$ curl -X GET localhost:5000/api/v1/data/summary
```

Sample response:

``` JSON
{
    "product_count": 17,
    "booking_count": 4,
    "return_count": 4
}
```

## Code Layout

``` bash
$ tree rental_be/
rental_be/
├── __init__.py
├── api                                 <<- API endpoints (`V` of MVC)
│   ├── __init__.py
│   └── v1
│       ├── __init__.py                     <<- Flask blueprints by API versions
│       ├── data.py
│       ├── ops.py
│       └── product.py
├── auth                                <<- For all auth related stuff. Not implemented.
│   └── __init__.py
├── config                              <<- Flask app configuration (almost production ready!)
│   ├── __init__.py
│   └── settings.py
├── controllers                         <<- Business logic (`C` of MVC)
│   ├── __init__.py
│   ├── compute.py
│   └── ops.py
├── db                                  <<- DB Engine (connections, etc.)
│   ├── __init__.py
│   ├── mongo.py                            << MongoEngine ODM as a Flask extension
│   └── mongo_connection.py
├── models                              <<- DB document models (`M` of MVC)
│   ├── __init__.py
│   ├── ops.py
│   └── product.py
└── schema                              <<- Schema defintions
    ├── __init__.py
    ├── internal.py
    └── v1                                  <<- API schemas
        ├── __init__.py
        ├── inventory.py
        └── product_ops.py
```

## Local Dev Environment 

### (*How do you run this thing??*)

#### 1. Start MongoDB in a Docker container

``` bash
$ docker run -it -v data:/data/db -p 27017:27017 --name mongodb -d mongo
```

#### 2. `git clone` this repo to your local

``` bash
$ git clone git@github.com:pareshsaxena/rental-app-api.git
```

#### 3. Change directory to

``` bash
$ cd rental-app-api
```

#### 4. Create and activate a virtual environment in the folder

``` bash
$ virtualenv .venv && source .venv/bin/activate
```

#### 5. Install Python packages using `pip`

``` bash
$ pip install -r requirements.txt
```

#### 6. Run the Flask development server

``` bash
$ python run.py
WARNING:root:No secret file found!
 * Serving Flask app 'rental_be' (lazy loading)
 * Environment: development
 * Debug mode: on
WARNING:werkzeug: * Running on all addresses.
   WARNING: This is a development server. Do not use it in a production deployment.
INFO:werkzeug: * Running on http://192.168.2.13:5000/ (Press CTRL+C to quit)
INFO:werkzeug: * Restarting with stat
...
```

You should now have a Flask dev server running on port 5000 of your machine (localhost).

### Running Tests

``` bash
$ pytest -Wignore -vv tests/
```

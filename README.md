# E-Shopper Django Project

Welcome to the **E-Shopper** e-commerce platform repository. This README provides a step-by-step guide to setting up the project, configuring a MySQL database, and running the project locally.

## Prerequisites

Ensure the following software is installed:

- **Python 3.9 or higher**
- **MySQL**
- **Django**

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/VishalNeosoft24/ecommerce.git
cd ecommerce
```

### 2. Set Up a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate

```

### 3. Install Project Dependencies

```
pip install -r requirements.txt
```

### 4. Create a MySQL Database

```
mysql -u root -p
```

In the MySQL shell, run:

```
CREATE DATABASE Database_name;
```

### 5. Create a Database User and Grant Privileges

```
CREATE USER 'myuser'@'localhost' IDENTIFIED BY 'mypassword';
GRANT ALL PRIVILEGES ON Database_name.* TO 'myuser'@'localhost';
FLUSH PRIVILEGES;
```

If the user already exists, grant privileges directly:

```
GRANT ALL PRIVILEGES ON new_schema.* TO 'myuser'@'localhost';
FLUSH PRIVILEGES;
```

### 6. Configure Django Settings

Edit the DATABASES configuration in settings.py to match the database setup:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'Database_name',
        'USER': 'myuser',
        'PASSWORD': 'mypassword1',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 7. Apply Migrations

Set up the database schema by applying migrations:

```
python manage.py migrate
```

### 8. Create a Superuser

Create an admin account to access the Django admin panel:

```
python manage.py createsuperuser
```

### 9. Run the Development Server

Start the development server:

```
python manage.py runserver

```

# Django Project Fixtures Guide

This section provides instructions on how to create, load, and manage fixtures in your Django project. Fixtures are useful for loading initial data into your database, providing data for testing, or migrating data between environments.

## Table of Contents

1. [Introduction](#introduction)
2. [Creating a Fixture](#creating-a-fixture)
3. [Loading a Fixture](#loading-a-fixture)
4. [Example Fixture File](#example-fixture-file)
5. [Setting Up and Running Background Services](#setting-up-and-running-background-services)

## Introduction

Fixtures in Django are serialized data representations that can be used to populate your database. They are usually stored in JSON, XML, or YAML format.

## Creating a Fixture

To create a fixture from existing data in the database, use the `dumpdata` management command:

```
python manage.py dumpdata <app_name>.<ModelName> --indent 4 > <fixture_name>.json

python manage.py dumpdata ecommerce.Product --indent 4 > initial_data.json
```

## Example to create a fixture for a individual model of product_management app

```
python manage.py dumpdata product_management.Category --indent 4 > product_management/fixtures/category_data.json
python manage.py dumpdata product_management.Product --indent 4 > product_management/fixtures/product_data.json
python manage.py dumpdata product_management.ProductImage --indent 4 > product_management/fixtures/product_image_data.json
python manage.py dumpdata product_management.ProductAttribute --indent 4 > product_management/fixtures/product_attribute_data.json
python manage.py dumpdata product_management.ProductAttributeValue --indent 4 > product_management/fixtures/product_attribute_value_data.json

```

## Example to create a fixture for a individual model of order_management app

```
python manage.py dumpdata order_management.PaymentGateway --indent 4 > order_management/fixtures/payment_gateway_data.json
python manage.py dumpdata order_management.UserOrder --indent 4 > order_management/fixtures/user_order_data.json
python manage.py dumpdata order_management.OrderDetail --indent 4 > order_management/fixtures/order_detail_data.json
python manage.py dumpdata order_management.UserWishList --indent 4 > order_management/fixtures/user_wishlist_data.json
python manage.py dumpdata order_management.PaymentLogs --indent 4 > order_management/fixtures/payment_logs_data.json

```

## Example to create a fixture for a individual model of user_management app

```
python manage.py dumpdata user_management.Category --indent 4 > user_management/fixtures/user_data.json

```

## Loading a Fixture

```
python manage.py loaddata <fixture_name>.json

python manage.py loaddata initial_data.json
```

## Example Fixture File

[
{
"model": "ecommerce.product",
"pk": 1,
"fields": {
"name": "Laptop",
"description": "A high-end laptop with 16GB RAM and 512GB SSD.",
"price": 1200.00,
"stock": 50,
"category": 1
}
},
{
"model": "ecommerce.product",
"pk": 2,
"fields": {
"name": "Smartphone",
"description": "A smartphone with 8GB RAM and 128GB storage.",
"price": 700.00,
"stock": 150,
"category": 2
}
}
]

## Setting Up and Running Background Services

This project requires three background services to function correctly:

1. Redis server – acts as a message broker for Celery.
2. Celery Worker – processes background tasks.
3. Celery Beat – schedules periodic tasks.

To start each of these services, open separate terminal windows and use the following commands.

### 1. Start Redis Server

In the first terminal, run:

```
redis-server
```

### 2. Start Celery Worker

In the second terminal, run:

```
celery -A ecommerce worker --loglevel=info
```

### 3. Start Celery Beat Scheduler

In the third terminal, run:

```
celery -A ecommerce beat --loglevel=info

```

This README section provides clear, step-by-step instructions, making it easy for other developers to set up and run these background services.

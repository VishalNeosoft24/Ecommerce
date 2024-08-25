from .models import User
from product_management.models import Category, Product


def create_categories():
    # Fetch or create the admin user who will be the 'created_by' and 'updated_by'
    admin_user, _ = User.objects.get_or_create(
        username="admin",
        defaults={"email": "admin@example.com", "password": "adminpass"},
    )

    categories = [
        {
            "name": "Electronics",
            "description": "All kinds of electronics",
            "parent": None,
        },
        {
            "name": "Mobile Phones",
            "description": "Smartphones and accessories",
            "parent": "Electronics",
        },
        {
            "name": "Android Phones",
            "description": "Phones running Android OS",
            "parent": "Mobile Phones",
        },
        {
            "name": "Android Accessories",
            "description": "Accessories for Android Phones",
            "parent": "Android Phones",
        },
        {
            "name": "Laptop Accessories",
            "description": "Accessories for laptops",
            "parent": "Laptops",
        },
        {
            "name": "Home Appliances",
            "description": "Appliances for home",
            "parent": None,
        },
        {
            "name": "Kitchen Appliances",
            "description": "Appliances for kitchen",
            "parent": "Home Appliances",
        },
        {
            "name": "Microwaves",
            "description": "Microwave ovens",
            "parent": "Kitchen Appliances",
        },
        {
            "name": "Convection Microwaves",
            "description": "Convection microwave ovens",
            "parent": "Microwaves",
        },
        {"name": "Clothing", "description": "All types of clothing", "parent": None},
        {"name": "Men's Clothing", "description": "Men's wear", "parent": "Clothing"},
        {
            "name": "Men's Suits",
            "description": "Suits for men",
            "parent": "Men's Clothing",
        },
        {
            "name": "Formal Suits",
            "description": "Formal suits for men",
            "parent": "Men's Suits",
        },
        {
            "name": "Women's Clothing",
            "description": "Women's wear",
            "parent": "Clothing",
        },
        {
            "name": "Women's Dresses",
            "description": "Dresses for women",
            "parent": "Women's Clothing",
        },
        {
            "name": "Evening Gowns",
            "description": "Evening gowns and party wear",
            "parent": "Women's Dresses",
        },
        {"name": "Books", "description": "Books of all genres", "parent": None},
        {"name": "Science Fiction", "description": "Sci-Fi books", "parent": "Books"},
        {
            "name": "Cyberpunk",
            "description": "Cyberpunk novels",
            "parent": "Science Fiction",
        },
        {
            "name": "Classic Cyberpunk",
            "description": "Classic cyberpunk books",
            "parent": "Cyberpunk",
        },
        {
            "name": "Sports Equipment",
            "description": "Sports gear and equipment",
            "parent": None,
        },
        {
            "name": "Football Gear",
            "description": "Football equipment and gear",
            "parent": "Sports Equipment",
        },
        {
            "name": "Outdoor Equipment",
            "description": "Equipment for outdoor sports",
            "parent": "Sports Equipment",
        },
        {
            "name": "Camping Gear",
            "description": "Camping essentials",
            "parent": "Outdoor Equipment",
        },
        {
            "name": "Advanced Camping Gear",
            "description": "High-end camping gear",
            "parent": "Camping Gear",
        },
    ]

    # Create categories
    for category_data in categories:
        parent_name = category_data.pop("parent")
        parent_category = (
            Category.objects.filter(name=parent_name).first() if parent_name else None
        )

        category, created = Category.objects.get_or_create(
            name=category_data["name"],
            defaults={
                "description": category_data["description"],
                "parent": parent_category,
                "created_by": admin_user,
                "updated_by": admin_user,
            },
        )

        if created:
            print(f"Category '{category.name}' created successfully.")
        else:
            print(f"Category '{category.name}' already exists.")


def create_products():
    # Fetch the admin user who will be the 'created_by' and 'updated_by'
    admin_user = User.objects.get(username="admin")

    products = [
        {
            "name": "Samsung Galaxy S22",
            "short_description": "High-end Android smartphone",
            "long_description": "Samsung Galaxy S22 with 128GB storage and 8GB RAM.",
            "price": 999.99,
            "category_name": "Android Phones",
            "quantity": 25,
        },
        {
            "name": "Apple MacBook Pro",
            "short_description": "High-performance laptop",
            "long_description": "Apple MacBook Pro with M1 chip, 16GB RAM, and 512GB SSD.",
            "price": 1999.99,
            "category_name": "Laptop Accessories",
            "quantity": 10,
        },
        {
            "name": "Sony WH-1000XM4",
            "short_description": "Noise-canceling headphones",
            "long_description": "Over-ear wireless headphones with industry-leading noise cancellation.",
            "price": 349.99,
            "category_name": "Electronics",
            "quantity": 50,
        },
        {
            "name": "LG Convection Microwave",
            "short_description": "Convection microwave oven",
            "long_description": "LG 30L convection microwave with auto-cook menu.",
            "price": 299.99,
            "category_name": "Convection Microwaves",
            "quantity": 20,
        },
        {
            "name": "Men's Formal Suit",
            "short_description": "Stylish formal suit",
            "long_description": "Premium formal suit perfect for business meetings and formal occasions.",
            "price": 149.99,
            "category_name": "Formal Suits",
            "quantity": 15,
        },
        {
            "name": "Women's Evening Gown",
            "short_description": "Elegant evening gown",
            "long_description": "Stunning evening gown with intricate designs and premium fabric.",
            "price": 199.99,
            "category_name": "Evening Gowns",
            "quantity": 12,
        },
        {
            "name": "Camping Tent - 4 Person",
            "short_description": "Durable camping tent",
            "long_description": "Waterproof and windproof tent suitable for 4 people.",
            "price": 129.99,
            "category_name": "Camping Gear",
            "quantity": 30,
        },
        {
            "name": "Classic Cyberpunk Novel",
            "short_description": "Iconic cyberpunk book",
            "long_description": "A classic cyberpunk novel by a renowned author.",
            "price": 19.99,
            "category_name": "Classic Cyberpunk",
            "quantity": 100,
        },
        {
            "name": "Nike Football Shoes",
            "short_description": "Professional football shoes",
            "long_description": "High-performance football shoes with superior grip and comfort.",
            "price": 79.99,
            "category_name": "Football Gear",
            "quantity": 40,
        },
        {
            "name": "Samsung 4K Smart TV",
            "short_description": "Ultra HD Smart TV",
            "long_description": "Samsung 55-inch 4K Ultra HD Smart TV with HDR support.",
            "price": 699.99,
            "category_name": "Electronics",
            "quantity": 20,
        },
        {
            "name": "KitchenAid Mixer",
            "short_description": "All-purpose kitchen mixer",
            "long_description": "Powerful stand mixer with multiple attachments for all your kitchen needs.",
            "price": 499.99,
            "category_name": "Kitchen Appliances",
            "quantity": 15,
        },
        {
            "name": "Gaming Laptop - ASUS ROG",
            "short_description": "High-performance gaming laptop",
            "long_description": "ASUS ROG laptop with Intel i7, 16GB RAM, and NVIDIA RTX 3060.",
            "price": 1499.99,
            "category_name": "Laptop Accessories",
            "quantity": 8,
        },
        {
            "name": "Men's Casual Shirt",
            "short_description": "Comfortable casual shirt",
            "long_description": "Lightweight casual shirt perfect for daily wear.",
            "price": 29.99,
            "category_name": "Men's Clothing",
            "quantity": 50,
        },
        {
            "name": "Women's Summer Dress",
            "short_description": "Light and breezy summer dress",
            "long_description": "Stylish summer dress made from breathable fabric.",
            "price": 39.99,
            "category_name": "Women's Dresses",
            "quantity": 40,
        },
        {
            "name": "Advanced Camping Stove",
            "short_description": "Portable camping stove",
            "long_description": "High-efficiency camping stove for outdoor cooking.",
            "price": 69.99,
            "category_name": "Advanced Camping Gear",
            "quantity": 25,
        },
    ]

    for product_data in products:
        category = Category.objects.get(name=product_data.pop("category_name"))

        product, created = Product.objects.get_or_create(
            name=product_data["name"],
            defaults={
                "short_description": product_data["short_description"],
                "long_description": product_data["long_description"],
                "price": product_data["price"],
                "category": category,
                "quantity": product_data["quantity"],
                "created_by": admin_user,
                "updated_by": admin_user,
            },
        )

        if created:
            print(f"Product '{product.name}' created successfully.")
        else:
            print(f"Product '{product.name}' already exists.")

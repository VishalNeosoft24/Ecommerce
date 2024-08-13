from django.contrib.auth.models import User
from .models import Category, Product


created_by_user = User.objects.get(id=1)
updated_by_user = created_by_user
products_data = [
    {
        "name": "Smartphone",
        "short_description": "A modern smartphone with 4G LTE",
        "long_description": "This smartphone features a sleek design, powerful processor, and a high-quality camera.",
        "price": 299.99,
        "category_name": "Electronics",  # Single category for ForeignKey
        "quantity": 50,
        "is_active": True,
        "created_by": created_by_user,
        "updated_by": updated_by_user,
    },
    {
        "name": "Gaming Laptop",
        "short_description": "High-performance laptop for gaming",
        "long_description": "Experience smooth gaming with this laptop that has a powerful GPU and fast processor.",
        "price": 1199.99,
        "category_name": "Electronics",
        "quantity": 30,
        "is_active": True,
        "created_by": created_by_user,
        "updated_by": updated_by_user,
    },
    {
        "name": "Yoga Mat",
        "short_description": "Non-slip yoga mat",
        "long_description": "This yoga mat provides comfort and stability during your yoga practice.",
        "price": 29.99,
        "category_name": "Sports & Outdoors",
        "quantity": 100,
        "is_active": True,
        "created_by": created_by_user,
        "updated_by": updated_by_user,
    },
    {
        "name": "Digital Camera",
        "short_description": "High-resolution digital camera",
        "long_description": "Capture stunning images with this high-resolution digital camera.",
        "price": 499.99,
        "category_name": "Electronics",
        "quantity": 20,
        "is_active": True,
        "created_by": created_by_user,
        "updated_by": updated_by_user,
    },
    {
        "name": "Smart TV",
        "short_description": "4K Ultra HD Smart TV",
        "long_description": "Enjoy your favorite shows in stunning 4K Ultra HD with this Smart TV.",
        "price": 699.99,
        "category_name": "Electronics",
        "quantity": 25,
        "is_active": True,
        "created_by": created_by_user,
        "updated_by": updated_by_user,
    },
    {
        "name": "Men's Shirt",
        "short_description": "Cotton casual shirt",
        "long_description": "A comfortable and stylish cotton casual shirt for men.",
        "price": 19.99,
        "category_name": "Fashion",
        "quantity": 200,
        "is_active": True,
        "created_by": created_by_user,
        "updated_by": updated_by_user,
    },
    {
        "name": "Women's Dress",
        "short_description": "Elegant evening dress",
        "long_description": "This elegant evening dress is perfect for special occasions.",
        "price": 79.99,
        "category_name": "Fashion",
        "quantity": 75,
        "is_active": True,
        "created_by": created_by_user,
        "updated_by": updated_by_user,
    },
    {
        "name": "Boys' T-Shirt",
        "short_description": "Graphic T-shirt for boys",
        "long_description": "A cool and comfortable graphic T-shirt for boys.",
        "price": 9.99,
        "category_name": "Fashion",
        "quantity": 150,
        "is_active": True,
        "created_by": created_by_user,
        "updated_by": updated_by_user,
    },
    {
        "name": "Living Room Sofa",
        "short_description": "Comfortable living room sofa",
        "long_description": "A comfortable and stylish sofa for your living room.",
        "price": 399.99,
        "category_name": "Home & Kitchen",
        "quantity": 10,
        "is_active": True,
        "created_by": created_by_user,
        "updated_by": updated_by_user,
    },
    {
        "name": "Refrigerator",
        "short_description": "Energy-efficient refrigerator",
        "long_description": "This energy-efficient refrigerator keeps your food fresh and reduces energy consumption.",
        "price": 899.99,
        "category_name": "Home & Kitchen",
        "quantity": 15,
        "is_active": True,
        "created_by": created_by_user,
        "updated_by": updated_by_user,
    },
    {
        "name": "Wall Art",
        "short_description": "Beautiful canvas wall art",
        "long_description": "Add a touch of elegance to your home with this beautiful canvas wall art.",
        "price": 49.99,
        "category_name": "Home & Kitchen",
        "quantity": 80,
        "is_active": True,
        "created_by": created_by_user,
        "updated_by": updated_by_user,
    },
    {
        "name": "Science Fiction Book",
        "short_description": "Exciting science fiction novel",
        "long_description": "Dive into an exciting adventure with this science fiction novel.",
        "price": 14.99,
        "category_name": "Books",
        "quantity": 120,
        "is_active": True,
        "created_by": created_by_user,
        "updated_by": updated_by_user,
    },
    {
        "name": "Biography Book",
        "short_description": "Inspiring biography",
        "long_description": "Read about the life and achievements of a remarkable individual.",
        "price": 19.99,
        "category_name": "Books",
        "quantity": 90,
        "is_active": True,
        "created_by": created_by_user,
        "updated_by": updated_by_user,
    },
    {
        "name": "Treadmill",
        "short_description": "High-performance treadmill",
        "long_description": "Stay fit and healthy with this high-performance treadmill.",
        "price": 599.99,
        "category_name": "Sports & Outdoors",
        "quantity": 15,
        "is_active": True,
        "created_by": created_by_user,
        "updated_by": updated_by_user,
    },
    {
        "name": "Camping Tent",
        "short_description": "Durable camping tent",
        "long_description": "This durable camping tent is perfect for your outdoor adventures.",
        "price": 99.99,
        "category_name": "Sports & Outdoors",
        "quantity": 40,
        "is_active": True,
        "created_by": created_by_user,
        "updated_by": updated_by_user,
    },
]


def get_category_instance(category_name):
    """
    Fetch the Category instance based on the category name.
    """
    category, created = Category.objects.get_or_create(name=category_name)
    return category


for product_data in products_data:
    category_instance = get_category_instance(product_data.pop("category_name"))
    product_data["category"] = category_instance
    Product.objects.create(**product_data)

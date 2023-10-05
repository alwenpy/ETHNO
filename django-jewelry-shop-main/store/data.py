# Import the necessary settings to set up the Django environment
import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable to your project's settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerceshop.settings')

# Initialize Django
django.setup()

# Now you can import your model
from store.models import Review  # Replace 'your_app' with the actual name of your Django app

# Your script logic here
objects = Review.objects.filter(product=product, rating=rating, user=user)
print(objects)

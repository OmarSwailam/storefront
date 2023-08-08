# E-Commerce RESTful API
Production ready Django REST Framework API that leverages Celery as a distributed task queue and Redis as both a
message broker and a caching solution. The result is a powerful e-commerce backend that can be seamlessly integrated into
any application or website.

- Implemented user authentication with Djoser library and json web token (JWT).
- Implemented payment gateway using stripe.
- Designed shopping cart functionality and order placement.
- Product search and filtering this allows users to quickly and easily find the products they're looking for.
- Used Celery for asynchronous task processing such as sending confirmation emails and updating order status.
- Utilized Redis for caching frequently accessed data to improve performance and reduce database load.
- Optimized database queries for improved performance and scalability.
- Created custom permissions, custom filters, custom validators and custom model manager.
- Designed a custom admin panel for managing products, orders, and users.
- Used Locust to load test the API and optimize the performance.
- Used Silk for a live profiling and inspection tool as it intercepts and stores HTTP requests and database queries

## installation
```

# Clone repository
  git clone https://github.com/OmarSwailam/storefront.git

# make sure docker is installed on your machine

# run the application
  docker-compose up -d --build

```

Author: Omar Swailam

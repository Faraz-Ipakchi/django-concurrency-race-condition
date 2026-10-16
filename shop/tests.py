from concurrent.futures import ThreadPoolExecutor
from django.test import TransactionTestCase
from django.db import connections
from rest_framework.test import APIClient
from .models import Product, Order


class ConcurrencyPurchaseTest(TransactionTestCase):

    def run_concurrent_requests(self, url_path, num_requests=10):
        Order.objects.all().delete()
        Product.objects.all().delete()
        product = Product.objects.create(name="iPhone", stock=1, price=1000)

        def make_request(_):
            client = APIClient()
            response = client.post(f"/api/products/{product.id}/{url_path}/")
            connections.close_all()
            return response.status_code

        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            results = list(executor.map(make_request, range(num_requests)))

        success_count = results.count(200)
        fail_count = results.count(400)
        product.refresh_from_db()
        orders_created = Order.objects.count()

        print(f"\n--- Results for: {url_path} ---")
        print(f"Initial Stock: 1 | Concurrent Requests: {num_requests}")
        print(f"Successful Purchases (200 OK): {success_count}")
        print(f"Failed Requests (400 Out of Stock): {fail_count}")
        print(f"Orders Created in DB: {orders_created}")
        print(f"Final Stock in DB: {product.stock}")
        print("-" * 40)

        return success_count, product.stock

    def test_all_approaches(self):
        self.run_concurrent_requests("purchase-naive", num_requests=10)

        self.run_concurrent_requests("purchase-atomic", num_requests=10)

        success_lock, stock_lock = self.run_concurrent_requests("purchase-lock", num_requests=10)
        self.assertEqual(success_lock, 1)
        self.assertEqual(stock_lock, 0)

        success_f, stock_f = self.run_concurrent_requests("purchase-f", num_requests=10)
        self.assertEqual(success_f, 1)
        self.assertEqual(stock_f, 0)
from decimal import Decimal

from django.contrib.messages import get_messages
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

# Исправленные импорты - с полным путем от apps
from apps.my_app.forms import ContactForm
from apps.my_app.models import Product


class IntegrationFlowTest(TestCase):
    """Интеграционные тесты с использованием Django TestCase."""

    @classmethod
    def setUpTestData(cls):
        """Создаём данные для всех тестов (выполняется один раз)."""
        cls.product = Product.objects.create(
            name='Интеграционный продукт',
            description='Для тестирования',
            price=Decimal('199'),
            stock=15,
            is_active=True
        )

    def test_full_user_journey(self):
        """Полный путь пользователя."""
        # 1. Главная страница
        response = self.client.get(reverse('my_app:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Интеграционный продукт')

        # 2. Страница списка продуктов
        response = self.client.get(reverse('my_app:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertTemplateUsed(response, 'my_app/product_list.html')

        # 3. Детальная страница продукта
        response = self.client.get(reverse('my_app:product_detail', args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.product.price))
        self.assertContains(response, self.product.name)

        # 4. Страница контактов
        response = self.client.get(reverse('my_app:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_app/contact.html')

        # 5. Отправка формы
        response = self.client.post(reverse('my_app:contact'), {
            'name': 'Тестовый пользователь',
            'email': 'test@example.com',
            'message': 'Тест интеграции'
        }, follow=True)

        self.assertRedirects(response, reverse('my_app:contact'))

        # 6. Проверка сообщения об успехе (используем messages framework)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Сообщение отправлено!')

    def test_inactive_product_not_visible_in_journey(self):
        """Проверка, что неактивный продукт не виден в пользовательском пути."""
        # Деактивируем продукт
        self.product.is_active = False
        self.product.save()

        # Главная страница
        response = self.client.get(reverse('my_app:home'))
        self.assertNotContains(response, self.product.name)

        # Список продуктов
        response = self.client.get(reverse('my_app:product_list'))
        self.assertNotContains(response, self.product.name)

        # Прямой доступ к детальной странице
        response = self.client.get(reverse('my_app:product_detail', args=[self.product.pk]))
        self.assertEqual(response.status_code, 404)


class CRUDIntegrationTest(TestCase):
    """Тестирование CRUD операций."""

    def test_product_crud_flow(self):
        """Полный цикл CRUD операций."""
        # 1. CREATE
        product = Product.objects.create(
            name='CRUD Продукт',
            description='Создан в тесте',
            price=Decimal('299.99'),
            stock=20,
            is_active=True
        )

        self.assertEqual(product.name, 'CRUD Продукт')
        self.assertEqual(product.price, Decimal('299.99'))

        # 2. READ
        response = self.client.get(reverse('my_app:product_detail', args=[product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CRUD Продукт')

        # Ищем просто число 299.99 (без символа рубля)
        content = response.content.decode('utf-8')
        self.assertTrue('299.99' in content or '299,99' in content,
                        f"Price '299.99' not found. Content snippet: {content[:500]}")

        # 3. UPDATE
        product.name = 'Обновлённый продукт'
        product.price = Decimal('399.99')
        product.save()

        product.refresh_from_db()

        response = self.client.get(reverse('my_app:product_detail', args=[product.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Обновлённый продукт')

        # Ищем просто число 399.99
        content = response.content.decode('utf-8')
        self.assertTrue('399.99' in content or '399,99' in content,
                        f"Price '399.99' not found. Content snippet: {content[:500]}")

        # 4. DELETE
        product_id = product.pk
        product.delete()

        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(pk=product_id)

        response = self.client.get(reverse('my_app:product_detail', args=[product_id]))
        self.assertEqual(response.status_code, 404)

class DatabasePerformanceTest(TestCase):
    """Тесты производительности БД."""

    @classmethod
    def setUpTestData(cls):
        """Создаём много тестовых данных один раз."""
        cls.products = []
        for i in range(50):
            cls.products.append(
                Product.objects.create(
                    name=f'Тест {i}',
                    price=Decimal('50.00'),
                    stock=i,
                    is_active=(i % 2 == 0)
                )
            )

    def test_query_count_on_product_list(self):
        """Проверка количества запросов на странице списка."""
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(reverse('my_app:product_list'))
            self.assertEqual(response.status_code, 200)

        self.assertLessEqual(len(context.captured_queries), 3)

    def test_query_count_on_home_page(self):
        """Проверка количества запросов на главной странице."""
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(reverse('my_app:home'))
            self.assertEqual(response.status_code, 200)

        self.assertEqual(len(context.captured_queries), 2)

    def test_bulk_creation_performance(self):
        """Тест массового создания (bulk_create)."""
        products_data = [
            Product(name=f'Bulk {i}', price=Decimal('10.00'), stock=i)
            for i in range(100, 200)
        ]

        with CaptureQueriesContext(connection) as context:
            Product.objects.bulk_create(products_data)

        self.assertEqual(len(context.captured_queries), 1)
        self.assertEqual(Product.objects.filter(name__startswith='Bulk').count(), 100)


class FormIntegrationTest(TestCase):
    """Интеграционные тесты форм."""

    def test_contact_form_submission(self):
        """Тест отправки контактной формы."""
        response = self.client.get(reverse('my_app:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], ContactForm)

        response = self.client.post(
            reverse('my_app:contact'),
            {
                'name': 'Тестовый Пользователь',
                'email': 'test@example.com',
                'message': 'Тестовое сообщение'
            },
            follow=True
        )

        self.assertRedirects(response, reverse('my_app:contact'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Сообщение отправлено!')

    def test_contact_form_invalid_data(self):
        """Тест отправки формы с невалидными данными."""
        response = self.client.post(reverse('my_app:contact'), {
            'name': '',
            'email': 'invalid-email',
            'message': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertIn('email', response.context['form'].errors)
        self.assertIn('name', response.context['form'].errors)


class SecurityIntegrationTest(TestCase):
    """Тесты безопасности."""

    def test_admin_page_requires_login(self):
        """Проверка защиты админ-панели."""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/admin/login/'))

    def test_csrf_protection_on_forms(self):
        """Проверка CSRF защиты на формах."""
        response = self.client.get(reverse('my_app:contact'))
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_sql_injection_protection(self):
        """Проверка защиты от SQL инъекций."""
        Product.objects.create(
            name='Тестовый продукт',
            description='Для теста безопасности',
            price=Decimal('99.99'),
            stock=10,
            is_active=True
        )

        initial_count = Product.objects.count()

        malicious_input = "'; DROP TABLE my_app_product; --"

        response = self.client.post(
            reverse('my_app:contact'),
            {
                'name': malicious_input,
                'email': 'test@example.com',
                'message': 'Test'
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.count(), initial_count)


class ClientIntegrationTest(TestCase):
    """Расширенные тесты с использованием Client."""

    def test_ajax_request(self):
        """Тест AJAX запросов."""
        response = self.client.get(
            reverse('my_app:product_list'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

    def test_follow_redirects(self):
        """Тест с автоматическим следованием редиректам."""
        response = self.client.post(
            reverse('my_app:contact'),
            {
                'name': 'Test',
                'email': 'test@example.com',
                'message': 'Test'
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Сообщение отправлено!')

    def test_secure_headers(self):
        """Проверка security headers."""
        response = self.client.get(reverse('my_app:home'))

        self.assertIn('X-Content-Type-Options', response)
        self.assertIn('X-Frame-Options', response)
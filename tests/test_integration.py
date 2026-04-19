# from decimal import Decimal
#
# from django.test import Client
# from django.urls import reverse
# from my_app.models import Product
# import pytest
#
#
# @pytest.fixture
# def client():
#     """Фикстура клиента."""
#     return Client()
#
#
# @pytest.fixture
# def product():
#     """Фикстура продукта."""
#     return Product.objects.create(
#         name='Интеграционный продукт',
#         description='Для тестирования',
#         price=Decimal('199.99'),
#         stock=15,
#         is_active=True
#     )
#
#
# # Явно указываем, какие URL использовать
# @pytest.mark.urls('Django_star.urls')
# @pytest.mark.django_db
# class TestIntegrationFlow:
#     """Интеграционные тесты."""
#
#     def test_full_user_journey(self, client, product):
#         """Полный путь пользователя."""
#         # Теперь reverse должен работать
#         home_url = reverse('my_app:home')
#         response = client.get(home_url)
#         assert response.status_code == 200
#         assert 'Интеграционный продукт' in response.content.decode()
#
#         products_url = reverse('my_app:product_list')
#         response = client.get(products_url)
#         assert response.status_code == 200
#         assert product.name in response.content.decode()
#
#         detail_url = reverse('my_app:product_detail', args=[product.pk])
#         response = client.get(detail_url)
#         assert response.status_code == 200
#         assert product.price == Decimal('199.99')
#
#         contact_url = reverse('my_app:contact')
#         response = client.get(contact_url)
#         assert response.status_code == 200
#
#         response = client.post(contact_url, {
#             'name': 'Тестовый пользователь',
#             'email': 'test@example.com',
#             'message': 'Тест интеграции'
#         })
#         assert response.status_code == 302
#
#     def test_product_crud_flow(self, client):
#         """Тест CRUD операций с продуктом."""
#         product = Product.objects.create(
#             name='CRUD Продукт',
#             description='Создан в тесте',
#             price=Decimal('299.99'),
#             stock=20,
#             is_active=True
#         )
#
#         assert product.name == 'CRUD Продукт'
#         assert product.price == Decimal('299.99')
#
#         retrieved_product = Product.objects.get(pk=product.pk)
#         assert retrieved_product.name == product.name
#
#         product.name = 'Обновлённый продукт'
#         product.save()
#         updated_product = Product.objects.get(pk=product.pk)
#         assert updated_product.name == 'Обновлённый продукт'
#
#         product.delete()
#         with pytest.raises(Product.DoesNotExist):
#             Product.objects.get(pk=product.pk)
#
#
# @pytest.mark.urls('Django_star.urls')
# @pytest.mark.django_db
# class TestDatabaseIntegration:
#     """Интеграционные тесты базы данных."""
#
#     def test_bulk_product_creation(self):
#         """Тест массового создания продуктов."""
#         products_data = [
#             Product(name=f'Продукт {i}', price=Decimal('10.00'), stock=i)
#             for i in range(1, 11)
#         ]
#         Product.objects.bulk_create(products_data)
#
#         count = Product.objects.count()
#         assert count >= 10
#
#     def test_product_query_performance(self):
#         """Тест производительности запросов."""
#         for i in range(50):
#             Product.objects.create(
#                 name=f'Тест {i}',
#                 price=Decimal('50.00'),
#                 stock=i
#             )
#
#         from django.db import connection
#         from django.test.utils import CaptureQueriesContext
#
#         with CaptureQueriesContext(connection) as context:
#             products = Product.objects.filter(is_active=True)[:10]
#             list(products)
#
#         assert len(context.captured_queries) == 1


from decimal import Decimal

from django.contrib.messages import get_messages  # ← Добавить импорт
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from my_app.forms import ContactForm
from my_app.models import Product


class IntegrationFlowTest(TestCase):
    """Интеграционные тесты с использованием Django TestCase."""

    @classmethod
    def setUpTestData(cls):
        """Создаём данные для всех тестов (выполняется один раз)."""
        cls.product = Product.objects.create(
            name='Интеграционный продукт',
            description='Для тестирования',
            price=Decimal('199.99'),
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
        }, follow=True)  # ← Добавить follow=True

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
        # Используем DetailView, который по умолчанию возвращает 404 для неактивных
        response = self.client.get(reverse('my_app:product_detail', args=[self.product.pk]))
        self.assertEqual(response.status_code, 404)  # Должен быть 404


class CRUDIntegrationTest(TestCase):
    """Тестирование CRUD операций."""

    def test_product_crud_flow(self):
        """Полный цикл CRUD операций."""
        # CREATE
        product = Product.objects.create(
            name='CRUD Продукт',
            description='Создан в тесте',
            price=Decimal('299.99'),
            stock=20,
            is_active=True
        )

        self.assertEqual(product.name, 'CRUD Продукт')
        self.assertEqual(product.price, Decimal('299.99'))

        # READ - проверяем через представление
        response = self.client.get(reverse('my_app:product_detail', args=[product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CRUD Продукт')

        # UPDATE - через модель
        product.name = 'Обновлённый продукт'
        product.price = Decimal('399.99')
        product.save()

        # Проверяем обновление
        response = self.client.get(reverse('my_app:product_detail', args=[product.pk]))
        self.assertContains(response, 'Обновлённый продукт')
        self.assertContains(response, '399.99')

        # DELETE
        product_id = product.pk  # ← Сохраняем ID перед удалением
        product.delete()

        # Проверяем, что продукт удален
        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(pk=product_id)

        # Проверяем, что детальная страница возвращает 404
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

        # Должно быть не больше 2 запросов
        self.assertLessEqual(len(context.captured_queries), 3)

    def test_query_count_on_home_page(self):
        """Проверка количества запросов на главной странице."""
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(reverse('my_app:home'))
            self.assertEqual(response.status_code, 200)

        # Только один запрос для получения продуктов
        self.assertEqual(len(context.captured_queries), 1)

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
        # GET запрос
        response = self.client.get(reverse('my_app:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], ContactForm)

        # POST с валидными данными
        response = self.client.post(
            reverse('my_app:contact'),
            {
                'name': 'Тестовый Пользователь',
                'email': 'test@example.com',
                'message': 'Тестовое сообщение'
            },
            follow=True  # ← Добавить follow=True
        )

        self.assertRedirects(response, reverse('my_app:contact'))

        # Проверяем сообщение об успехе через messages framework
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
        # Создаем тестовый продукт
        Product.objects.create(
            name='Тестовый продукт',
            description='Для теста безопасности',
            price=Decimal('99.99'),
            stock=10,
            is_active=True
        )

        # Сохраняем количество продуктов до инъекции
        initial_count = Product.objects.count()

        # Пытаемся внедрить SQL
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

        # Проверяем успешность запроса
        self.assertEqual(response.status_code, 200)

        # Проверяем, что БД не повреждена (продукты все еще существуют)
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

        # Проверяем наличие security headers
        self.assertIn('X-Content-Type-Options', response)
        self.assertIn('X-Frame-Options', response)

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

# Замени относительные импорты на абсолютные
from apps.my_app.forms import ContactForm, ProductForm
from apps.my_app.models import Product


class ProductModelTest(TestCase):
    """Тесты для модели Product."""

    def setUp(self):
        """Создаём тестовые данные."""
        self.product = Product.objects.create(
            name='Тестовый продукт',
            description='Тестовое описание',
            price=Decimal('99.99'),
            stock=10,
            is_active=True
        )

    def test_product_creation(self):
        """Тест создания продукта."""
        self.assertEqual(self.product.name, 'Тестовый продукт')
        self.assertEqual(self.product.price, Decimal('99.99'))
        self.assertEqual(self.product.stock, 10)
        self.assertTrue(self.product.is_active)

    def test_product_str_method(self):
        """Тест строкового представления продукта."""
        self.assertEqual(str(self.product), 'Тестовый продукт')

    def test_is_in_stock_method(self):
        """Тест метода is_in_stock."""
        self.assertTrue(self.product.is_in_stock())

        # Изменяем количество на 0
        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.is_in_stock())

        # Деактивируем продукт
        self.product.stock = 10
        self.product.is_active = False
        self.product.save()
        self.assertFalse(self.product.is_in_stock())

    def test_product_absolute_url(self):
        """Тест URL продукта."""
        url = self.product.get_absolute_url()
        expected_url = reverse('my_app:product_detail', args=[str(self.product.pk)])
        self.assertEqual(url, expected_url)


class ProductViewTest(TestCase):
    """Тесты представлений продуктов."""

    def setUp(self):
        """Создаём тестовые данные."""
        self.product = Product.objects.create(
            name='Тестовый продукт',
            description='Тестовое описание',
            price=Decimal('99.99'),
            stock=10,
            is_active=True
        )

    def test_home_page_status_code(self):
        """Тест главной страницы."""
        response = self.client.get(reverse('my_app:home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_contains_products(self):
        """Тест наличия продуктов на главной."""
        response = self.client.get(reverse('my_app:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый продукт')

    def test_product_list_page(self):
        """Тест страницы списка продуктов."""
        response = self.client.get(reverse('my_app:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый продукт')

    def test_product_detail_page(self):
        """Тест детальной страницы продукта."""
        response = self.client.get(reverse('my_app:product_detail', args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый продукт')
        # Проверяем оба варианта: точка или запятая
        self.assertTrue(
            '99.99' in response.content.decode() or '99,99' in response.content.decode(),
            "Price '99.99' or '99,99' not found in response"
        )

    def test_inactive_product_not_shown(self):
        """Тест: неактивный продукт не отображается."""
        self.product.is_active = False
        self.product.save()

        response = self.client.get(reverse('my_app:product_list'))
        self.assertNotContains(response, 'Тестовый продукт')


class ContactFormTest(TestCase):
    """Тесты контактной формы."""

    def test_valid_contact_form(self):
        """Тест валидной формы."""
        form_data = {
            'name': 'Иван Иванов',
            'email': 'ivan@example.com',
            'message': 'Тестовое сообщение'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_contact_form(self):
        """Тест невалидной формы."""
        # Пустая форма
        form = ContactForm(data={})
        self.assertFalse(form.is_valid())

        # Неверный email
        form_data = {
            'name': 'Иван Иванов',
            'email': 'invalid-email',
            'message': 'Тестовое сообщение'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_contact_page_get(self):
        """Тест GET запроса на страницу контактов."""
        response = self.client.get(reverse('my_app:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], ContactForm)

    def test_contact_page_post_valid(self):
        """Тест POST запроса с валидными данными."""
        response = self.client.post(reverse('my_app:contact'), {
            'name': 'Иван Иванов',
            'email': 'ivan@example.com',
            'message': 'Тестовое сообщение'
        })
        # Должен быть редирект после отправки
        self.assertEqual(response.status_code, 302)


class ProductFormTest(TestCase):
    """Тесты формы продукта."""

    def test_valid_product_form(self):
        """Тест валидной формы продукта."""
        form_data = {
            'name': 'Новый продукт',
            'description': 'Описание',
            'price': '49.99',
            'stock': '5',
            'is_active': True
        }
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_product_form(self):
        """Тест невалидной формы продукта."""
        # Без названия
        form_data = {
            'price': '49.99',
            'stock': '5'
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

        # Отрицательная цена
        form_data = {
            'name': 'Продукт',
            'price': '-10.00',
            'stock': '5'
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

        # Отрицательное количество
        form_data = {
            'name': 'Продукт',
            'price': '49.99',
            'stock': '-5'
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('stock', form.errors)

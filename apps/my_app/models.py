from django.db import models
from django.urls import reverse


class Product(models.Model):
    """Простая модель продукта для тестирования."""
    name: models.CharField = models.CharField('Название', max_length=200)
    description: models.TextField = models.TextField('Описание', blank=True)
    price: models.DecimalField = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    stock: models.PositiveIntegerField = models.PositiveIntegerField('Количество', default=0)
    is_active: models.BooleanField = models.BooleanField('Активен', default=True)
    created_at: models.DateTimeField = models.DateTimeField('Создан', auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField('Обновлён', auto_now=True)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return str(self.name)

    def get_absolute_url(self) -> str:
        return reverse('my_app:product_detail', args=[str(self.pk)])

    def is_in_stock(self) -> bool:
        """Проверяет, есть ли товар в наличии."""
        return bool(self.stock > 0 and self.is_active)

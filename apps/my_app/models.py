from contextlib import suppress

from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.urls import reverse

from src.Django_star.loggers import get_logger

# Создаем логгер для моделей
logger = get_logger(__name__)


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
        in_stock = bool(self.stock > 0 and self.is_active)

        # Логируем проверку наличия (уровень DEBUG для отладки)
        if not in_stock and self.stock > 0:
            logger.debug(f"Продукт '{self.name}' (ID: {self.pk}) активен, но нет в наличии")
        elif not in_stock and not self.is_active:
            logger.debug(f"Продукт '{self.name}' (ID: {self.pk}) неактивен")

        return in_stock


# Сигналы для автоматического логирования изменений продуктов
@receiver(post_save, sender=Product)
def log_product_save(sender, instance, created, **kwargs):
    """Логирует создание и обновление продуктов."""
    if created:
        logger.info(
            f"Создан новый продукт: '{instance.name}' (ID: {instance.pk}), "
            f"цена: {instance.price}, количество: {instance.stock}"
        )
    else:
        # Получаем старые значения для более информативного лога
        if hasattr(instance, '_old_data'):
            changes = []
            for field in ['name', 'price', 'stock', 'is_active']:
                old_value = getattr(instance._old_data, field, None)
                new_value = getattr(instance, field)
                if old_value != new_value:
                    changes.append(f"{field}: {old_value} -> {new_value}")

            if changes:
                logger.info(
                    f"Обновлен продукт '{instance.name}' (ID: {instance.pk}): "
                    f"{', '.join(changes)}"
                )
            else:
                logger.info(f"Обновлен продукт '{instance.name}' (ID: {instance.pk})")
        else:
            logger.info(f"Обновлен продукт '{instance.name}' (ID: {instance.pk})")


@receiver(post_delete, sender=Product)
def log_product_delete(sender, instance, **kwargs):
    """Логирует удаление продуктов."""
    logger.warning(
        f"Удален продукт: '{instance.name}' (ID: {instance.pk}), "
        f"цена: {instance.price}, количество: {instance.stock}"
    )


# Вспомогательный класс для логирования изменений
class ProductUpdateLogger:
    """Вспомогательный класс для логирования изменений."""

    @staticmethod
    def save_old_data(instance):
        """Сохраняет старые данные перед обновлением."""
        if instance.pk:
            # Используем contextlib.suppress вместо try-except-pass
            with suppress(Product.DoesNotExist):
                instance._old_data = Product.objects.get(pk=instance.pk)

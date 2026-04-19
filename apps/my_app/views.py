from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView, TemplateView

from src.Django_star.loggers import get_logger

from .forms import ContactForm
from .models import Product

# Создаем логгер для представлений
logger = get_logger(__name__)


class HomeView(TemplateView):
    """Главная страница."""
    template_name = 'my_app/home.html'

    def get_context_data(self, **kwargs):
        logger.debug("Загрузка главной страницы")
        context = super().get_context_data(**kwargs)

        products_count = Product.objects.filter(is_active=True).count()
        context['products'] = Product.objects.filter(is_active=True)[:6]

        logger.info(
            f"Главная страница загружена. Показано {min(6, products_count)} из {products_count} активных продуктов")
        return context


class ProductListView(ListView):
    """Список продуктов."""
    model = Product
    template_name = 'my_app/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        logger.debug("Запрос списка активных продуктов")
        queryset = Product.objects.filter(is_active=True)

        # Логируем количество найденных продуктов
        count = queryset.count()
        logger.info(f"Найдено {count} активных продуктов")

        return queryset

    def get(self, request, *args, **kwargs):
        # Логируем информацию о запросе
        page = request.GET.get('page', 1)
        logger.debug(f"GET запрос к списку продуктов, страница: {page}, пользователь: {request.user}")

        return super().get(request, *args, **kwargs)


class ProductDetailView(DetailView):
    """Детальная страница продукта."""
    model = Product
    template_name = 'my_app/product_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        """Переопределяем для возврата 404 если продукт неактивен."""
        obj = super().get_object(queryset=queryset)

        # Логируем попытку доступа к продукту
        logger.debug(f"Запрос деталей продукта ID: {obj.pk}, название: '{obj.name}'")

        if not obj.is_active:
            logger.warning(
                f"Попытка доступа к неактивному продукту ID: {obj.pk}, "
                f"название: '{obj.name}', пользователь: {self.request.user}"
            )
            from django.http import Http404
            raise Http404("Продукт неактивен")

        logger.info(f"Просмотр продукта: '{obj.name}' (ID: {obj.pk}), цена: {obj.price}, в наличии: {obj.stock}")
        return obj


def contact_view(request):
    """Страница контактов с формой."""
    logger.debug(f"GET запрос к контактной странице от {request.user}")

    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            # Логируем успешную отправку (без sensitive данных)
            cleaned_data = form.cleaned_data
            name = cleaned_data.get('name', 'Unknown')
            email = cleaned_data.get('email', 'Unknown')
            message = cleaned_data.get('message', '')

            logger.info(
                f"Отправлена контактная форма от {name} (email: {email}), "
                f"сообщение: {message[:50] if message else 'пусто'}..."
            )

            messages.success(request, 'Сообщение отправлено!')
            return redirect('my_app:contact')
        else:
            # Логируем ошибки валидации
            logger.warning(
                f"Ошибка валидации контактной формы от {request.user}: {form.errors}"
            )
    else:
        form = ContactForm()

    return render(request, 'my_app/contact.html', {'form': form})


def health_check(request):
    """Health check endpoint for Docker."""
    logger.debug("Health check запрос выполнен")
    return HttpResponse("OK")

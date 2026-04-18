from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, TemplateView
from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContactForm
from .models import Product


class HomeView(TemplateView):
    """Главная страница."""
    template_name = 'my_app/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(is_active=True)[:6]
        return context


class ProductListView(ListView):
    """Список продуктов."""
    model = Product
    template_name = 'my_app/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        return Product.objects.filter(is_active=True)


class ProductDetailView(DetailView):
    """Детальная страница продукта."""
    model = Product
    template_name = 'my_app/product_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        """Переопределяем для возврата 404 если продукт неактивен."""
        obj = super().get_object(queryset=queryset)
        if not obj.is_active:
            from django.http import Http404
            raise Http404("Продукт неактивен")
        return obj


def contact_view(request):
    """Страница контактов с формой."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Сообщение отправлено!')
            return redirect('my_app:contact')
    else:
        form = ContactForm()

    return render(request, 'my_app/contact.html', {'form': form})
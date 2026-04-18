from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    """Форма для создания/редактирования продукта."""

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_price(self):
        """Валидация цены."""
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError('Цена должна быть больше 0')
        return price

    def clean_stock(self):
        """Валидация количества."""
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError('Количество не может быть отрицательным')
        return stock


class ContactForm(forms.Form):
    """Простая контактная форма."""
    name = forms.CharField(max_length=100, label='Имя')
    email = forms.EmailField(label='Email')
    message = forms.CharField(widget=forms.Textarea, label='Сообщение')

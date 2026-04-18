from django.urls import path

from . import views

app_name = 'my_app'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('contact/', views.contact_view, name='contact'),  # ← добавить этот маршрут
]

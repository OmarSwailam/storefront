from django.urls import path
from . import views


urlpatterns = [
    path('products', views.product_list),
    path('products/<int:pk>', views.product_detail),
    path('collections', views.collection_list),
    path('collections/<int:pk>', views.collection_detail, name='collection-detail'),
]

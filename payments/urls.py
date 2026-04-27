from django.urls import path
from .views import CreateCheckoutSessionView, OrderListView

urlpatterns = [
    path('checkout/', CreateCheckoutSessionView.as_view(), name='checkout'),
    path('orders/', OrderListView.as_view(), name='orders'),
]

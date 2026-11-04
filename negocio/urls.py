from django.urls import path
from . import views

app_name = "negocio"
urlpatterns = [
    path("", views.NegocioUpdateView.as_view(), name="editar"),
]

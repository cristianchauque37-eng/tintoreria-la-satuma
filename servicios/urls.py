from django.urls import path
from . import views

app_name = "servicios"
urlpatterns = [
    path("", views.ServicioPublicoListView.as_view(), name="publico"),
    path("catalogo/", views.ServicioCatalogoView.as_view(), name="catalogo"),
    path("gestion/", views.ServicioGestionListView.as_view(), name="gestion"),
    path("gestion/nuevo/", views.ServicioCreateView.as_view(), name="crear"),
    path("gestion/<int:pk>/editar/", views.ServicioUpdateView.as_view(), name="editar"),
    path(
        "gestion/<int:pk>/estado/",
        views.ServicioCambiarEstadoView.as_view(),
        name="estado",
    ),
]

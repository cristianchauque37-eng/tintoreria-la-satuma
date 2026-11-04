from django.urls import path

from . import views

app_name = "consultas"
urlpatterns = [
    path("", views.ConsultaCreateView.as_view(), name="nueva"),
    path("gestion/", views.ConsultaGestionListView.as_view(), name="gestion"),
    path(
        "gestion/<int:pk>/estado/",
        views.ConsultaCambiarEstadoView.as_view(),
        name="estado",
    ),
    path("enviada/", views.ConsultaEnviadaView.as_view(), name="enviada"),
]

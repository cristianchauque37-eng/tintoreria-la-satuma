from django.urls import path

from . import views

app_name = "consultas"
urlpatterns = [
    path("", views.ConsultaCreateView.as_view(), name="nueva"),
    path("enviada/", views.ConsultaEnviadaView.as_view(), name="enviada"),
]

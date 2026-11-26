from django.contrib.auth.views import LoginView
from .forms import AccesoForm


class AccesoView(LoginView):
    template_name = "cuentas/login.html"
    authentication_form = AccesoForm
    redirect_authenticated_user = True

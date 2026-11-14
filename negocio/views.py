from django.urls import reverse_lazy
from django.views.generic import UpdateView
from cuentas.mixins import GuardadoSeguroMixin, SoloAdministradorMixin
from .forms import NegocioForm
from .models import Negocio


class NegocioUpdateView(SoloAdministradorMixin, GuardadoSeguroMixin, UpdateView):
    """HU05: el administrador modifica los datos del negocio."""

    form_class = NegocioForm
    template_name = "negocio/formulario.html"
    success_url = reverse_lazy("negocio:editar")

    def get_object(self, queryset=None):
        return Negocio.obtener()

    def form_valid(self, form):
        form.instance.administrador = self.request.user
        return super().form_valid(form)

from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, TemplateView

from negocio.models import Negocio

from .forms import ConsultaForm
from .models import Consulta


class ConsultaCreateView(CreateView):
    """Formulario público: no requiere iniciar sesión."""

    form_class = ConsultaForm
    template_name = "consultas/formulario.html"

    def get_initial(self):
        inicial = super().get_initial()
        if self.request.GET.get("servicio", "").isdigit():
            inicial["servicio"] = int(self.request.GET["servicio"])
        return inicial

    def form_valid(self, form):
        consulta = form.save()
        # Solo quien envió la consulta puede ver su confirmación.
        self.request.session["ultima_consulta"] = consulta.pk
        return redirect("consultas:enviada")


class ConsultaEnviadaView(TemplateView):
    template_name = "consultas/enviada.html"

    def dispatch(self, request, *args, **kwargs):
        if "ultima_consulta" not in request.session:
            return redirect("consultas:nueva")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        consulta = get_object_or_404(
            Consulta, pk=self.request.session["ultima_consulta"]
        )
        negocio = Negocio.obtener()
        contexto["consulta"] = consulta
        contexto["negocio"] = negocio
        contexto["enlace_whatsapp"] = consulta.enlace_whatsapp(negocio.whatsapp)
        return contexto

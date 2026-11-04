from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView

from catalogo.views import SoloAdministradorMixin
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


class ConsultaGestionListView(SoloAdministradorMixin, ListView):
    """HU11: el administrador ve las consultas con su servicio asociado."""

    model = Consulta
    template_name = "consultas/gestion.html"
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset().select_related("servicio")
        estado = self.request.GET.get("estado", "")
        if estado in Consulta.Estado.values:
            qs = qs.filter(estado=estado)
        q = self.request.GET.get("q", "").strip()[:100]
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(mensaje__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["estados"] = Consulta.Estado.choices
        contexto["estado_actual"] = self.request.GET.get("estado", "")
        return contexto


class ConsultaCambiarEstadoView(SoloAdministradorMixin, View):
    """HU12: pendiente, respondida o archivada."""

    http_method_names = ["post"]

    def post(self, request, pk):
        consulta = get_object_or_404(Consulta, pk=pk)
        estado = request.POST.get("estado")
        if estado in Consulta.Estado.values:
            consulta.estado = estado
            consulta.save(update_fields=["estado"])
            messages.success(
                request, f"Consulta marcada como {consulta.get_estado_display().lower()}."
            )
        else:
            messages.error(request, "Estado no válido.")
        return redirect("consultas:gestion")

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView
from catalogo.views import GuardadoSeguroMixin, SoloAdministradorMixin
from negocio.models import Negocio
from .forms import ServicioForm
from .models import Servicio


class ServicioPublicoListView(ListView):
    """HU06: cualquier visitante ve los servicios activos, sin iniciar sesión."""

    model = Servicio
    template_name = "servicios/publico.html"

    def get_queryset(self):
        return Servicio.objects.filter(activo=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["negocio"] = Negocio.obtener()
        return context


class ServicioGestionListView(SoloAdministradorMixin, ListView):
    model = Servicio
    template_name = "servicios/gestion.html"
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()[:100]
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
        return qs


class ServicioCreateView(SoloAdministradorMixin, GuardadoSeguroMixin, CreateView):
    """HU03: el administrador registra un servicio."""

    model = Servicio
    form_class = ServicioForm
    template_name = "servicios/formulario.html"
    success_url = reverse_lazy("servicios:gestion")

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        form.instance.actualizado_por = self.request.user
        return super().form_valid(form)


class ServicioUpdateView(SoloAdministradorMixin, GuardadoSeguroMixin, UpdateView):
    """HU04: el administrador modifica un servicio."""

    model = Servicio
    form_class = ServicioForm
    template_name = "servicios/formulario.html"
    success_url = reverse_lazy("servicios:gestion")

    def form_valid(self, form):
        form.instance.actualizado_por = self.request.user
        return super().form_valid(form)


class ServicioCambiarEstadoView(SoloAdministradorMixin, View):
    """HU04: dar de baja (o reactivar) sin borrar el registro."""

    http_method_names = ["post"]

    def post(self, request, pk):
        servicio = get_object_or_404(Servicio, pk=pk)
        servicio.activo = not servicio.activo
        servicio.actualizado_por = request.user
        servicio.save()
        if servicio.activo:
            messages.success(request, "Servicio reactivado.")
        else:
            messages.success(request, "Servicio dado de baja. Ya no se muestra a los clientes.")
        return redirect("servicios:gestion")

from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect, render

from consultas.models import Consulta
from cuentas.models import Usuario
from servicios.models import Servicio


def home(request):
    if not request.user.is_authenticated:
        return redirect("servicios:publico")
    contexto = {}
    if request.user.is_superuser:
        contexto = {
            "servicios_activos": Servicio.objects.filter(activo=True).count(),
            "consultas_pendientes": Consulta.objects.filter(
                estado=Consulta.Estado.PENDIENTE
            ).count(),
            "consultas_total": Consulta.objects.count(),
            "solicitudes_pendientes": Usuario.objects.filter(estado="pendiente").count(),
            "recientes": Consulta.objects.select_related("servicio")[:5],
        }
    return render(request, "inicio/home.html", contexto)


def salud(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return JsonResponse({"estado": "no disponible"}, status=503)
    return JsonResponse({"estado": "ok"})

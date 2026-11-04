from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect, render
from catalogo.models import Producto, Categoria
from cuentas.models import Usuario


def home(request):
    if not request.user.is_authenticated:
        return redirect("servicios:publico")
    return render(
        request,
        "inicio/home.html",
        {
            "productos": Producto.objects.count(),
            "categorias": Categoria.objects.count(),
            "pendientes": (
                Usuario.objects.filter(estado="pendiente").count()
                if request.user.is_superuser
                else None
            ),
            "recientes": Producto.objects.select_related("categoria").order_by(
                "-actualizado"
            )[:5],
        },
    )


def salud(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return JsonResponse({"estado": "no disponible"}, status=503)
    return JsonResponse({"estado": "ok"})

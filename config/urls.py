from django.contrib import admin
from django.conf import settings
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("cuentas/", include("cuentas.urls")),
    path("catalogo/", include("catalogo.urls")),
    path("servicios/", include("servicios.urls")),
    path("consultas/", include("consultas.urls")),
    path("negocio/", include("negocio.urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    path("", include("inicio.urls")),
]
admin.site.site_header = "Administración de la organización"
admin.site.site_title = "Administración"

from django.contrib import admin

from .models import Consulta


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "servicio", "estado", "creado")
    list_filter = ("estado", "servicio")
    search_fields = ("nombre", "mensaje")

from django.contrib import admin

from .models import Consulta


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "servicio", "estado", "administrador", "creado")
    list_filter = ("estado", "servicio")
    readonly_fields = ("administrador",)
    search_fields = ("nombre", "mensaje")

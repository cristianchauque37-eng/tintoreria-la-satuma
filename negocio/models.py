from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class Negocio(models.Model):
    """Datos de contacto de la tintorería. Hay un único registro (HU05)."""

    nombre_comercial = models.CharField(
        "nombre comercial", max_length=100, default="Tintorería La Satuma"
    )
    direccion = models.CharField("dirección", max_length=150, blank=True)
    horarios = models.CharField(max_length=100, blank=True)
    telefono = models.CharField("teléfono", max_length=20, blank=True)
    whatsapp = models.CharField(
        "WhatsApp",
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                r"^\d{10,15}$",
                "Escribí solo números, con código de país y sin +, espacios ni guiones.",
            )
        ],
        help_text="Solo números con código de país. Ejemplo: 5493874123456",
    )
    administrador = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        editable=False,
        related_name="negocio",
    )
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "negocio"
        verbose_name_plural = "negocio"

    def __str__(self):
        return self.nombre_comercial

    @classmethod
    def obtener(cls):
        """Devuelve el único registro, creándolo vacío la primera vez."""
        negocio, _ = cls.objects.get_or_create(pk=1)
        return negocio

    @property
    def enlace_whatsapp(self):
        return f"https://wa.me/{self.whatsapp}" if self.whatsapp else ""

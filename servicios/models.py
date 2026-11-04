from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Lower


class Servicio(models.Model):
    class Categoria(models.TextChoices):
        TINTORERIA = "tintoreria", "Tintorería"
        CALZADO = "calzado", "Calzado y accesorios"
        LAVANDERIA = "lavanderia", "Lavandería"
        OFERTAS = "ofertas", "Ofertas"
        OTROS = "otros", "Otros servicios"

    nombre = models.CharField(max_length=120)
    categoria = models.CharField(
        max_length=12, choices=Categoria.choices, default=Categoria.TINTORERIA
    )
    descripcion = models.TextField("descripción", blank=True, max_length=2000)
    precio = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    imagen = models.ImageField(
        "imagen", upload_to="servicios/", blank=True, null=True,
        help_text="Opcional. Formatos JPG, PNG o WEBP.",
    )
    activo = models.BooleanField(
        default=True, help_text="Si está desmarcado, no se muestra a los clientes."
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="servicios_creados",
    )
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="servicios_actualizados",
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre", "pk"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(precio__gte=0), name="servicio_precio_no_negativo"
            ),
            models.UniqueConstraint(
                Lower("nombre"), name="servicio_nombre_sin_mayusculas"
            ),
        ]

    def __str__(self):
        return self.nombre

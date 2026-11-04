from urllib.parse import quote

from django.db import models


class Consulta(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        RESPONDIDA = "respondida", "Respondida"
        ARCHIVADA = "archivada", "Archivada"

    nombre = models.CharField(max_length=100)
    email = models.EmailField("correo electrónico", blank=True)
    telefono = models.CharField("teléfono", max_length=20, blank=True)
    mensaje = models.TextField(max_length=1000)
    servicio = models.ForeignKey(
        "servicios.Servicio",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="consultas",
    )
    estado = models.CharField(
        max_length=12, choices=Estado.choices, default=Estado.PENDIENTE
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.nombre} ({self.creado:%d/%m/%Y %H:%M})"

    def texto_whatsapp(self):
        partes = [f"Hola, soy {self.nombre}."]
        if self.servicio:
            partes.append(f"Servicio: {self.servicio.nombre}.")
        partes.append(f"Mi consulta: {self.mensaje}")
        return " ".join(partes)

    def enlace_whatsapp(self, numero):
        if not numero:
            return ""
        return f"https://wa.me/{numero}?text={quote(self.texto_whatsapp())}"

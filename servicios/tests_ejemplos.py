from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Servicio


class EjemplosTests(TestCase):
    def test_carga_y_portada(self):
        get_user_model().objects.create_superuser("jefe", password="x12345678abc")
        call_command("cargar_ejemplos")
        n = Servicio.objects.count()
        self.assertGreater(n, 15)
        call_command("cargar_ejemplos")  # no duplica
        self.assertEqual(Servicio.objects.count(), n)
        r = self.client.get(reverse("servicios:publico"))
        self.assertContains(r, "Calzado y accesorios")
        self.assertContains(r, "Consultar precio")
        self.assertContains(r, "Tu campera de cuero")

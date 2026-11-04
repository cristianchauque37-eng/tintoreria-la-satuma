from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from negocio.models import Negocio
from servicios.models import Servicio

from .models import Consulta


class ConsultaTests(TestCase):
    def setUp(self):
        u = get_user_model().objects.create_user("admin", password="x12345678abc")
        self.servicio = Servicio.objects.create(
            nombre="Campera", precio=1000, creado_por=u, actualizado_por=u
        )
        n = Negocio.obtener()
        n.whatsapp = "5493874215609"
        n.save()

    def datos(self, **extra):
        d = {"nombre": "Ana", "mensaje": "¿Cuánto tarda?", "telefono": "3875000000"}
        d.update(extra)
        return d

    def test_formulario_es_publico(self):
        self.assertEqual(self.client.get(reverse("consultas:nueva")).status_code, 200)

    def test_consulta_valida_se_guarda_pendiente(self):
        r = self.client.post(
            reverse("consultas:nueva"), self.datos(servicio=self.servicio.pk)
        )
        self.assertRedirects(r, reverse("consultas:enviada"))
        c = Consulta.objects.get()
        self.assertEqual(c.estado, "pendiente")
        self.assertEqual(c.servicio, self.servicio)
        self.assertIsNotNone(c.creado)

    def test_sin_contacto_no_se_guarda(self):
        r = self.client.post(reverse("consultas:nueva"), self.datos(telefono=""))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "correo electrónico o un teléfono")
        self.assertEqual(Consulta.objects.count(), 0)

    def test_confirmacion_con_enlace_whatsapp(self):
        self.client.post(reverse("consultas:nueva"), self.datos())
        r = self.client.get(reverse("consultas:enviada"))
        self.assertContains(r, "https://wa.me/5493874215609?text=")
        self.assertContains(r, "Ana")

    def test_confirmacion_sin_envio_previo_redirige(self):
        r = self.client.get(reverse("consultas:enviada"))
        self.assertRedirects(r, reverse("consultas:nueva"))

    def test_servicio_inactivo_no_se_ofrece(self):
        self.servicio.activo = False
        self.servicio.save()
        r = self.client.post(
            reverse("consultas:nueva"), self.datos(servicio=self.servicio.pk)
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Consulta.objects.count(), 0)


class GestionConsultasTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            "jefe", password="x12345678abc"
        )
        self.consulta = Consulta.objects.create(
            nombre="Luis", telefono="1", mensaje="Hola"
        )

    def test_visitante_no_accede(self):
        r = self.client.get(reverse("consultas:gestion"))
        self.assertNotEqual(r.status_code, 200)

    def test_admin_ve_lista(self):
        self.client.force_login(self.admin)
        r = self.client.get(reverse("consultas:gestion"))
        self.assertContains(r, "Luis")

    def test_admin_cambia_estado(self):
        self.client.force_login(self.admin)
        self.client.post(
            reverse("consultas:estado", args=[self.consulta.pk]),
            {"estado": "respondida"},
        )
        self.consulta.refresh_from_db()
        self.assertEqual(self.consulta.estado, "respondida")

    def test_estado_invalido_se_ignora(self):
        self.client.force_login(self.admin)
        self.client.post(
            reverse("consultas:estado", args=[self.consulta.pk]), {"estado": "xx"}
        )
        self.consulta.refresh_from_db()
        self.assertEqual(self.consulta.estado, "pendiente")

    def test_filtro_por_estado(self):
        self.client.force_login(self.admin)
        r = self.client.get(reverse("consultas:gestion") + "?estado=archivada")
        self.assertNotContains(r, "Luis")


class ReporteTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            "jefe", password="x12345678abc"
        )
        u = self.admin
        self.s = Servicio.objects.create(
            nombre="Campera", precio=1, creado_por=u, actualizado_por=u
        )
        Consulta.objects.create(nombre="A", telefono="1", mensaje="m", servicio=self.s)
        Consulta.objects.create(
            nombre="B", telefono="1", mensaje="m", estado="respondida"
        )
        self.client.force_login(self.admin)
        from django.utils import timezone

        self.hoy = timezone.localdate().isoformat()

    def test_reporte_totales(self):
        r = self.client.get(
            reverse("consultas:reporte"), {"desde": self.hoy, "hasta": self.hoy}
        )
        self.assertEqual(r.context["total"], 2)
        self.assertEqual(dict(r.context["por_estado"])["Pendiente"], 1)
        self.assertEqual(r.context["sin_servicio"], 1)
        self.assertEqual(r.context["por_servicio"][0]["total"], 1)

    def test_reporte_filtra_estado(self):
        r = self.client.get(
            reverse("consultas:reporte"),
            {"desde": self.hoy, "hasta": self.hoy, "estado": "respondida"},
        )
        self.assertEqual(r.context["total"], 1)

    def test_periodo_invalido(self):
        r = self.client.get(
            reverse("consultas:reporte"), {"desde": "2026-12-01", "hasta": "2026-01-01"}
        )
        self.assertNotIn("generado", r.context)

    def test_visitante_no_accede(self):
        self.client.logout()
        r = self.client.get(reverse("consultas:reporte"))
        self.assertNotEqual(r.status_code, 200)


class InicioAdminTests(TestCase):
    def test_inicio_admin_muestra_resumen(self):
        admin = get_user_model().objects.create_superuser("jefe", password="x12345678abc")
        Consulta.objects.create(nombre="Zoe", telefono="1", mensaje="m")
        self.client.force_login(admin)
        r = self.client.get(reverse("inicio:home"))
        self.assertContains(r, "Consultas pendientes")
        self.assertContains(r, "Zoe")
        self.assertNotContains(r, "Catálogo")

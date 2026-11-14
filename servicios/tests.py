import io
import os
import shutil
import tempfile
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Servicio

Usuario = get_user_model()

# Mismas condiciones de prueba que el resto de la suite: sin redirección a HTTPS
# y sin depender de los archivos estáticos compilados.
AJUSTES = dict(
    SECURE_SSL_REDIRECT=False,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)


def crear_admin(nombre="jefe"):
    return Usuario.objects.create_superuser(
        nombre, f"{nombre}@example.test", "Temporal-segura-298!"
    )


def crear_servicio(admin, **extra):
    datos = {
        "nombre": "Campera de cuero",
        "precio": Decimal("15000"),
        "creado_por": admin,
        "actualizado_por": admin,
    }
    datos.update(extra)
    return Servicio.objects.create(**datos)


def png_de_bytes(ancho=40, alto=40, ruido=False):
    """Genera un PNG válido. Con ruido=True pesa más de 3 MB."""
    from PIL import Image

    if ruido:
        imagen = Image.frombytes("RGB", (ancho, alto), os.urandom(ancho * alto * 3))
    else:
        imagen = Image.new("RGB", (ancho, alto), (200, 30, 30))
    salida = io.BytesIO()
    imagen.save(salida, format="PNG")
    return salida.getvalue()


@override_settings(**AJUSTES)
class ModeloServicioTests(TestCase):
    def setUp(self):
        self.admin = crear_admin()

    def test_se_muestra_por_su_nombre(self):
        self.assertEqual(str(crear_servicio(self.admin)), "Campera de cuero")

    def test_nuevo_servicio_queda_activo_y_en_tintoreria(self):
        servicio = crear_servicio(self.admin)
        self.assertTrue(servicio.activo)
        self.assertEqual(servicio.categoria, Servicio.Categoria.TINTORERIA)

    def test_se_ordenan_por_nombre(self):
        crear_servicio(self.admin, nombre="Zapatos")
        crear_servicio(self.admin, nombre="Abrigo")
        nombres = list(Servicio.objects.values_list("nombre", flat=True))
        self.assertEqual(nombres, ["Abrigo", "Zapatos"])

    def test_la_base_rechaza_precios_negativos(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            crear_servicio(self.admin, precio=Decimal("-1"))

    def test_la_base_rechaza_nombres_repetidos_sin_distinguir_mayusculas(self):
        crear_servicio(self.admin, nombre="Campera")
        with self.assertRaises(IntegrityError), transaction.atomic():
            crear_servicio(self.admin, nombre="CAMPERA")

    def test_no_se_puede_borrar_al_administrador_que_creo_un_servicio(self):
        from django.db.models import ProtectedError

        crear_servicio(self.admin)
        with self.assertRaises(ProtectedError):
            self.admin.delete()


@override_settings(**AJUSTES)
class PaginasPublicasTests(TestCase):
    def setUp(self):
        self.admin = crear_admin()

    def test_portada_y_catalogo_se_ven_sin_iniciar_sesion(self):
        for nombre in ("servicios:publico", "servicios:catalogo"):
            with self.subTest(pagina=nombre):
                self.assertEqual(self.client.get(reverse(nombre)).status_code, 200)

    def test_solo_se_muestran_los_servicios_activos(self):
        crear_servicio(self.admin, nombre="Limpieza de campera")
        crear_servicio(self.admin, nombre="Servicio retirado", activo=False)
        respuesta = self.client.get(reverse("servicios:catalogo"))
        self.assertContains(respuesta, "Limpieza de campera")
        self.assertNotContains(respuesta, "Servicio retirado")

    def test_los_servicios_se_agrupan_por_categoria(self):
        crear_servicio(self.admin, nombre="Taco de zapato", categoria="calzado")
        crear_servicio(self.admin, nombre="Lavado de acolchado", categoria="lavanderia")
        respuesta = self.client.get(reverse("servicios:catalogo"))
        grupos = [nombre for nombre, _ in respuesta.context["grupos"]]
        # Respeta el orden de las categorías y omite las que no tienen servicios.
        self.assertEqual(grupos, ["Calzado y accesorios", "Lavandería"])

    def test_precio_en_cero_muestra_consultar_precio(self):
        crear_servicio(self.admin, nombre="Tapizado", precio=Decimal("0"))
        crear_servicio(self.admin, nombre="Campera", precio=Decimal("15000"))
        respuesta = self.client.get(reverse("servicios:catalogo"))
        self.assertContains(respuesta, "Consultar precio")
        self.assertContains(respuesta, "$ 15.000")

    def test_sin_servicios_muestra_un_aviso(self):
        respuesta = self.client.get(reverse("servicios:catalogo"))
        self.assertContains(respuesta, "Todavía no hay servicios cargados")

    def test_cada_servicio_enlaza_al_formulario_de_consulta(self):
        servicio = crear_servicio(self.admin)
        respuesta = self.client.get(reverse("servicios:catalogo"))
        self.assertContains(
            respuesta, f"{reverse('consultas:nueva')}?servicio={servicio.pk}"
        )


@override_settings(**AJUSTES)
class AccesoGestionTests(TestCase):
    def setUp(self):
        self.admin = crear_admin()
        self.servicio = crear_servicio(self.admin)
        self.operador = Usuario.objects.create_user(
            "operador", "operador@example.test", "Temporal-segura-298!"
        )
        self.operador.estado = "aprobado"
        self.operador.is_active = True
        self.operador.save()
        self.urls = [
            reverse("servicios:gestion"),
            reverse("servicios:crear"),
            reverse("servicios:editar", args=[self.servicio.pk]),
        ]

    def test_visitante_es_enviado_a_iniciar_sesion(self):
        for url in self.urls:
            with self.subTest(url=url):
                respuesta = self.client.get(url)
                self.assertEqual(respuesta.status_code, 302)
                self.assertIn(reverse("cuentas:login"), respuesta.url)

    def test_usuario_que_no_es_administrador_recibe_403(self):
        self.client.force_login(self.operador)
        for url in self.urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_visitante_no_puede_dar_de_baja_un_servicio(self):
        self.client.post(reverse("servicios:estado", args=[self.servicio.pk]))
        self.servicio.refresh_from_db()
        self.assertTrue(self.servicio.activo)

    def test_usuario_que_no_es_administrador_no_puede_dar_de_baja(self):
        self.client.force_login(self.operador)
        respuesta = self.client.post(
            reverse("servicios:estado", args=[self.servicio.pk])
        )
        self.assertEqual(respuesta.status_code, 403)
        self.servicio.refresh_from_db()
        self.assertTrue(self.servicio.activo)


@override_settings(**AJUSTES)
class GestionServiciosTests(TestCase):
    def setUp(self):
        self.admin = crear_admin()
        self.client.force_login(self.admin)
        self.carpeta = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.carpeta, ignore_errors=True)

    def datos(self, **extra):
        d = {
            "nombre": "Limpieza de campera",
            "categoria": "tintoreria",
            "descripcion": "Limpieza en seco de cuero.",
            "precio": "15000",
            "activo": "on",
        }
        d.update(extra)
        return d

    def test_el_listado_muestra_activos_e_inactivos(self):
        crear_servicio(self.admin, nombre="Servicio activo")
        crear_servicio(self.admin, nombre="Servicio de baja", activo=False)
        respuesta = self.client.get(reverse("servicios:gestion"))
        self.assertContains(respuesta, "Servicio activo")
        self.assertContains(respuesta, "Servicio de baja")

    def test_buscar_por_nombre_o_descripcion(self):
        crear_servicio(self.admin, nombre="Campera", descripcion="Gamuza")
        crear_servicio(self.admin, nombre="Zapatos", descripcion="Nobuk")
        por_nombre = self.client.get(reverse("servicios:gestion") + "?q=campe")
        self.assertContains(por_nombre, "Campera")
        self.assertNotContains(por_nombre, "Zapatos")
        por_descripcion = self.client.get(reverse("servicios:gestion") + "?q=nobuk")
        self.assertContains(por_descripcion, "Zapatos")
        self.assertNotContains(por_descripcion, "Campera")

    def test_crear_guarda_quien_lo_cargo(self):
        respuesta = self.client.post(reverse("servicios:crear"), self.datos())
        self.assertRedirects(respuesta, reverse("servicios:gestion"))
        servicio = Servicio.objects.get()
        self.assertEqual(servicio.precio, Decimal("15000"))
        self.assertEqual(servicio.creado_por, self.admin)
        self.assertEqual(servicio.actualizado_por, self.admin)

    def test_nombre_repetido_no_se_guarda_aunque_cambien_las_mayusculas(self):
        crear_servicio(self.admin, nombre="Campera")
        respuesta = self.client.post(
            reverse("servicios:crear"), self.datos(nombre="  campera ")
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Ya existe un servicio con ese nombre.")
        self.assertEqual(Servicio.objects.count(), 1)

    def test_precio_negativo_no_se_guarda(self):
        respuesta = self.client.post(
            reverse("servicios:crear"), self.datos(precio="-5")
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Servicio.objects.count(), 0)

    def test_nombre_y_precio_son_obligatorios(self):
        respuesta = self.client.post(
            reverse("servicios:crear"), self.datos(nombre="", precio="")
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Servicio.objects.count(), 0)

    def test_editar_cambia_actualizado_por_y_conserva_al_creador(self):
        servicio = crear_servicio(self.admin)
        otro = crear_admin("otro")
        self.client.force_login(otro)
        respuesta = self.client.post(
            reverse("servicios:editar", args=[servicio.pk]),
            self.datos(nombre="Campera de gamuza", precio="18000"),
        )
        self.assertRedirects(respuesta, reverse("servicios:gestion"))
        servicio.refresh_from_db()
        self.assertEqual(servicio.nombre, "Campera de gamuza")
        self.assertEqual(servicio.precio, Decimal("18000"))
        self.assertEqual(servicio.creado_por, self.admin)
        self.assertEqual(servicio.actualizado_por, otro)

    def test_editar_permite_conservar_el_mismo_nombre(self):
        servicio = crear_servicio(self.admin, nombre="Campera")
        respuesta = self.client.post(
            reverse("servicios:editar", args=[servicio.pk]),
            self.datos(nombre="Campera", precio="16000"),
        )
        self.assertRedirects(respuesta, reverse("servicios:gestion"))

    def test_dar_de_baja_y_reactivar_sin_borrar_el_registro(self):
        servicio = crear_servicio(self.admin)
        url = reverse("servicios:estado", args=[servicio.pk])
        self.client.post(url)
        servicio.refresh_from_db()
        self.assertFalse(servicio.activo)
        self.assertEqual(Servicio.objects.count(), 1)
        self.client.post(url)
        servicio.refresh_from_db()
        self.assertTrue(servicio.activo)

    def test_un_servicio_dado_de_baja_deja_de_verse_en_el_catalogo(self):
        servicio = crear_servicio(self.admin, nombre="Servicio visible")
        self.client.post(reverse("servicios:estado", args=[servicio.pk]))
        respuesta = self.client.get(reverse("servicios:catalogo"))
        self.assertNotContains(respuesta, "Servicio visible")

    def test_cambiar_estado_solo_acepta_post(self):
        servicio = crear_servicio(self.admin)
        respuesta = self.client.get(reverse("servicios:estado", args=[servicio.pk]))
        self.assertEqual(respuesta.status_code, 405)

    def test_editar_un_servicio_inexistente_da_404(self):
        self.assertEqual(
            self.client.get(reverse("servicios:editar", args=[999])).status_code, 404
        )

    def test_imagen_valida_se_guarda(self):
        with override_settings(MEDIA_ROOT=self.carpeta):
            foto = SimpleUploadedFile(
                "campera.png", png_de_bytes(), content_type="image/png"
            )
            respuesta = self.client.post(
                reverse("servicios:crear"), self.datos(imagen=foto)
            )
            self.assertRedirects(respuesta, reverse("servicios:gestion"))
            self.assertTrue(Servicio.objects.get().imagen.name.startswith("servicios/"))

    def test_imagen_de_mas_de_3_mb_se_rechaza(self):
        with override_settings(MEDIA_ROOT=self.carpeta):
            foto = SimpleUploadedFile(
                "pesada.png", png_de_bytes(1300, 1300, ruido=True), content_type="image/png"
            )
            self.assertGreater(foto.size, 3 * 1024 * 1024)
            respuesta = self.client.post(
                reverse("servicios:crear"), self.datos(imagen=foto)
            )
            self.assertEqual(respuesta.status_code, 200)
            self.assertContains(respuesta, "La imagen no puede superar los 3 MB.")
            self.assertEqual(Servicio.objects.count(), 0)

    def test_un_archivo_que_no_es_imagen_se_rechaza(self):
        with override_settings(MEDIA_ROOT=self.carpeta):
            falso = SimpleUploadedFile(
                "virus.png", b"esto no es una imagen", content_type="image/png"
            )
            respuesta = self.client.post(
                reverse("servicios:crear"), self.datos(imagen=falso)
            )
            self.assertEqual(respuesta.status_code, 200)
            self.assertEqual(Servicio.objects.count(), 0)

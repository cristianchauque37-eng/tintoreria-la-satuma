from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from .models import Usuario


@override_settings(
    SECURE_SSL_REDIRECT=False,
    STORAGES={
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        }
    },
)
class CuentasTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_superuser(
            "admin", "admin@example.test", "Temporal-segura-298!"
        )
        self.usuario = Usuario.objects.create_user(
            "alumna", "alumna@example.test", "Temporal-segura-298!"
        )


    def test_pendiente_no_ingresa(self):
        response = self.client.post(
            reverse("cuentas:login"),
            {"username": "alumna", "password": "Temporal-segura-298!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)




    def test_logout_requiere_post(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("cuentas:logout")).status_code, 405)

    def test_base_impide_activar_sin_aprobar(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Usuario.objects.filter(pk=self.usuario.pk).update(is_active=True)

    def test_deshabilitar_invalida_acceso_de_sesion(self):
        self.client.force_login(self.admin)
        Usuario.objects.filter(pk=self.admin.pk).update(is_active=False)
        self.assertEqual(self.client.get(reverse("inicio:home")).status_code, 302)

    def test_no_redireccion_abierta(self):
        response = self.client.post(
            reverse("cuentas:login"),
            {
                "username": "admin",
                "password": "Temporal-segura-298!",
                "next": "https://otro.example/",
            },
        )
        self.assertRedirects(response, reverse("inicio:home"))

    def test_bloqueo_tras_cinco_intentos(self):
        for intento in range(5):
            response = self.client.post(
                reverse("cuentas:login"),
                {"username": "admin", "password": "incorrecta"},
                HTTP_USER_AGENT=f"navegador-{intento}",
                REMOTE_ADDR=f"192.0.2.{intento+1}",
            )
        self.assertEqual(response.status_code, 429)
        self.assertContains(response, "Demasiados intentos", status_code=429)
        response = self.client.post(
            reverse("cuentas:login"),
            {"username": "admin", "password": "Temporal-segura-298!"},
        )
        self.assertEqual(response.status_code, 429)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_superusuario_creado_normaliza_identidad(self):
        user = Usuario.objects.create_superuser(
            "ADMIN2", "ADMIN2@example.test", "Temporal-segura-298!"
        )
        self.assertTrue(user.is_active)
        self.assertEqual(user.username, "admin2")

    @override_settings(SITE_NAME="Organización de ejemplo")
    def test_nombre_organizacion_en_login(self):
        self.assertContains(
            self.client.get(reverse("cuentas:login")), "Organización de ejemplo"
        )

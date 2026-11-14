from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import IntegrityError, transaction


class SoloAdministradorMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Permite el acceso solo al administrador (superusuario) con sesión iniciada."""

    def test_func(self):
        return self.request.user.is_superuser


class GuardadoSeguroMixin:
    """Guarda el formulario dentro de una transacción y avisa si no se pudo guardar."""

    def form_valid(self, form):
        try:
            with transaction.atomic():
                response = super().form_valid(form)
        except IntegrityError:
            form.add_error(
                None,
                "No se pudo guardar: otro registro usa esos datos o cambió una relación. Revisá e intentá de nuevo.",
            )
            return self.form_invalid(form)
        messages.success(self.request, "Cambios guardados.")
        return response

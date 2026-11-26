from django.contrib.auth.forms import AuthenticationForm


class AccesoForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "No pudimos iniciar sesión. Revisá tu usuario y contraseña.",
        "inactive": "La cuenta no está habilitada. Contactá al administrador.",
    }

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()

from django import forms

from servicios.models import Servicio

from .models import Consulta


class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ("nombre", "email", "telefono", "servicio", "mensaje")
        widgets = {"mensaje": forms.Textarea(attrs={"rows": 5})}
        help_texts = {
            "email": "Completá correo o teléfono para que podamos responderte.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["servicio"].queryset = Servicio.objects.filter(activo=True)
        self.fields["servicio"].required = False
        self.fields["servicio"].empty_label = "Sin servicio en particular"

    def clean(self):
        datos = super().clean()
        if not datos.get("email") and not (datos.get("telefono") or "").strip():
            raise forms.ValidationError(
                "Ingresá un correo electrónico o un teléfono para poder contactarte."
            )
        return datos

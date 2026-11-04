from django import forms

from servicios.models import Servicio

from .models import Consulta


class ReporteForm(forms.Form):
    desde = forms.DateField(
        label="Desde", widget=forms.DateInput(attrs={"type": "date"})
    )
    hasta = forms.DateField(
        label="Hasta", widget=forms.DateInput(attrs={"type": "date"})
    )
    estado = forms.ChoiceField(
        label="Estado", required=False,
        choices=[("", "Todos los estados")] + Consulta.Estado.choices,
    )

    def clean(self):
        datos = super().clean()
        desde, hasta = datos.get("desde"), datos.get("hasta")
        if desde and hasta and desde > hasta:
            raise forms.ValidationError(
                "La fecha desde no puede ser posterior a la fecha hasta."
            )
        return datos


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

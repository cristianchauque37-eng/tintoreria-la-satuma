from django import forms
from .models import Servicio


class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ("nombre", "descripcion", "precio", "activo")
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 4})}

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if (
            Servicio.objects.filter(nombre__iexact=nombre)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("Ya existe un servicio con ese nombre.")
        return nombre

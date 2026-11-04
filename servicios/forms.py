from django import forms
from .models import Servicio


class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ("nombre", "descripcion", "precio", "imagen", "activo")
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 4})}

    def clean_imagen(self):
        imagen = self.cleaned_data.get("imagen")
        if imagen and hasattr(imagen, "size") and imagen.size > 3 * 1024 * 1024:
            raise forms.ValidationError("La imagen no puede superar los 3 MB.")
        return imagen

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if (
            Servicio.objects.filter(nombre__iexact=nombre)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("Ya existe un servicio con ese nombre.")
        return nombre

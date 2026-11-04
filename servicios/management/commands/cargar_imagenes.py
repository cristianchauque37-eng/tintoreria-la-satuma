from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand

from servicios.models import Servicio

CARPETA = Path(__file__).resolve().parents[2] / "imagenes_ejemplo"

# Nombre del servicio -> archivo de imagen (fotos de Unsplash, uso libre).
IMAGENES = {
    "Campera de cuero": "01-campera-de-cuero.jpg",
    "Campera de gamuza": "02-campera-de-gamuza.jpg",
    "Campera de nobuk": "03-campera-de-nobuk.jpg",
    "Chaleco de cuero": "04-chaleco-de-cuero.jpg",
    "Pantalón de cuero": "05-pantalon-de-cuero.jpg",
    "Tapado o abrigo (sin piel)": "06-tapado-o-abrigo.jpg",
    "Botas de gamuza": "07-botas-de-gamuza.jpg",
    "Cartera o bolso de cuero": "08-cartera-o-bolso-de-cuero.jpg",
    "Cinturón de cuero": "09-cinturon-de-cuero.jpg",
    "Zapatos de nobuk": "10-zapatos-de-nobuk.jpg",
    "Cortinas": "11-cortinas.jpg",
    "Edredón": "12-edredon.jpg",
    "Manta o cubrecama": "13-manta-o-cubrecama.jpg",
    "Ropa de cama y sábanas": "14-ropa-de-cama-y-sabanas.jpg",
    "Combo 2 camperas": "15-combo-2-camperas.jpg",
    "Combo campera + cartera": "16-combo-campera-cartera.jpg",
    "Descuento por 3 prendas": "17-descuento-por-3-prendas.jpg",
    "Desodorizado de prendas": "18-desodorizado-de-prendas.jpg",
    "Eliminación de manchas": "19-eliminacion-de-manchas.jpg",
    "Impermeabilización": "20-impermeabilizacion.jpg",
}


class Command(BaseCommand):
    help = "Asigna las fotos de ejemplo a los servicios que todavía no tienen imagen."

    def add_arguments(self, parser):
        parser.add_argument(
            "--forzar", action="store_true", help="Reemplaza también las imágenes ya cargadas."
        )

    def handle(self, *args, **opciones):
        asignadas = 0
        for nombre, archivo in IMAGENES.items():
            servicio = Servicio.objects.filter(nombre__iexact=nombre).first()
            if servicio is None or (servicio.imagen and not opciones["forzar"]):
                continue
            with open(CARPETA / archivo, "rb") as f:
                servicio.imagen.save(archivo, File(f), save=True)
            asignadas += 1
        self.stdout.write(self.style.SUCCESS(f"Imágenes asignadas: {asignadas}"))

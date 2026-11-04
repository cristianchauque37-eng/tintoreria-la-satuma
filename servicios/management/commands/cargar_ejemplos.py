from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from servicios.models import Servicio

C = Servicio.Categoria

# Datos de EJEMPLO para el catálogo. Los precios son ficticios: el
# administrador los reemplaza desde el panel (Servicios).
EJEMPLOS = [
    (C.TINTORERIA, "Campera de cuero", "Limpieza en seco, hidratación y acabado del cuero.", 15000),
    (C.TINTORERIA, "Campera de gamuza", "Limpieza especial y cepillado para recuperar el pelo.", 16000),
    (C.TINTORERIA, "Campera de nobuk", "Limpieza en seco y protección del nobuk.", 16000),
    (C.TINTORERIA, "Chaleco de cuero", "Limpieza en seco y tratamiento del cuero.", 11000),
    (C.TINTORERIA, "Pantalón de cuero", "Limpieza en seco e hidratación, con cuidado de las costuras.", 13000),
    (C.TINTORERIA, "Tapado o abrigo (sin piel)", "Limpieza en seco y planchado profesional.", 12000),
    (C.CALZADO, "Botas de gamuza", "Limpieza y reavivado del pelo de la gamuza.", 9000),
    (C.CALZADO, "Zapatos de nobuk", "Limpieza en seco y protección contra manchas.", 8000),
    (C.CALZADO, "Cartera o bolso de cuero", "Limpieza, hidratación y renovación del color.", 10000),
    (C.CALZADO, "Cinturón de cuero", "Limpieza y acabado.", 4000),
    (C.LAVANDERIA, "Ropa de cama y sábanas", "Lavado, secado y doblado cuidadoso.", 7000),
    (C.LAVANDERIA, "Edredón", "Lavado especial y secado completo.", 12000),
    (C.LAVANDERIA, "Manta o cubrecama", "Lavado, secado y doblado.", 9000),
    (C.LAVANDERIA, "Cortinas", "Lavado y planchado. Consultar según el tamaño.", 0),
    (C.OFERTAS, "Combo 2 camperas", "Traé 2 camperas de cuero y obtené un descuento.", 27000),
    (C.OFERTAS, "Combo campera + cartera", "Limpieza de una campera y una cartera de cuero a precio especial.", 22000),
    (C.OFERTAS, "Descuento por 3 prendas", "Traé 3 prendas de cualquier categoría y pagá menos.", 0),
    (C.OTROS, "Eliminación de manchas", "Evaluamos la mancha sin cargo. El precio depende del caso.", 0),
    (C.OTROS, "Desodorizado de prendas", "Tratamiento para eliminar olores en cuero y gamuza.", 5000),
    (C.OTROS, "Impermeabilización", "Protección contra agua y manchas para cuero y gamuza.", 6000),
]


class Command(BaseCommand):
    help = "Carga servicios de ejemplo en el catálogo (no duplica los existentes)."

    def handle(self, *args, **opciones):
        admin = get_user_model().objects.filter(is_superuser=True).order_by("pk").first()
        if admin is None:
            raise CommandError("Primero creá el administrador (createsuperuser).")
        creados = 0
        for categoria, nombre, descripcion, precio in EJEMPLOS:
            _, nuevo = Servicio.objects.get_or_create(
                nombre__iexact=nombre,
                defaults={
                    "nombre": nombre,
                    "categoria": categoria,
                    "descripcion": descripcion,
                    "precio": precio,
                    "creado_por": admin,
                    "actualizado_por": admin,
                },
            )
            creados += nuevo
        self.stdout.write(self.style.SUCCESS(f"Servicios nuevos cargados: {creados}"))

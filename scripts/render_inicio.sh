#!/bin/sh
# Arranque en Render (plan gratuito: no hay terminal, así que todo se prepara acá).
set -e

# Render genera dos valores al azar; juntos superan los 50 caracteres que exige settings.py.
export DJANGO_SECRET_KEY="${DJANGO_SECRET_A}${DJANGO_SECRET_B}"
export DJANGO_ALLOWED_HOSTS="${RENDER_EXTERNAL_HOSTNAME}"
export DJANGO_CSRF_TRUSTED_ORIGINS="https://${RENDER_EXTERNAL_HOSTNAME}"

python manage.py migrate --noinput

# Crea el administrador la primera vez (usuario y clave vienen de las variables de entorno).
python manage.py shell -c "
import sys
from django.contrib.auth import get_user_model
sys.exit(0 if get_user_model().objects.filter(is_superuser=True).exists() else 1)
" || python manage.py createsuperuser --noinput

# Carga los servicios de ejemplo y sus fotos solo si la base está vacía.
python manage.py shell -c "
import sys
from servicios.models import Servicio
sys.exit(0 if Servicio.objects.exists() else 1)
" || python manage.py loaddata datos_ejemplo.json

# En el plan gratuito el disco se borra cada vez que el servicio se duerme o se reinicia,
# pero la base no: las fotos se vuelven a copiar en cada arranque.
python manage.py cargar_imagenes --forzar

exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-10000}" --workers 2 --access-logfile - --error-logfile -

# Tintorería La Satuma

Sistema web de gestión de consultas y servicios para una tintorería de Salta, especializada en cuero, gamuza y nobuk.

Proyecto de **Práctica Profesional II** · Tecnicatura Superior en Análisis de Sistemas en Computación · Instituto Superior del Milagro.

## Integrantes y roles

**Grupo 2**

| Integrante | Rol |
| --- | --- |
| Chauque, Cristian | Product Owner, Scrum Master y Development Team |
| Baldiviezo, Fredy | Development Team |
| Pachado, Julio | Development Team |
| Pachado, Sofía | Development Team |

Con un grupo de cuatro integrantes, los roles de Product Owner y Scrum Master los asumió un mismo integrante, tal como lo acordamos en el grupo.

## Qué incluye

- **Página pública:** portada, catálogo de servicios por categoría, formulario de consulta, WhatsApp y mapa.
- **Panel de administración:** servicios y categorías, consultas con su estado y datos del negocio.

## Tecnologías

Django 5.2 · PostgreSQL 17 · Docker · Gunicorn · Scrum

## Estructura del proyecto

    config/            Configuración de Django (settings, urls, wsgi).
    cuentas/           Modelo de usuario e inicio de sesión del administrador.
    servicios/         Servicios, categorías y catálogo público.
    consultas/         Consultas del visitante, derivación a WhatsApp y reportes.
    negocio/           Datos de contacto del negocio (dirección, horarios, WhatsApp).
    inicio/            Página de inicio del panel con los totales.
    templates/         Plantillas HTML, una carpeta por módulo.
    static/            Hojas de estilo, imágenes y archivos estáticos.
    scripts/           configurar.py (configuración local) y render_inicio.sh (arranque en Render).
    infra/             Configuración de Caddy para el servidor.
    datos_ejemplo.json Servicios de ejemplo para cargar la base.
    compose.yaml       Docker Compose para desarrollo.
    Dockerfile         Imagen de la aplicación.
    render.yaml        Despliegue en Render.

Cada módulo sigue la misma organización: `models.py`, `forms.py`, `views.py`, `urls.py`, `admin.py`, `tests.py` y `migrations/`.

## Cómo levantarlo

Con Docker Desktop abierto, en la carpeta del proyecto:

**Paso 1.** Generar la configuración:

    python scripts/configurar.py

**Paso 2.** Levantar el sistema:

    docker compose up -d --build

**Paso 3.** Crear el usuario administrador:

    docker compose exec web python manage.py createsuperuser

**Paso 4.** Cargar los servicios de ejemplo:

    docker compose exec web python manage.py loaddata datos_ejemplo.json

**Paso 5.** Cargar las fotos de los servicios:

    docker compose exec web python manage.py cargar_imagenes --forzar

**Paso 6.** Abrir en el navegador: http://localhost:8000

## Cómo ejecutar las pruebas

Con el sistema levantado, las pruebas automáticas se corren con:

    docker compose exec web python manage.py test

Son 62 pruebas y se ejecutan en una base de datos de prueba que Django crea y borra sola, así que no tocan los datos cargados.

Para correr las pruebas de un solo módulo:

    docker compose exec web python manage.py test servicios

Para ver el detalle de cada prueba:

    docker compose exec web python manage.py test -v 2

## Publicar en Render

El archivo `render.yaml` es un Blueprint: crea la base de datos PostgreSQL y el servicio web, los dos en el plan gratuito.

**Paso 1.** Subir el repositorio a GitHub.

**Paso 2.** En Render, elegir **New → Blueprint** y seleccionar el repositorio. Render lee `render.yaml`.

**Paso 3.** Cargar la contraseña del administrador cuando Render la pida, en la variable `DJANGO_SUPERUSER_PASSWORD`. Es la única que no se genera sola.

**Paso 4.** Confirmar el despliegue. En cada arranque, `scripts/render_inicio.sh` aplica las migraciones, crea o actualiza el administrador, carga los servicios de ejemplo si la base está vacía y copia las fotos.

**Paso 5.** Entrar a la dirección que da Render y al panel en `/cuentas/ingresar/`.

Las demás variables (`DJANGO_SECRET_A`, `DJANGO_SECRET_B` y los datos de la base) las genera Render a partir del Blueprint.

**Límites del plan gratuito.** El servicio se duerme a los 15 minutos sin visitas y el primer ingreso tarda cerca de un minuto en responder. El disco se borra en cada reinicio, por eso las fotos se vuelven a copiar al arrancar. La base de datos gratuita vence a los 30 días de creada.

## Nota

Los servicios, precios y fotos son datos de ejemplo. Se usó IA (Claude) como apoyo en el desarrollo.

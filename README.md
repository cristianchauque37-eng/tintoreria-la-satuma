# Tintorería La Satuma

Sistema web de gestión de consultas y servicios para una tintorería de Salta, especializada en cuero, gamuza y nobuk.

Proyecto de **Práctica Profesional II** · Tecnicatura Superior en Análisis de Sistemas en Computación · Instituto Superior del Milagro.

**Grupo 2:** Baldiviezo Fredy · Chauque Cristian · Pachado Julio · Pachado Sofía

## Qué incluye

- **Página pública:** portada, catálogo de servicios por categoría, formulario de consulta, WhatsApp y mapa.
- **Panel de administración:** servicios y categorías, consultas con su estado, datos del negocio y solicitudes de acceso.

## Tecnologías

Django · PostgreSQL · Docker · Scrum

## Módulos

`servicios` · `consultas` · `negocio` · `cuentas` · `inicio`

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

## Nota

Los servicios, precios y fotos son datos de ejemplo. Se usó IA (Claude) como apoyo en el desarrollo.

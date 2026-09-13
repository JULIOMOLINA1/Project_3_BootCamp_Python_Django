# API REST - Albergue de Animales (BootCamp Python · Caso 5)

Proyecto **Django + Django REST Framework** para registrar el ciclo completo de un animal en un
albergue: **ingreso → ubicación temporal (traslados) → atención veterinaria → solicitudes de
adopción → adopción → seguimiento post adopción**. La base de datos conserva el historial del
animal aunque cambie de albergue, reciba varias atenciones o existan múltiples solicitudes antes
de concretar una adopción.

Cuando un animal es adoptado, su `estado_actual` cambia automáticamente a **Adoptado** y queda
registrado en el historial completo.

---

## 1. Tecnologías

| Herramienta | Versión |
|---|---|
| Python | 3.14 |
| Django (LTS) | 5.2.17 |
| Django REST Framework | 3.16.1 |
| djangorestframework-simplejwt | 5.5.1 |
| drf-spectacular (Swagger/Redoc) | 0.30.0 |
| PostgreSQL (psycopg 3) | Neon / Render |
| Whitenoise | 6.12 |
| gunicorn | 26.2 |

## 2. Estructura

```
.
├── config/                # settings, urls, views (portada), wsgi, asgi
├── albergues/             # Albergue / views / serializers
├── animales/              # Animal, Ingreso, UbicacionTemporal
├── veterinaria/           # AtencionVeterinaria
├── adopciones/            # Adoptante, SolicitudAdopcion, Adopcion, SeguimientoAdopcion
├── templates/             # welcome.html (portada con acceso a Swagger)
├── images/                # DIAGRAMA.png (modelo de base de datos)
├── scripts/smoke_caso5.py # smoke test (Caso 5 + validaciones)
├── manage.py
├── requirements.txt
├── build.sh               # build para Render
├── Procfile               # gunicorn para Render
├── .env.example
└── .env                   # credenciales locales (NO subir)
```

## 3. Endpoints

| Método / Ruta | Descripción |
|---|---|
| `GET /` | **Portada** con acceso rápido a Swagger |
| `POST /api/token/` | Login JWT (usuario/contraseña) |
| `POST /api/token/refresh/` | Renovar access token |
| `GET /api/docs/` | **Swagger UI** (público) |
| `GET /api/redoc/` | Redoc |
| `GET /api/schema/` | OpenAPI schema (YAML) |
| `GET /api/schema/?format=json` | OpenAPI schema (JSON) |
| `GET/POST /api/albergues/`, `/api/animales/`, `/api/ingresos/`, `/api/ubicaciones/`, `/api/atenciones/`, `/api/adoptantes/`, `/api/solicitudes/`, `/api/adopciones/`, `/api/seguimientos/` | CRUD completo (ModelViewSet) |
| `GET/PUT/PATCH/DELETE /api/<recurso>/{id}/` | Detalle / edición / borrado |

**Permisos:** lectura pública; creación/edición/borrado requieren JWT `Authorization: Bearer <token>`.

## 4. Autenticación (JWT)

1. Obtén tu token con `POST /api/token/` (usa un usuario creado con `createsuperuser`):

   ```bash
   curl -X POST https://localhost:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "tu_contraseña"}'
   ```

2. La respuesta devuelve `access` y `refresh`. Envía el `access` en cada petición de escritura:

   ```bash
   curl -X POST https://localhost:8000/api/animales/ \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
     -H "Content-Type: application/json" \
     -d '{"nombre": "Luna", "especie": "Gato", "raza": "Criollo", "sexo": "Hembra"}'
   ```

## 5. Modelo de la base de datos

La base de datos relacional está compuesta por **9 tablas**. `Animal`, `Albergue` y
`SolicitudAdopcion` son entidades centrales y su historial está protegido (`PROTECT`).

![Diagrama entidad-relación](images/DIAGRAMA.png)

### Tablas y relaciones

| Tabla | Campos principales | Relaciones |
|---|---|---|
| `albergues` | `id`, `nombre`, `direccion`, `telefono` | Padres del historial de ubicación e ingreso |
| `animales` | `id`, `nombre`, `especie`, `raza`, `edad_aproximada`, `sexo`, `estado_actual`, `created_at` | Principal; historial en las demás tablas |
| `ingresos` | `id`, `fecha_ingreso`, `motivo_ingreso` | FK `animal` y `albergue_inicial` (PROTECT) |
| `ubicaciones_temporales` | `id`, `fecha_entrada`, `fecha_salida`, `observaciones` | FK `animal` y `albergue` (PROTECT); `fecha_salida >= fecha_entrada` |
| `atenciones_veterinarias` | `id`, `fecha_atencion`, `diagnostico`, `tratamiento`, `veterinario_responsable`, `costo` | FK `animal` (PROTECT); `costo >= 0` |
| `adoptantes` | `id`, `nombre`, `telefono`, `email` (único), `direccion` | Hacen solicitudes de adopción |
| `solicitudes_adopcion` | `id`, `fecha_solicitud`, `estado` (Pendiente/Aprobada/Rechazada), `comentarios` | FK `animal` y `adoptante` (PROTECT); varias por animal |
| `adopciones` | `id`, `fecha_adopcion` | **OneToOne** con `solicitud_adopcion` (solo Aprobada) |
| `seguimientos_adopcion` | `id`, `fecha_seguimiento`, `observaciones` | FK `adopcion` (PROTECT) |

**Flujo:** un animal genera uno o varios `ingresos`/`ubicaciones_temporales`/`atenciones_veterinarias`/
`solicitudes_adopcion`; cuando una solicitud pasa a **Aprobada**, se crea su `adopcion` (una por
animal) que dispara el cambio de `estado_actual` a `Adoptado`, y sobre esa adopción se registran
los `seguimientos_adopcion`.

## 6. Ejecución local

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configurar entorno
Copy-Item .env.example .env   # y rellenar SECRET_KEY, DEBUG=True, DATABASE_URL

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abrir `http://127.0.0.1:8000/` para la portada o `http://127.0.0.1:8000/api/docs/`.

Sin `DATABASE_URL` en `.env` el proyecto usa SQLite automáticamente (no apto para producción).

### Smoke test (Caso 5)

```powershell
Get-Content scripts\smoke_caso5.py -Raw | python manage.py shell
```

Valida el flujo completo, las validaciones y la protección del historial (`PROTECT`).

## 7. Despliegue en Render

1. **Sube el repositorio a GitHub** (sin `.env`; usa variables de entorno).
2. En Render: **New → Web Service** y conecta el repo.
3. Crea una base **PostgreSQL** (Render ofrece una; o usa Neon) y copia su `DATABASE_URL` interna.
4. Ambiente (Variables):
   | Variable | Valor |
   |---|---|
   | `SECRET_KEY` | clave aleatoria larga |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `uralic-website-tu-nombre.onrender.com,tu-dominio.com` |
   | `DATABASE_URL` | `postgresql://...?sslmode=require` (de Render/Neon) |
   | `CORS_ALLOWED_ORIGINS` | URL de tu frontend (p. ej. `https://mi-front.web.app`) |
   | `PYTHON_VERSION` | `3.14.5` |
5. **Build command** → `bash build.sh` (instala dependencias, copia estáticos y aplica migraciones)
6. **Start command** → `gunicorn config.wsgi:application`
7. Deploy. La migración corre en cada build automáticamente.

Por defecto `ALLOWED_HOSTS` ya acepta cualquier subdominio `*.onrender.com`, así que el host
autogenerado funciona incluso sin configurarlo.

## 8. Despliegue (producción · en vivo)

El proyecto está desplegado en **Render** con base de datos **PostgreSQL (Neon)**:

| Recurso | URL |
|---|---|
| **Aplicación** | https://project-3-bootcamp-python-django.onrender.com/ |
| **Swagger UI** | https://project-3-bootcamp-python-django.onrender.com/api/docs/ |
| **Redoc** | https://project-3-bootcamp-python-django.onrender.com/api/redoc/ |
| **Schema OpenAPI (JSON)** | https://project-3-bootcamp-python-django.onrender.com/api/schema/?format=json |
| **API animales** | https://project-3-bootcamp-python-django.onrender.com/api/animales/ |

Configuración en producción: `DEBUG=False`, `SECRET_KEY` por variable de entorno,
`DATABASE_URL` apuntando a Neon (PostgreSQL) y `ALLOWED_HOSTS *.onrender.com`.

> **Nota de seguridad:** las credenciales reales (usuario/contraseña del superusuario y
> `DATABASE_URL`) viven solo en las variables de entorno de Render y en el `.env` local.
> **Nunca se suben al repositorio.**

## 9. Decisiones de diseño (Caso 5)

- **Nombres de tablas (PostgreSQL)**: `albergues`, `animales`, `ingresos`,
  `ubicaciones_temporales`, `atenciones_veterinarias`, `adoptantes`,
  `solicitudes_adopcion`, `adopciones`, `seguimientos_adopcion` (definidos con
  `db_table` en cada `Meta`).
- **Historial inmutable**: `on_delete=PROTECT` en toda FK que apunte a `Animal`, `Albergue` y
  `SolicitudAdopcion` → no se puede borrar un animal/albergue con historial registrado.
- **Múltiples solicitudes**: `SolicitudAdopcion` es FK a `animal` (varias por animal); solo una
  pasada a `Aprobada` puede concretar `Adopcion` (OneToOne sobre la solicitud).
- **Estado `Adoptado`**: se actualiza automáticamente al crear la `Adopcion` (transacción).
- **Restricciones a nivel de BD** (además de los serializers):
  - `ubicacion.fecha_salida >= fecha_entrada` (o NULL)
  - `atencion.costo >= 0`
  - `animal.edad_aproximada >= 0`
- **Validaciones en serializers**: fecha futura (ingreso/atención/solicitud), email único
  (case-insensitive) para adoptantes, adopción no anterior a la solicitud, seguimiento no
  anterior a la adopción, una sola adopción por animal.
- **Historial del animal**: `GET /api/animales/{id}/` devuelve anidados sus ingresos,
  ubicaciones (traslados), atenciones y solicitudes con su resultado.
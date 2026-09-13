# API REST - Albergue de Animales (BootCamp Python · Caso 5)

Proyecto **Django + Django REST Framework** para registrar el ciclo completo de un animal en un
albergue: **ingreso → ubicación temporal (traslados) → atención veterinaria → solicitudes de
adopción → adopción → seguimiento post adopción**. La base de datos conserva el historial del
animal aunque cambie de albergue, reciba varias atenciones o existan múltiples solicitudes antes
de concretar una adopción.

---

## 1. Tecnologías

| Herramienta | Versión |
|---|---|
| Python | 3.14 |
| Django (LTS) | 5.2.17 |
| Django REST Framework | 3.16.1 |
| djangorestframework-simplejwt | 5.5.1 |
| drf-spectacular (Swagger) | 0.30.0 |
| PostgreSQL (psycopg 3) | Neon / Render |
| Whitenoise | 6.12 |
| gunicorn | 26.2 |

## 2. Estructura

```
.
├── config/                # settings, urls, wsgi, asgi
├── albergues/             # Albergue
├── animales/              # Animal, Ingreso, UbicacionTemporal
├── veterinaria/           # AtencionVeterinaria
├── adopciones/            # Adoptante, SolicitudAdopcion, Adopcion, SeguimientoAdopcion
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
| `POST /api/token/` | Login JWT (usuario/contraseña) |
| `POST /api/token/refresh/` | Renovar access token |
| `GET /api/docs/` | **Swagger UI** (público) |
| `GET /api/redoc/` | Redoc |
| `GET /api/schema/` | OpenAPI schema |
| `GET/POST /api/albergues/`, `/api/animales/`, `/api/ingresos/`, `/api/ubicaciones/`, `/api/atenciones/`, `/api/adoptantes/`, `/api/solicitudes/`, `/api/adopciones/`, `/api/seguimientos/` | CRUD completo (ModelViewSet) |
| `GET/PUT/PATCH/DELETE /api/<recurso>/{id}/` | Detalle / edición / borrado |

**Permisos:** lectura pública; creación/edición/borrado requieren JWT `Authorization: Bearer <token>`.

## 4. Ejecución local

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

Abrir `http://127.0.0.1:8000/api/docs/`.

Sin `DATABASE_URL` en `.env` el proyecto usa SQLite automáticamente (no apto para producción).

### Smoke test (Caso 5)

```powershell
Get-Content scripts\smoke_caso5.py -Raw | python manage.py shell
```

Valida el flujo completo, las validaciones y la protección del historial (`PROTECT`).

## 5. Despliegue en Render

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
5. **Build command** → `./build.sh` (instala, copia estáticos y aplica migraciones)
   > Si usas Windows y no guardaste el permiso de ejecución, en Render usa `bash build.sh`.
6. **Start command** → `gunicorn config.wsgi:application`
7. Deploy. La migración corre en cada build automáticamente.

Por defecto `ALLOWED_HOSTS` ya acepta cualquier subdominio `*.onrender.com`, así que el host
autogenerado funciona incluso sin configurarlo.

## 6. Decisiones de diseño (Caso 5)

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
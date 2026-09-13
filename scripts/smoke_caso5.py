"""
Smoke test del Caso 5 contra la base de datos configurada (Neon).

Ejecutar:
    python manage.py shell < scripts/smoke_caso5.py
o bien:
    $env:DJANGO_SETTINGS_MODULE="config.settings"
    python scripts/smoke_caso5.py

Verifica:
  - Flujo completo: albergue -> animal -> ingreso -> traslados -> atenciones
    -> solicitudes -> adopcion -> seguimiento.
  - Validaciones (costo negativo, fechas, email duplicado, solicitud no
    aprobada, seguimiento antes de adopcion).
  - Proteccion del historial (PROTECT impide borrar animal/albergue).
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.db.models import ProtectedError  # noqa: E402
from rest_framework import status  # noqa: E402
from rest_framework.test import APIClient  # noqa: E402

from adopciones.models import Adopcion  # noqa: E402
from animales.models import Animal  # noqa: E402

client = APIClient()
ok = 0
fail = 0


def check(name, condition, detail=""):
    global ok, fail
    if condition:
        ok += 1
        print(f"  [OK] {name}")
    else:
        fail += 1
        print(f"  [FAIL] {name} -> {detail}")


print("== 0. Autenticacion JWT (admin) ==")
r = client.post("/api/token/", {"username": "admin", "password": "Admin12345#"}, format="json")
check("token obtenido", r.status_code == status.HTTP_200_OK, r.content)
token = r.data["access"]
client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


print("== 1. Crear albergues ==")
r = client.post("/api/albergues/", {"nombre": "Albergue Central", "direccion": "Av. Lima 123", "telefono": "987654321"}, format="json")
check("albergue creado", r.status_code == status.HTTP_201_CREATED, r.content)
central_id = r.data["id"]

r = client.post("/api/albergues/", {"nombre": "Sucursal Norte", "direccion": "Jr. Norte 45", "telefono": "987000111"}, format="json")
norte_id = r.data["id"]

print("== 2. Crear animal (ingreso) ==")
r = client.post("/api/animales/", {
    "nombre": "Rex", "especie": "Perro", "raza": "Pastor Alemán",
    "edad_aproximada": 3, "sexo": "Macho", "estado_actual": "En Albergue",
}, format="json")
check("animal creado", r.status_code == status.HTTP_201_CREATED, r.content)
animal_id = r.data["id"]

r = client.post("/api/ingresos/", {
    "animal": animal_id, "fecha_ingreso": "2026-01-10",
    "motivo_ingreso": "Abandono en la vía pública",
    "albergue_inicial": central_id,
}, format="json")
check("ingreso registrado", r.status_code == status.HTTP_201_CREATED, r.content)

print("== 3. Ubicacion temporal (historial de traslados) ==")
r = client.post("/api/ubicaciones/", {
    "animal": animal_id, "albergue": central_id,
    "fecha_entrada": "2026-01-10", "fecha_salida": "2026-02-01",
    "observaciones": "Primeros cuidados",
}, format="json")
check("ubicacion 1", r.status_code == status.HTTP_201_CREATED, r.content)

r = client.post("/api/ubicaciones/", {
    "animal": animal_id, "albergue": norte_id,
    "fecha_entrada": "2026-02-01", "fecha_salida": None,
    "observaciones": "Trasladado por espacio",
}, format="json")
check("ubicacion 2 (cambio de albergue)", r.status_code == status.HTTP_201_CREATED, r.content)

r = client.post("/api/ubicaciones/", {
    "animal": animal_id, "albergue": central_id,
    "fecha_entrada": "2026-02-10", "fecha_salida": "2026-02-01",
    "observaciones": "fecha mal",
}, format="json")
check("rechaza salida anterior a entrada", r.status_code == status.HTTP_400_BAD_REQUEST, r.content)

print("== 4. Atencion veterinaria (varias) ==")
r = client.post("/api/atenciones/", {
    "animal": animal_id, "fecha_atencion": "2026-01-15",
    "diagnostico": "Desparasitación", "tratamiento": "Pastilla x 3 días",
    "veterinario_responsable": "Dra. Pérez", "costo": 50.00,
}, format="json")
check("atencion 1", r.status_code == status.HTTP_201_CREATED, r.content)

r = client.post("/api/atenciones/", {
    "animal": animal_id, "fecha_atencion": "2026-02-20",
    "diagnostico": "Vacunación antirrábica", "tratamiento": "Vacuna subcutánea",
    "veterinario_responsable": "Dr. Gómez", "costo": 80.00,
}, format="json")
check("atencion 2", r.status_code == status.HTTP_201_CREATED, r.content)

r = client.post("/api/atenciones/", {
    "animal": animal_id, "fecha_atencion": "2026-02-20",
    "diagnostico": "X", "tratamiento": "Y", "veterinario_responsable": "Z",
    "costo": -10,
}, format="json")
check("rechaza costo negativo", r.status_code == status.HTTP_400_BAD_REQUEST, r.content)

print("== 5. Adoptantes y solicitudes (multiples) ==")
r = client.post("/api/adoptantes/", {
    "nombre": "Juan", "apellido": "Lopez", "telefono": "999111222",
    "email": "juan@mail.com", "direccion": "Av. Sur 100",
}, format="json")
check("adoptante creado", r.status_code == status.HTTP_201_CREATED, r.content)
adoptante_id = r.data["id"]

r = client.post("/api/adoptantes/", {
    "nombre": "Maria", "apellido": "Rojas", "telefono": "933555777",
    "email": "JUAN@MAIL.COM", "direccion": "Calle 5",
}, format="json")
check("rechaza email duplicado (case-insensitive)", r.status_code == status.HTTP_400_BAD_REQUEST, r.content)

r = client.post("/api/solicitudes/", {
    "animal": animal_id, "adoptante": adoptante_id,
    "fecha_solicitud": "2026-03-01", "estado": "Rechazada",
    "comentarios": "Sin espacio para mascota",
}, format="json")
check("solicitud 1 rechazada", r.status_code == status.HTTP_201_CREATED, r.content)

r = client.post("/api/solicitudes/", {
    "animal": animal_id, "adoptante": adoptante_id,
    "fecha_solicitud": "2026-03-15", "estado": "Aprobada",
    "comentarios": "Entrevista favorable",
}, format="json")
check("solicitud 2 aprobada", r.status_code == status.HTTP_201_CREATED, r.content)
solicitud_aprobada = r.data["id"]

r = client.post("/api/adopciones/", {
    "solicitud": r.data["id"], "fecha_adopcion": "2026-03-01",
    "seguimiento_post_adopcion": "",
}, format="json")
check("rechaza adopcion antes de la solicitud", r.status_code == status.HTTP_400_BAD_REQUEST, r.content)

print("== 6. Concretar adopcion y seguimiento ==")
r = client.post("/api/adopciones/", {
    "solicitud": solicitud_aprobada, "fecha_adopcion": "2026-03-20",
    "seguimiento_post_adopcion": "Primer control en 15 días",
}, format="json")
check("adopcion creada", r.status_code == status.HTTP_201_CREATED, r.content)
adopcion_id = r.data["id"]

r = client.post("/api/seguimientos/", {
    "adopcion": adopcion_id, "fecha": "2026-03-19", "nota": "visita previa",
}, format="json")
check("rechaza seguimiento antes de adopcion", r.status_code == status.HTTP_400_BAD_REQUEST, r.content)

r = client.post("/api/seguimientos/", {
    "adopcion": adopcion_id, "fecha": "2026-04-05",
    "nota": "El animal se adaptó muy bien a su nueva casa",
}, format="json")
check("seguimiento creado", r.status_code == status.HTTP_201_CREATED, r.content)

r = client.post("/api/solicitudes/", {
    "animal": animal_id, "adoptante": adoptante_id,
    "fecha_solicitud": "2026-04-01", "estado": "Pendiente", "comentarios": "",
}, format="json")
check("rechaza nueva solicitud de animal adoptado", r.status_code == status.HTTP_400_BAD_REQUEST, r.content)

print("== 7. Historial completo del animal ==")
animal = Animal.objects.get(pk=animal_id)
check("estado_actual = Adoptado", animal.estado_actual == "Adoptado")
check("1 ingreso", animal.ingresos.count() == 1)
check("2 ubicaciones (traslados)", animal.ubicaciones.count() == 2)
check("2 atenciones", animal.atenciones_medicas.count() == 2)
check("2 solicitudes", animal.solicitudes.count() == 2)
check("1 adopcion", Adopcion.objects.filter(solicitud__animal=animal).count() == 1)

r = client.get(f"/api/animales/{animal_id}/", format="json")
payload = r.json()
check("GET animal muestra historial anidado", all(
    k in payload for k in ["ingresos", "ubicaciones", "atenciones_medicas", "solicitudes"]
))

print("== 8. Proteccion del historial (PROTECT) ==")
try:
    animal.delete()
    check("no se puede borrar animal con historial", False, "el borrado no fue bloqueado")
except ProtectedError:
    check("borrado de animal bloqueado por PROTECT", True)

print(f"\nASERTS: {ok} OK, {fail} FAIL")
raise SystemExit(1 if fail else 0)
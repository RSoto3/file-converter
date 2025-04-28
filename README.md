# Conversor de JSON a CSV para Datos de Personas

Este script permite convertir datos de un archivo JSON a CSV

## Características

- Reemplaza entidades HTML en los textos.
- Limpia espacios innecesarios.
- Valida y formatea fechas al formato `YYYY-MM-DD`.
- Detecta RUNs duplicados (pero no elimina el duplicado).
- Exporta múltiples archivos CSV, con cantidad de registros por archivo personalizable.
- Mantiene codificación UTF-8.

### Requisitos

- Python 3.6 o superior

## Estructura de Carpetas

```
proyecto/
│
├── data/         # Aquí se debe colocar el archivo JSON de entrada (en este caso: 'persona.json')
├── tmp/          # Aquí se guardarán los archivos CSV generados
├── scripts/json_to_csv.py     # Este es el script principal
└── README.md     # Este archivo
```

### 4. Ejecuta el script (debes estar en la carpeta scripts)

```bash
python json_to_csv.py
```

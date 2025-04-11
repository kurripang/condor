# Especificaciones Técnicas de Cóndor v1.0

## Estructura del Proyecto
```plaintext
.oasf/
├── MANIFEST.json          # Metadatos globales
├── audio/                 # Pistas de audio (WAV/FLAC 24-bit)
│   ├── kick_001.wav       # Nombre con hash parcial (ej: kick_a1b2.wav)
│   └── vocal_verse.wav
├── midi/                  # Archivos MIDI con expresiones detalladas
│   ├── bassline.mid       # Incluir CC1 (Modulación), CC11 (Expresión)
│   └── pads.mid
└── plugins/               # Configuraciones de plugins
    ├── fabfilter_proq3/
    │   └── eq_settings.json  # Parámetros en texto plano
    └── valhalla_delay/
        └── delay_preset.yaml
```

## MANIFEST.json Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "bpm": {
      "type": "number",
      "description": "Tempo en beats por minuto (ej: 120.0)"
    },
    "time_signature": {
      "type": "string",
      "pattern": "^\\d+/\\d+$",
      "example": "4/4"
    },
    "audio_tracks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "name": { "type": "string" },
          "path": { "type": "string" },
          "hash": { 
            "type": "string",
            "pattern": "^sha3-512:[a-f0-9]{128}$"
          }
        }
      }
    }
  },
  "required": ["bpm", "audio_tracks"]
}
```

## Tipos de Datos
| **Tipo**     | **Formato**          | **Ejemplo**           | **Uso**                |
|--------------|----------------------|-----------------------|------------------------|
| `timestamp`  | ISO 8601 con Z       | `2025-04-11T18:30:00Z` | Fechas de modificación |
| `hash`       | `sha3-512:[hex]`     | `sha3-512:a1b2...`    | Integridad de archivos |
| `dB`         | Número con precisión | `-6.3`                | Niveles de plugins     |

## Algoritmos Obligatorios
- **Hashes**: SHA3-512 (mejor para audio que SHA-256).
- **Compresión**: Zstandard (nivel 3) para metadata, audio sin compresión.
# Recuperación de sprites compartidos (2026-11-21)

Se conservan archivos por entidad aunque su imagen sea idéntica. No se borra ni reemplaza ningún sprite previo. Las copias proceden de archivos ya publicados en este repositorio; sus nombres nuevos conservan los nombres de la API.

| Tabla de la API | Campo | Archivos |
|---|---|---:|
| bosses | static_img | 107 |
| monsters | image_url | 8 |
| monsters | static_img | 253 |

Procedencia y hashes: `docs/sprite-recovery-2026-11-21.json`. Aggressive Chicken coincide con el SHA1 original confirmado por la API de TibiaWiki. Las demás coincidencias requieren exactamente el mismo lookType/lookTypeEx, colores, addons y montura en definiciones literales de Canary, y un único contenido entre los sprites candidatos. Si varias imágenes del mismo grupo difieren, no se elige una a ciegas.

Se validaron los 368 archivos y todos sus fotogramas; los 360 archivos estáticos tienen un fotograma. Los originales y animaciones se conservan sin reescalar ni convertir.

El servidor de archivos de la wiki respondió 403 para Torch. Se detuvieron las descargas; no se usan mirrors, otra IP ni variantes para rodear el bloqueo. No se descargaron nuevas imágenes de ese CDN en esta ejecución. Los objetos y criaturas sin archivo local verificable siguen pendientes.

Tibia y sus gráficos pertenecen a CipSoft. Se conservan las fuentes de TibiaWiki y de los assets previos. Este proyecto no está afiliado con CipSoft.

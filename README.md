# Portal de Informes de Soporte · INCOMELEC

Portal web estático con los informes del Área de Soporte.

## Estructura

| Ruta | Contenido |
|---|---|
| `index.html` | Portal de entrada: estado y fecha de actualización de cada informe |
| `SOPORTE SEMANAL/` | Informe de Soporte de la semana más reciente |
| `INFORME MENSUAL/` | Informe mensual · Comité de Dirección |
| `PLAN ESTRATEGICO/` | Seguimiento del Plan Estratégico 2026 |
| `REQUERIMIENTOS GESTION INTEGRAL/` | Requerimientos del sistema de gestión integral |

Cada carpeta contiene un `index.html` autocontenido (HTML, CSS y JS en un solo archivo).

## Cómo actualizar

- **Portal:** editar el objeto `window.PORTAL` al inicio de `index.html` (fechas, frecuencias, alertas).
- **Dashboards:** cada informe puede publicar su propia fecha en su `<head>`, y el portal la lee:

```html
<meta name="lidato:actualizado" content="2026-11-10T17:30-05:00">
<meta name="lidato:periodo"     content="Semana 45 · 2026">
```

## Publicación

Listo para GitHub Pages (incluye `.nojekyll`): Settings → Pages → Deploy from branch → `main` / `root`.

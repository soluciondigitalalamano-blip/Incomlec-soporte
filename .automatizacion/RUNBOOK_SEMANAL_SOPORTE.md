# Runbook · Informe Semanal de Soporte · INCOMELEC

Operación real. Seis corridas por semana: martes y miércoles a las 12:52,
14:52 y 16:52 (hora de Bogotá). La primera que encuentre el insumo publica;
las demás salen en silencio.

El reloj de la máquina está en UTC. Saca la hora local con
`TZ=America/Bogota date '+%Y-%m-%dT%H:%M'` y nunca escribas en el informe
una hora que quede en el futuro.

---

## Paso 0 · Salidas tempranas

Busca en Gmail un correo **del dominio `incomelec.com`**, con **«Informe de
soporte» en el asunto** y un **PDF adjunto**.

Consulta sugerida: `from:incomelec.com subject:(informe soporte) has:attachment newer_than:10d`

El adjunto se llama `<DDMMAAAA> INFORME SOPORTE.pdf`. **Los separadores
varían**: pueden ser espacios o guiones bajos. No descartes un PDF por eso;
lo que importa son los ocho dígitos iniciales, que son la fecha del corte en
formato DDMMAAAA.

- **No llegó** → termina en silencio. No avises.
- **Llegó, pero su corte ya está publicado** en `semana.corte` de
  `SOPORTE SEMANAL/index.html` → termina en silencio.
- **Su corte es anterior al publicado** → no publiques y avisa. Nunca
  retrocedas el corte.

## Paso 1 · Descargar y renderizar

Baja el adjunto a una carpeta nueva y vacía. Renderiza las nueve páginas:

```
pdftoppm -png -r 110 informe.pdf pag
```

Lee cada página **como imagen**. El texto extraído de un PDF de Power BI
sale desordenado y mezcla columnas: no transcribas desde ahí.

## Paso 2 · Validar que el PDF viene completo  ⚠️ OBLIGATORIO

Lee en cada página la tarjeta **Max Fecha Datos** (o el segmentador de mes,
donde no haya tarjeta) y compárala con el corte del nombre del archivo.

Esto no es teórico: **el 18-nov-2026 la página 1 (TICKETS ABIERTOS) vino
congelada en 10/11/2026 07:00**, con cifras idénticas a las de la semana
anterior, mientras el resto del PDF sí traía el corte nuevo.

Si alguna página no corresponde al corte:

- no transcribas esa sección, deja publicados los valores anteriores;
- sigue con las demás páginas;
- nombra en la notificación final qué páginas venían viejas.

Nunca publiques como dato nuevo una cifra repetida de la semana anterior.

## La plantilla ya está parametrizada

Los textos de la página —encabezado, pie, títulos, insights, la etiqueta
del eje— se derivan de `DATA.semana` y de los propios valores mediante las
constantes `CORTE`, `CORTE_DM`, `CORTE_DIA`, `MES_AL`, `MES_AL_C` y `RANGO`.
**No escribas la fecha a mano en ninguna parte.** Si al revisar encuentras
una fecha literal en el código de presentación, conviértela en derivada en
vez de editarla.

Lo mismo con los textos de reaperturas y de mantenimientos: dependen de
`DATA.reabiertos` y `DATA.mantenimientos`, no de constantes.

### Los dos cortes  ⚠️ revísalo cada semana

El informe maneja **dos** fechas de corte, porque el export puede traer la
página de tickets abiertos desfasada:

| Campo | Qué rotula |
|---|---|
| `DATA.semana.corte` | todo lo demás: flujo, SLA, ANS, clientes, compromisos |
| `DATA.semana.corteAbiertos` | backlog, tickets abiertos por área y por cliente, antigüedad |

De ahí salen `CORTE` / `CORTE_DM` y `CORTE_AB` / `CORTE_AB_DM`.

**Qué hacer cada semana**, según lo que diga la tarjeta *Max Fecha Datos*
de la página «INFORME TICKETS ABIERTOS» (Paso 2):

- Si corresponde al corte nuevo: transcribe esas secciones y pon
  `corteAbiertos` **igual** a `corte`.
- Si viene desfasada: no transcribas esas secciones y **deja
  `corteAbiertos` con la fecha que indique la tarjeta**, no con la del
  corte nuevo. Nunca lo dejes con el valor de la semana pasada por
  descuido: si no lo tocas, la página seguirá afirmando una fecha falsa.

Si el export deja de traer el desfase, `corteAbiertos` queda igual a
`corte` y la distinción desaparece sola de la pantalla.

## Paso 3 · Transcribir

Sigue `MAPA_PDF_A_DATA.md`, que dice qué página alimenta cada sección. No
inventes correspondencias que no estén ahí.

**Ubica cada sección por el título de la página, nunca por su número.** El
número de páginas cambia de un export a otro: el del 10-nov trajo diez y el
del 18-nov, nueve. Si un título no aparece esta semana, deja publicados los
valores anteriores de esa sección y dilo en la notificación.

Edita **solo** el bloque `const DATA = { … }` de
`SOPORTE SEMANAL/index.html`, incluidos `semana.label`, `semana.corte` y
`semana.hora`. Nada más de ese archivo.

## Paso 4 · Reconciliar con código  ⚠️ OBLIGATORIO

Antes de publicar, comprueba con un script —no a ojo— que:

- la suma de ingresados por área es igual al total del mes;
- la suma de cerrados por área es igual al total de cerrados del mes;
- `cumple + fuera` es igual a `cerrados` en el bloque `sla`;
- la suma de la columna de prioridad cuadra con el total de `sla`;
- cada serie mensual tiene el número de meses que le corresponde;
- ningún porcentaje queda fuera de 0–100.

Si algo no cuadra: no publiques y avisa con el detalle.

## Paso 5 · Fecha del portal

En el `index.html` **raíz**, dentro de `window.PORTAL`, actualiza el campo
`actualizado` del informe con `id: 'semanal'` a la fecha y hora del corte,
en formato `AAAA-MM-DDTHH:MM`. Es lo que hace que la tarjeta del portal deje
de decir «Por actualizar».

## Paso 6 · Publicar

Commit y push a `main`. Cloudflare Pages despliega solo el proyecto
`incomelec-soporte`.

El despliegue de Cloudflare tarda entre uno y cuatro minutos desde el
push. Espera y vuelve a consultar con un parámetro distinto en la URL
(`?v=<algo>`) para no leer la copia en caché; no des por fallido el
despliegue antes de cinco minutos. Comprueba que
`https://incomelec-soporte.pages.dev/SOPORTE%20SEMANAL/` responda y muestre
el corte nuevo. Esa es la URL a la que apunta el botón del correo. **Si no
sirve todavía el contenido nuevo, no envíes el correo**: avisa que el
despliegue no llegó.

## Paso 7 · Correo al área de soporte

Solo si el Paso 6 terminó bien. Sale por **Resend**, nunca por Gmail: el
conector de Gmail reescribe las direcciones y borra las imágenes externas.

Con `mcp__Resend__send-email`:

- `from`: `LIDATO <operaciones@lidato.site>`
- `to`: `["diego.munoz@incomelec.com", "Linda.Silva@incomelec.com", "vanessa.patino@incomelec.com"]`
- `subject`: `Actualización informe soporte`
- `html`: el contenido de `correo-aviso.html`, **tal cual, sin reemplazar nada**
- `text`: el contenido de `correo-aviso.txt`, también tal cual. Es
  obligatorio junto al html; no lo omitas.
- `attachments`: **ninguno**. Esta plantilla trae el logo y el icono como
  imágenes remotas (`src` a raw.githubusercontent.com), no como adjuntos
  `cid:`. No le agregues adjuntos ni conviertas las imágenes a `cid:`.

La plantilla no lleva fecha ni marcadores: no hay `{{FECHA_CORTE}}` que
sustituir. No le agregues la fecha del corte al cuerpo ni al asunto.

No toques el enlace del botón ni lo envuelvas en nada: Resend lo entrega
intacto y el cliente entra con un solo clic.

Después de enviar, con el `id` que devuelve llama a `mcp__Resend__get-email`
y comprueba en el HTML enviado que aparezca
`href="https://incomelec-soporte.pages.dev/"` sin `google.com/url`. Reporta
el resultado en una línea.

Si Resend falla, avisa el error y **no reintentes por Gmail**.

## Paso 8 · Bitácora en Notion

Solo si el correo salió. Base `LIDATO QUEST · Bitácora`
(`collection://4204c6f8-c23f-8158-bae8-000bdfbb3f41`).

Fila: `Registro` exactamente
`INCOMELEC · Informe Semanal de Soporte · <YYYY-MM>`. Si no existe la fila
del ciclo, **no la crees** y no inventes el `Total`: avisa que falta.

**Candado por semana, no por día.** Seis corridas se reparten entre martes y
miércoles. Mira el campo `Fecha`: si ya cae dentro de la semana en curso
(lunes a domingo, hora de Bogotá), la entrega ya está marcada y **no tocas
nada**. Comparar solo contra «hoy» dejaría pasar una segunda marca el
miércoles.

Si no está marcada:

- `Hecho` = el valor leído **más 1**, y solo +1. No lo recalcules contando
  semanas del calendario: una semana sin entrega debe quedarse atrás.
- `date:Fecha:start` = la fecha de hoy · `date:Fecha:is_datetime` = 0
- Si el nuevo `Hecho` iguala a `Total`: `Estado` = `Entregado a tiempo`.
  Si queda por debajo: `Estado` = `Parcial`. Si lo superaría: no escribas
  nada y avisa.
- No cambies ninguna otra propiedad.

Al terminar, relee la fila y di en una línea qué pasó: `contador 3 → 4` o
`la semana ya estaba marcada, no se tocó`.

Si Notion falla, el correo ya salió y eso no se deshace: avisa que falta
marcar la semana y no reintentes en bucle.

## Si algo falla

Transcripción, reconciliación o push fallidos: avisa el error con detalle,
**no envíes el correo** y **no escribas en la Bitácora**.

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
soporte» en el asunto** y un **PDF adjunto** llamado
`<DDMMAAAA>_INFORME_SOPORTE.pdf`.

Consulta sugerida: `from:incomelec.com subject:(informe soporte) has:attachment newer_than:10d`

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

## Paso 3 · Transcribir

Sigue `MAPA_PDF_A_DATA.md`, que dice qué página alimenta cada sección. No
inventes correspondencias que no estén ahí.

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

Commit y push a `main`. Cloudflare Pages despliega solo.

Verifica que la página publicada responda y muestre el corte nuevo. **Si la
URL del cliente todavía no sirve el contenido nuevo, no envíes el correo**:
avisa que el despliegue no llegó al dominio del cliente.

## Paso 7 · Correo al área de soporte

Solo si el Paso 6 terminó bien. Sale por **Resend**, nunca por Gmail: el
conector de Gmail reescribe las direcciones y borra las imágenes externas.

Con `mcp__Resend__send-email`:

- `from`: `LIDATO <operaciones@lidato.site>`
- `to`: `["diego.munoz@incomelec.com", "Linda.Silva@incomelec.com", "vanessa.patino@incomelec.com"]`
- `subject`: `Actualización informe soporte`
- `html`: el contenido de `correo-aviso.html` con `{{FECHA_CORTE}}` reemplazado
- `text`: el de `correo-aviso.txt`, igual. Es obligatorio junto al html.
- `attachments`: dos, en este orden. Primero `filename` `logo.png`, `url`
  `https://raw.githubusercontent.com/soluciondigitalalamano-blip/mis-imagenes/refs/heads/main/logo-white.png`,
  `contentId` `logolidato`. Segundo `filename` `usuario.png`, `url`
  `https://raw.githubusercontent.com/soluciondigitalalamano-blip/mis-imagenes/refs/heads/main/user-icon-teal.png`,
  `contentId` `iconousuario`. Esos `contentId` tienen que coincidir con los
  `cid:` de la plantilla o los iconos salen rotos.

`{{FECHA_CORTE}}` es la fecha del corte en formato `18 de Noviembre`. No uses
`date '+%B'`, que devuelve el mes en inglés. Antes de enviar comprueba que ni
el html ni el texto conserven la cadena `FECHA_CORTE`.

Después de enviar, con el `id` que devuelve llama a `mcp__Resend__get-email`
y comprueba que el enlace del botón salió intacto, sin `google.com/url`, y
que no quedó ningún `FECHA_CORTE`. Reporta el resultado en una línea.

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

# Mapa · página del PDF → sección del bloque `DATA`

Insumo: `<DDMMAAAA>_INFORME_SOPORTE.pdf`, exportado de Power BI Desktop.
Nueve páginas apaisadas. La fecha del nombre es la del corte.

Destino: el bloque `const DATA = { … }` de `SOPORTE SEMANAL/index.html`
(hoy, líneas ~497 a ~592). **Es lo único que se edita.** El resto del
archivo —estilos, Chart.js, render— no se toca nunca.

> El PDF no trae texto fiable: la extracción con `pdftotext` sale
> desordenada y mezcla columnas. Renderiza cada página a imagen
> (`pdftoppm -png -r 110 -f N -l N informe.pdf pagN`) y **léela como
> imagen**. Nunca transcribas desde el texto plano.

> **El número de página NO es estable.** El export del 10-nov-2026 trae diez
> páginas y abre con «TICKETS TOTAL ABIERTOS POR NIVEL»; el del 18-nov-2026
> trae nueve y esa página no existe. **Localiza cada sección por su título,
> nunca por su número de página.** Si un título no aparece en el export de
> esta semana, deja publicados los valores anteriores de esa sección y dilo
> en la notificación.

| Título en el PDF | Alimenta |
|---|---|
| TICKETS TOTAL ABIERTOS POR NIVEL · CONSOLIDADO DIARIOS | `semana.dias`, `abiertosArea` |
| INFORME TICKETS ABIERTOS | `abiertosKpi`, `abiertosFinMes`, `abiertosArea`, `antiguedad`, `abiertosCliente` |
| INFORME TICKETS ABIERTOS Y CERRADOS | `tarjetasAnio`, `flujo`, `areaNov` |
| INFORME TIEMPOS DE SERVICIO | `sla` (todo el bloque) |
| INFORME GENERAL TICKETS REABIERTOS | `reabiertos` |
| CLIENTES CON MÁS INGRESO Y CIERRE TICKETS | `clientes` |
| TICKETS POR ÁREAS 2026 | `areas`, `areaOct` (tabla izquierda = mes cerrado; derecha = mes en curso) |
| INFORMES TICKETS CLIENTES 2026 | `informes` |
| MANTENIMIENTOS 2026 | `mantenimientos`, `efReal`, `efTot` |
| CUMPLIMIENTO ANS POR TÉCNICO | `ansOct` |

Las dos primeras filas son alternativas: según el export, los tickets
abiertos vienen en una página o en la otra. `semana.dias` (el consolidado
diario del mes) solo existe en la primera; si el export no la trae, ese
campo no se actualiza.

## Detalle por sección

**`semana`** — `label` ('Semana D – D mes AAAA'), `corte` (fecha del nombre
del archivo), `hora` y `corteAbiertos`. Este último es la fecha que rotula
las secciones de tickets abiertos: ponlo igual a `corte` cuando la página
de abiertos venga al día, y con la fecha de su tarjeta *Max Fecha Datos*
cuando venga desfasada. Ver «Los dos cortes» en el runbook.

**`abiertosKpi`** (pág. 1, tarjetas superiores) — `total` = Total Tickets
Abiertos · `clientes` = Clientes con Tickets · `antiguedadDias` = Promedio
Antigüedad · `mas7dias` = Tickets Mayor a 7 Días · `antiguedadHoras` = fila
Total, columna Promedio Antigüedad (horas) de la tabla derecha.

**`abiertosFinMes`** (pág. 1, «Total Tickets que quedaron abiertos por mes
2026») — once valores, enero a noviembre, en orden.

**`abiertosArea`** (pág. 1, «Tickets Abiertos por Área») — por área,
`[2026, 2025]`. Las barras vienen en pares por año; respeta ese orden.

**`antiguedad`** (pág. 1, «Detalle de Tickets Abiertos por Año») — pares
`['mes aaaa', n]` de arriba abajo.

**`abiertosCliente`** (pág. 1, tabla derecha) — solo las filas visibles:
`[año, mes, cliente, tickets, % del total, antigüedad días, antigüedad horas]`.

**`tarjetasAnio`** (pág. 2, tarjetas) — `ingresados`, `cerrados`, `abiertos`,
`pct` (% Cerrados vs Ingresados), `atencionDias` (Promedio Atención),
`promDia` (Promedio por Día).

**`flujo`** (pág. 2) — del «Histórico por mes de Ingresados y Cerrados 2026»
salen los ingresados, los cerrados totales y los pendientes por mes; del
«Ratio Operativo por Mes» salen los cerrados nuevos y el % de ratio backlog.
`cerradosAntiguos` NO se escribe: el propio HTML lo calcula restando.

**`areaNov`** (pág. 2, «Descripción por área») — por área:
`[ingresados, cerrados, abiertos, promedio atención días]`.

**`sla`** (pág. 3) — `cerrados`, `promedio` (SLA Promedio General),
`cumplePct` (% Cumple por ANS), `cumple` (Total Cumple por ANS), `fuera`
(del anillo «Estado de tiempo de atención»), `promFuera` y `promATiempo`
(«Promedio Atención por horas»). Las series `general`, `aTiempo` y `fueraT`
salen de «Promedio de Horas por Estado de Cumplimiento»; `nuevosATiempo` y
`nuevosFuera` de «Promedio de horas por cumplimiento SLA – Tickets nuevos».
`prioridad` es la tabla inferior; `area` es el barrado derecho
`[area, promedio general ANS, promedio a tiempo]`.

**`reabiertos`** (pág. 4) — `cerradosAnio`, `cerradosSitio` (Técnicos en
Sitio), `total` (Tickets Reabiertos), `promedio`, `pct`, más `tecnicos` del
barrado y `tickets` de la tabla DETALLE REABIERTOS.

**`clientes`** (pág. 5) — por cliente, los tickets ingresados y cerrados del
barrado izquierdo y el movimiento de entradas del derecho. El segmentador
dice el mes al que está filtrada la página: compruébalo.

**`areas` / `areaOct`** (pág. 6) — dos tablas. La izquierda es el acumulado
del último mes cerrado; la derecha, el mes en curso. Cada fila:
`[ingresos, cerrados]`, y el % de efectividad se recalcula solo.

**`informes`** (pág. 7) — `esperados`, `ejecutados`, `faltantes`, `pct`, y el
desglose por ANS (Diamante / Oro) de la tabla.

**`mantenimientos`** (pág. 8) — tarjetas: `esperados`, `ejecutadaAcum`,
`faltantes`, `pct`. De la tabla mensual salen `efReal` (% Efectividad de
Cantidad Real del Mes) y `efTot` (% Efectividad Total), doce valores cada una.

**`ansOct`** (pág. 9) — `cerradosMes` (Total Cerrados Mes Vigente),
`cerradosTecnicos`, `cumple` (Total Cumple ANS), `pctMes` (% Efectividad
Mes-Cumple), `pctTotal`, `ingenieros` del barrado y `areaCierre` del pastel.

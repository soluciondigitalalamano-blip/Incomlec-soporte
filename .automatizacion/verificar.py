#!/usr/bin/env python3
"""
Verificación del informe semanal de Soporte · INCOMELEC

Comprueba el bloque DATA de «SOPORTE SEMANAL/index.html» contra sí mismo y
contra la versión publicada anteriormente. NO es opcional: el Paso 4 del
runbook consiste en ejecutar esto y pegar su salida en la notificación.

    python3 .automatizacion/verificar.py

Sale con código 0 si todo pasa y 1 si algo falla. Si falla, NO se publica.
"""
import json, re, subprocess, sys, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
HTML = RAIZ / 'SOPORTE SEMANAL' / 'index.html'
MES = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']

def extraer(texto):
    """Evalúa el bloque const DATA = {...} y lo devuelve como diccionario."""
    i = texto.index('const DATA = {')
    j = texto.index('\n};', i) + 3
    js = texto[i:j] + '\nconsole.log(JSON.stringify(DATA));'
    tmp = pathlib.Path('/tmp/_data_verif.js'); tmp.write_text(js)
    r = subprocess.run(['node', str(tmp)], capture_output=True, text=True)
    if r.returncode: sys.exit('No se pudo evaluar el bloque DATA:\n' + r.stderr)
    return json.loads(r.stdout)

def anterior():
    """El bloque DATA tal como estaba en el último commit, o None."""
    r = subprocess.run(['git','-C',str(RAIZ),'show','HEAD:SOPORTE SEMANAL/index.html'],
                       capture_output=True, text=True)
    return extraer(r.stdout) if r.returncode == 0 else None

fallos, avisos = [], []
def chk(cond, ok, mal):
    print(('  OK    ' if cond else '  FALLA ') + (ok if cond else mal))
    if not cond: fallos.append(mal)
def avisa(t):
    print('  AVISO ' + t); avisos.append(t)

D = extraer(HTML.read_text())
P = anterior()
NOV = 10

print('\n── Coherencia interna ──')
s = D['sla']
chk(s['cumple'] + s['fuera'] == s['cerrados'],
    f"SLA: {s['cumple']} a tiempo + {s['fuera']} fuera = {s['cerrados']} cerrados",
    f"SLA: {s['cumple']}+{s['fuera']} ≠ {s['cerrados']}")
for idx, nombre in ((1,'cerrados'), (2,'a tiempo'), (3,'fuera')):
    tot = sum(r[idx] for r in s['prioridad'])
    esp = {1: s['cerrados'], 2: s['cumple'], 3: s['fuera']}[idx]
    chk(tot == esp, f"prioridad {nombre}: suma {tot}", f"prioridad {nombre}: {tot} ≠ {esp}")

an = D['areaNov']
chk(sum(v[0] for v in an.values()) == D['flujo']['ingresados'][NOV],
    f"área nov ingresados = {D['flujo']['ingresados'][NOV]}",
    f"área nov ingresados {sum(v[0] for v in an.values())} ≠ flujo {D['flujo']['ingresados'][NOV]}")
chk(sum(v[1] for v in an.values()) == D['flujo']['cerradosNuevos'][NOV],
    f"área nov cerrados = {D['flujo']['cerradosNuevos'][NOV]}",
    f"área nov cerrados {sum(v[1] for v in an.values())} ≠ cerrados nuevos {D['flujo']['cerradosNuevos'][NOV]}")
chk(all(D['flujo']['cerradosTotal'][i] >= D['flujo']['cerradosNuevos'][i] for i in range(11)),
    "cerrados totales ≥ cerrados nuevos en los once meses",
    "algún mes tiene más cerrados nuevos que cerrados totales")

m = D['mantenimientos']
chk(sum(m['acum']) == m['ejecutadaAcum'], f"mantenimientos acumulado = {m['ejecutadaAcum']}",
    f"mantenimientos: suma {sum(m['acum'])} ≠ tarjeta {m['ejecutadaAcum']}")
chk(sum(m['real']) == m['esperados'], f"mantenimientos esperados = {m['esperados']}",
    f"mantenimientos: suma real {sum(m['real'])} ≠ esperados {m['esperados']}")
malos = [MES[i] for i in range(12) if m['realEj'][i] + m['ejPend'][i] != m['acum'][i]]
chk(not malos, "cada mes: real ejecutado + pendientes ejecutados = acumulado",
    f"no cuadra el acumulado en: {', '.join(malos)}")

a = D['ansOct']
chk(sum(r[1] for r in a['areaCierre']) == a['cumple'],
    f"ANS por área de cierre = {a['cumple']}",
    f"ANS por área suma {sum(r[1] for r in a['areaCierre'])} ≠ cumple {a['cumple']}")
chk(a['cerradosTecnicos'] <= a['cerradosMes'], "cerrados por técnicos ≤ cerrados del mes",
    f"cerrados por técnicos {a['cerradosTecnicos']} > del mes {a['cerradosMes']}")

r_ = D['reabiertos']
chk(sum(t[2] for t in r_['tecnicos']) == r_['total'],
    f"reaperturas por técnico = {r_['total']}",
    f"reaperturas por técnico suman {sum(t[2] for t in r_['tecnicos'])} ≠ {r_['total']}")
chk(len(r_['tickets']) == r_['total'], f"tickets reabiertos listados = {r_['total']}",
    f"hay {len(r_['tickets'])} tickets listados y {r_['total']} reaperturas")
chk(r_['total'] <= r_['cerradosSitio'], "reaperturas ≤ cierres en sitio",
    f"{r_['total']} reaperturas sobre {r_['cerradosSitio']} cierres en sitio")

I = D['informes']
chk(sum(f[2] for f in I['filas']) == I['ejecutados'], f"informes ejecutados = {I['ejecutados']}",
    f"filas suman {sum(f[2] for f in I['filas'])} ejecutados ≠ {I['ejecutados']}")
chk(sum(f[1] for f in I['filas']) == I['esperados'], f"informes esperados = {I['esperados']}",
    f"filas suman {sum(f[1] for f in I['filas'])} esperados ≠ {I['esperados']}")

print('\n── Forma de los datos ──')
for nombre, serie in [('flujo.ingresados', D['flujo']['ingresados']), ('flujo.cerradosNuevos', D['flujo']['cerradosNuevos']),
                      ('flujo.cerradosTotal', D['flujo']['cerradosTotal']), ('flujo.pendientes', D['flujo']['pendientes']),
                      ('flujo.ratio', D['flujo']['ratio']), ('sla.general', s['general']), ('sla.aTiempo', s['aTiempo']),
                      ('sla.fueraT', s['fueraT']), ('sla.nuevosATiempo', s['nuevosATiempo']),
                      ('sla.nuevosFuera', s['nuevosFuera']), ('abiertosFinMes', D['abiertosFinMes'])]:
    chk(len(serie) == 11, f"{nombre}: 11 meses", f"{nombre} tiene {len(serie)} valores, deben ser 11")
for nombre in ('real','pend','total','realEj','ejPend','acum','efReal','efTot'):
    chk(len(m[nombre]) == 12, f"mantenimientos.{nombre}: 12 meses",
        f"mantenimientos.{nombre} tiene {len(m[nombre])} valores, deben ser 12")
pcts = D['flujo']['ratio'] + m['efReal'] + m['efTot'] + [I['pct'], s['cumplePct'], a['pctMes'], a['pctTotal']]
fuera = [p for p in pcts if p is not None and not 0 <= p <= 100]
chk(not fuera, "todos los porcentajes entre 0 y 100", f"porcentajes fuera de rango: {fuera}")
chk(len(D['clientes']) == 10, "10 clientes en el top", f"hay {len(D['clientes'])} clientes, deben ser 10")
chk('corteAbiertos' in D['semana'], f"corteAbiertos declarado: {D['semana'].get('corteAbiertos')}",
    "falta DATA.semana.corteAbiertos (ver «Los dos cortes» en el runbook)")

print('\n── Contra la versión publicada ──')
if not P:
    avisa('no se pudo leer la versión anterior; sin comparación')
else:
    sucio = subprocess.run(['git','-C',str(RAIZ),'diff','--quiet','--','SOPORTE SEMANAL/index.html']).returncode != 0
    if D['semana']['corte'] != P['semana']['corte']:
        print(f"  OK    el corte avanzó: {P['semana']['corte']} → {D['semana']['corte']}")
    elif sucio:
        chk(False, '', f"hay cambios sin publicar pero el corte sigue en {D['semana']['corte']}")
    else:
        avisa(f"el corte {D['semana']['corte']} ya está publicado; esta comparación es contra sí misma. "
              "Ejecuta este script ANTES del commit.")
    # Los meses cerrados (ene–oct) no deberían moverse. Si se mueven, casi
    # siempre es una lectura equivocada del PDF, no un cambio real.
    for nombre, nuevo, viejo in [('flujo.ingresados', D['flujo']['ingresados'], P['flujo']['ingresados']),
                                 ('flujo.cerradosTotal', D['flujo']['cerradosTotal'], P['flujo']['cerradosTotal']),
                                 ('flujo.cerradosNuevos', D['flujo']['cerradosNuevos'], P['flujo']['cerradosNuevos'])]:
        dif = [f"{MES[i]} {viejo[i]}→{nuevo[i]}" for i in range(10) if viejo[i] != nuevo[i]]
        if dif: avisa(f"{nombre} cambió en meses ya cerrados: {', '.join(dif)} · confírmalo contra el PDF")
        else: print(f"  OK    {nombre}: los meses cerrados no se movieron")
    if D['areaOct'] != P['areaOct']:
        avisa('areaOct cambió · octubre es un mes cerrado, confírmalo contra el PDF')
    else:
        print('  OK    areaOct: octubre intacto')
    if D['abiertosKpi'] == P['abiertosKpi'] and D['semana'].get('corteAbiertos') == D['semana']['corte']:
        avisa('los tickets abiertos son idénticos a la semana pasada pero corteAbiertos dice que están al día · revisa el Paso 2')

print('\n── Resultado ──')
if fallos:
    print(f"  {len(fallos)} FALLO(S). No publiques."); sys.exit(1)
print(f"  Sin fallos." + (f" {len(avisos)} aviso(s) para confirmar a ojo." if avisos else " Listo para publicar."))

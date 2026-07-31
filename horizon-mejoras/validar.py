#!/usr/bin/env python3
"""Valida las plantillas generadas contra los esquemas reales del tema.

Shopify no avisa cuando un ajuste trae un valor que su esquema no acepta:
simplemente no lo aplica. Así se colaron dos botones sin estilo
("button-primary" en el hero y "link" en los "Ver todos") que sólo se
descubrieron abriendo la tienda en un teléfono.

Este script compara cada valor contra las opciones declaradas en
`schemas/`, que se extraen del propio tema. Sólo revisa los tipos de los
que hay esquema descargado; el resto los cuenta como omitidos para que
quede claro qué no se verificó.
"""

import glob
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
THEME = os.path.join(BASE, "theme")
SCHEMAS = os.path.join(BASE, "schemas")


def cargar_json(ruta):
    contenido = open(ruta, encoding="utf-8").read()
    if contenido.lstrip().startswith("/*"):
        contenido = contenido[contenido.index("{", contenido.index("*/")):]
    return json.loads(contenido)


def cargar_esquemas():
    esquemas = {"sections": {}, "blocks": {}}
    for ruta in glob.glob(os.path.join(SCHEMAS, "*.json")):
        clase, nombre = os.path.basename(ruta)[:-5].split("__", 1)
        esquemas[clase][nombre] = json.load(open(ruta, encoding="utf-8"))
    return esquemas


def indexar(esquema):
    """id de ajuste -> definición, saltando headers y párrafos."""
    return {s["id"]: s for s in esquema.get("settings", []) if s.get("id")}


# Valores fuera del selector que sí funcionan, con el motivo verificado.
# Se listan aquí para que el informe no los repita como si fueran defectos.
TOLERADOS = {
    # typography-style.liquid emite --font-size: <valor> tal cual, y estas dos
    # variables existen en :root. El selector sólo ofrece medidas fijas, pero
    # atarlas a la escala tipográfica es deliberado.
    ("font_size", "var(--font-size--h6)"),
    ("font_size", "var(--font-size--h4)"),
    # Dato muerto que viene del propio tema base: --font-primary--family no
    # está definida, pero el snippet sólo lee 'font' cuando type_preset es
    # 'custom', y en esos bloques es h2/h3/rte. Nunca llega al CSS.
    ("font", "var(--font-primary--family)"),
}


def revisar(valor, definicion):
    """Devuelve el motivo del problema, o None si el valor es válido."""
    tipo = definicion.get("type")

    if (definicion.get("id"), valor) in TOLERADOS:
        return None

    # Los valores plantilla los resuelve Shopify al renderizar.
    if isinstance(valor, str) and "{{" in valor:
        return None

    if tipo == "select":
        permitidos = [o.get("value") for o in definicion.get("options", [])]
        if valor not in permitidos:
            return f"no está entre {permitidos}"

    elif tipo == "range":
        if not isinstance(valor, (int, float)) or isinstance(valor, bool):
            return "debería ser un número"
        minimo, maximo, paso = definicion["min"], definicion["max"], definicion["step"]
        if valor < minimo or valor > maximo:
            return f"fuera del rango {minimo}–{maximo}"
        # Shopify rechaza los valores que no caen en un escalón exacto.
        pasos = (valor - minimo) / paso
        if abs(pasos - round(pasos)) > 1e-9:
            return f"no cae en un escalón de {paso} desde {minimo}"

    elif tipo == "checkbox":
        if not isinstance(valor, bool):
            return "debería ser verdadero o falso"

    return None


def recorrer(nodo, esquemas, ruta, hallazgos, omitidos):
    for bid, bloque in (nodo or {}).items():
        tipo = bloque.get("type")
        esquema = esquemas["blocks"].get(tipo)
        aqui = f"{ruta}/{bid}"
        if esquema is None:
            omitidos.add(tipo)
        else:
            validar_ajustes(bloque.get("settings", {}), indexar(esquema),
                            aqui, tipo, hallazgos)
        recorrer(bloque.get("blocks"), esquemas, aqui, hallazgos, omitidos)


def validar_ajustes(ajustes, indice, ruta, tipo, hallazgos):
    for clave, valor in (ajustes or {}).items():
        definicion = indice.get(clave)
        if definicion is None:
            # Un ajuste que el esquema no declara lo descarta el importador.
            hallazgos.append((ruta, tipo, clave, valor, "no existe en el esquema"))
            continue
        motivo = revisar(valor, definicion)
        if motivo:
            hallazgos.append((ruta, tipo, clave, valor, motivo))


def main():
    esquemas = cargar_esquemas()
    hallazgos, omitidos = [], set()

    for ruta in sorted(glob.glob(os.path.join(THEME, "**", "*.json"), recursive=True)):
        if "settings_data" in ruta:
            continue
        rel = os.path.relpath(ruta, THEME)
        datos = cargar_json(ruta)
        for sid, seccion in datos.get("sections", {}).items():
            tipo = seccion.get("type")
            esquema = esquemas["sections"].get(tipo)
            aqui = f"{rel}:{sid}"
            if esquema is None:
                omitidos.add("section/" + str(tipo))
            else:
                validar_ajustes(seccion.get("settings", {}), indexar(esquema),
                                aqui, tipo, hallazgos)
            recorrer(seccion.get("blocks"), esquemas, aqui, hallazgos, omitidos)

    for ruta, tipo, clave, valor, motivo in hallazgos:
        print(f"  {ruta}\n      [{tipo}] {clave} = {valor!r}\n      {motivo}")

    print(f"\n{len(hallazgos)} problemas")
    if omitidos:
        print("sin esquema (no verificados):", " ".join(sorted(map(str, omitidos))))
    return 1 if hallazgos else 0


if __name__ == "__main__":
    sys.exit(main())

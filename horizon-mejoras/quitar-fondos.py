#!/usr/bin/env python3
"""Quita el fondo a las fotos de todos los productos de la tienda.

Descarga cada imagen, le recorta el fondo de estudio, y —si se lo pides—
sube la versión recortada a Shopify y retira la original.

Por qué existe este archivo en vez de estar hecho ya: el entorno donde se
genera este repositorio no tiene salida a `cdn.shopify.com` (la política de
red devuelve 403), así que desde ahí es imposible descargar las imágenes.
Tu computadora sí llega. Shopify tampoco expone su quitafondos por API: se
listaron **todas** las mutaciones del esquema en vivo de la tienda y no hay
ninguna que quite fondos —ni `imageRemoveBackground`, ni `fileRemoveBackground`,
ni `mediaRemoveBackground`, ni `productImageRemoveBackground`, ni un campo
`removeBackground` en `FileUpdateInput`—. El quitafondos del admin es de la
interfaz, no de la API, así que no se puede automatizar desde fuera.

    pip install pillow requests

    export SHOPIFY_TIENDA=levelupmx.myshopify.com
    export SHOPIFY_TOKEN=shpat_xxxxxxxx

    python3 quitar-fondos.py              # prueba: no toca la tienda
    python3 quitar-fondos.py --aplicar    # sube y reemplaza

Sin `--aplicar` no escribe nada en Shopify: descarga, recorta, deja los
archivos en ./fondos/ y escribe un informe para que puedas mirarlos antes.
"""

import argparse
import io
import json
import os
import sys
import time
import urllib.request

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter
except ImportError:
    sys.exit("Falta Pillow.  pip install pillow")

API = "2025-01"
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fondos")

# Cuánto puede alejarse un píxel del color del fondo y seguir contando como
# fondo. 32 sobre 255 aguanta la sombra suave y el degradado de un ciclorama
# sin empezar a comerse la prenda.
TOLERANCIA = 32

# Umbrales para decidir si una foto es de estudio. Una foto de modelo en la
# calle no se recorta: el fondo es parte de la imagen y quitarlo deja a la
# persona flotando, que se ve peor que dejarlo.
BORDE_MIN_LUZ = 222      # el marco tiene que ser claro
BORDE_MAX_RUIDO = 20     # y parejo


# --------------------------------------------------------------------------
# Shopify
# --------------------------------------------------------------------------

def api(consulta, variables=None):
    tienda = os.environ.get("SHOPIFY_TIENDA")
    token = os.environ.get("SHOPIFY_TOKEN")
    if not tienda or not token:
        sys.exit("Faltan SHOPIFY_TIENDA y/o SHOPIFY_TOKEN. Mira el README.")

    cuerpo = json.dumps({"query": consulta, "variables": variables or {}}).encode()
    peticion = urllib.request.Request(
        f"https://{tienda}/admin/api/{API}/graphql.json",
        data=cuerpo,
        headers={"Content-Type": "application/json", "X-Shopify-Access-Token": token},
    )
    with urllib.request.urlopen(peticion, timeout=60) as r:
        datos = json.load(r)

    if "errors" in datos:
        sys.exit("Shopify devolvió un error:\n" + json.dumps(datos["errors"], indent=2))
    return datos["data"]


LISTAR = """
query Listar($cursor: String) {
  products(first: 50, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes {
      id title handle
      media(first: 250) {
        nodes {
          id mediaContentType status
          ... on MediaImage { image { url width height altText } }
        }
      }
    }
  }
}
"""


def listar_productos():
    productos, cursor = [], None
    while True:
        d = api(LISTAR, {"cursor": cursor})["products"]
        productos += d["nodes"]
        if not d["pageInfo"]["hasNextPage"]:
            return productos
        cursor = d["pageInfo"]["endCursor"]


def descargar(url):
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read()


# --------------------------------------------------------------------------
# El recorte
# --------------------------------------------------------------------------

def _pixeles_del_borde(img, grosor=2):
    an, al = img.size
    px = img.load()
    fuera = []
    for x in range(an):
        for y in range(grosor):
            fuera.append(px[x, y])
            fuera.append(px[x, al - 1 - y])
    for y in range(al):
        for x in range(grosor):
            fuera.append(px[x, y])
            fuera.append(px[an - 1 - x, y])
    return fuera


def es_de_estudio(img):
    """¿El marco de la foto es un fondo liso y claro?

    Devuelve (sí/no, color del fondo, motivo). Es lo que separa una foto de
    catálogo —prenda sobre ciclorama— de una foto de modelo en la calle, que
    no hay que tocar.
    """
    borde = _pixeles_del_borde(img)
    n = len(borde)
    medio = tuple(sum(c[i] for c in borde) // n for i in range(3))

    luz = sum(medio) / 3
    if luz < BORDE_MIN_LUZ:
        return False, medio, f"el marco es oscuro (luz {luz:.0f})"

    # Ruido = qué tanto se aleja el píxel típico del color medio. Un
    # ciclorama da 2-8; una calle o un interior se disparan.
    ruido = sum(max(abs(c[i] - medio[i]) for i in range(3)) for c in borde) / n
    if ruido > BORDE_MAX_RUIDO:
        return False, medio, f"el marco no es liso (ruido {ruido:.0f})"

    return True, medio, f"fondo liso {medio}, ruido {ruido:.0f}"


def recortar(img, color_fondo, tolerancia=TOLERANCIA):
    """Devuelve la imagen en RGBA con el fondo en transparente.

    No basta con borrar todo lo que se parezca al fondo: eso se comería el
    blanco de dentro de la prenda —una suela, un logo, el hueco de un asa—.
    Sólo se borra lo que además esté **pegado al borde**, y para eso se
    rellena desde las cuatro esquinas.
    """
    rgb = img.convert("RGB")

    # Mapa de "se parece al fondo": 255 donde sí.
    plano = Image.new("RGB", rgb.size, color_fondo)
    distancia = ImageChops.difference(rgb, plano).convert("L")
    parecido = distancia.point(lambda v: 255 if v <= tolerancia else 0)

    # De todo lo parecido, quedarse sólo con lo conectado a las esquinas.
    an, al = rgb.size
    for esquina in ((0, 0), (an - 1, 0), (0, al - 1), (an - 1, al - 1)):
        if parecido.getpixel(esquina) == 255:
            ImageDraw.floodfill(parecido, esquina, 128, thresh=0)

    # 128 = fondo de verdad. Todo lo demás se queda.
    alfa = parecido.point(lambda v: 0 if v == 128 else 255)

    # Encoger un píxel antes de suavizar: el borde de un recorte sobre blanco
    # arrastra un halo claro, y comerse ese píxel lo quita. Después un
    # desenfoque mínimo para que el filo no quede dentado.
    alfa = alfa.filter(ImageFilter.MinFilter(3))
    alfa = alfa.filter(ImageFilter.GaussianBlur(0.8))

    salida = rgb.convert("RGBA")
    salida.putalpha(alfa)
    return salida


def proporcion_borrada(rgba):
    alfa = rgba.getchannel("A")
    histograma = alfa.histogram()
    transparentes = sum(histograma[:16])
    return transparentes / float(rgba.size[0] * rgba.size[1])


# --------------------------------------------------------------------------
# Subida
# --------------------------------------------------------------------------

STAGED = """
mutation Staged($input: [StagedUploadInput!]!) {
  stagedUploadsCreate(input: $input) {
    stagedTargets { url resourceUrl parameters { name value } }
    userErrors { field message }
  }
}
"""

# Adjuntar y borrar se hacen con las mutaciones vigentes. Las de toda la vida
# —productCreateMedia y productDeleteMedia— siguen respondiendo, pero están
# deprecadas y el propio esquema dice con qué sustituirlas:
#
#   productCreateMedia -> "Use `productUpdate` or `productSet` instead."
#   productDeleteMedia -> "Use `fileUpdate` instead."   (para borrar, fileDelete)
#
# productUpdate no devuelve cuál de los medios acaba de crear, así que se pide
# la lista entera y se saca por diferencia contra los que ya había.

ADJUNTAR = """
mutation Adjuntar($product: ProductUpdateInput!, $media: [CreateMediaInput!]) {
  productUpdate(product: $product, media: $media) {
    product { media(first: 250) { nodes { id status } } }
    userErrors { field message }
  }
}
"""

REORDENAR = """
mutation Reordenar($id: ID!, $moves: [MoveInput!]!) {
  productReorderMedia(id: $id, moves: $moves) {
    job { id done }
    mediaUserErrors { field message }
  }
}
"""

BORRAR = """
mutation Borrar($fileIds: [ID!]!) {
  fileDelete(fileIds: $fileIds) {
    deletedFileIds
    userErrors { field message }
  }
}
"""

ESTADO = """
query Estado($id: ID!) {
  node(id: $id) { ... on MediaImage { id status } }
}
"""


def subir_a_shopify(nombre, datos):
    """Sube los bytes a un destino temporal y devuelve su resourceUrl."""
    import requests  # sólo hace falta aquí: el POST es multipart

    destino = api(STAGED, {"input": [{
        "filename": nombre, "mimeType": "image/png",
        "resource": "IMAGE", "httpMethod": "POST",
    }]})["stagedUploadsCreate"]

    if destino["userErrors"]:
        raise RuntimeError(destino["userErrors"])

    objetivo = destino["stagedTargets"][0]
    campos = [(p["name"], (None, p["value"])) for p in objetivo["parameters"]]
    campos.append(("file", (nombre, datos, "image/png")))

    r = requests.post(objetivo["url"], files=campos, timeout=180)
    if r.status_code not in (200, 201, 204):
        raise RuntimeError(f"la subida devolvió {r.status_code}: {r.text[:300]}")

    return objetivo["resourceUrl"]


def esperar_listo(media_id, intentos=40):
    """Shopify procesa la imagen en segundo plano. No se borra la original
    hasta que la nueva esté lista: si algo falla, el producto se queda con
    la foto que tenía y no con ninguna."""
    for _ in range(intentos):
        estado = api(ESTADO, {"id": media_id})["node"]
        if estado and estado["status"] == "READY":
            return True
        if estado and estado["status"] == "FAILED":
            return False
        time.sleep(3)
    return False


def reemplazar(producto_id, media_vieja, posicion, nombre, datos, ya_estaban):
    """Sube el recorte, lo deja en el sitio de la original y retira la vieja.

    `ya_estaban` es el conjunto de ids de medios que el producto tenía antes:
    productUpdate no dice cuál acaba de crear, así que el nuevo es el que
    aparece de más.
    """
    fuente = subir_a_shopify(nombre, datos)

    creado = api(ADJUNTAR, {
        "product": {"id": producto_id},
        "media": [{"originalSource": fuente, "mediaContentType": "IMAGE"}],
    })["productUpdate"]
    if creado["userErrors"]:
        raise RuntimeError(creado["userErrors"])

    ahora = [m["id"] for m in creado["product"]["media"]["nodes"]]
    nuevas = [i for i in ahora if i not in ya_estaban]
    if len(nuevas) != 1:
        raise RuntimeError(
            f"esperaba una foto nueva y aparecieron {len(nuevas)}; "
            "no borro nada para no dejar el producto peor de como estaba"
        )
    nueva = nuevas[0]

    if not esperar_listo(nueva):
        raise RuntimeError("Shopify no terminó de procesar la imagen nueva")

    api(REORDENAR, {"id": producto_id,
                    "moves": [{"id": nueva, "newPosition": str(posicion)}]})

    borrado = api(BORRAR, {"fileIds": [media_vieja]})["fileDelete"]
    if borrado["userErrors"]:
        raise RuntimeError(borrado["userErrors"])

    return nueva


# --------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--aplicar", action="store_true",
                   help="sube los recortes y retira las originales")
    p.add_argument("--producto", metavar="HANDLE",
                   help="sólo este producto, para probar con uno antes")
    p.add_argument("--tolerancia", type=int, default=TOLERANCIA,
                   help=f"cuánto puede variar el fondo (por omisión {TOLERANCIA})")
    p.add_argument("--forzar", action="store_true",
                   help="recorta también las fotos que no parecen de estudio")
    args = p.parse_args()

    os.makedirs(os.path.join(SALIDA, "originales"), exist_ok=True)
    os.makedirs(os.path.join(SALIDA, "recortadas"), exist_ok=True)

    productos = listar_productos()
    if args.producto:
        productos = [x for x in productos if x["handle"] == args.producto]
        if not productos:
            sys.exit(f"No hay ningún producto con el handle {args.producto!r}")

    if args.aplicar:
        total = sum(len(x["media"]["nodes"]) for x in productos)
        print(f"Vas a reemplazar hasta {total} imágenes en {len(productos)} "
              f"productos de {os.environ.get('SHOPIFY_TIENDA')}.")
        print("Las originales quedan guardadas en fondos/originales/ antes de tocar nada.")
        if input("Escribe SI para continuar: ").strip() != "SI":
            sys.exit("Cancelado.")

    informe, recortadas, saltadas, fallidas = [], 0, 0, 0

    for prod in productos:
        medios = [m for m in prod["media"]["nodes"]
                  if m["mediaContentType"] == "IMAGE" and m.get("image")]
        print(f"\n{prod['title']}  ({len(medios)} fotos)")

        # Qué medios tiene el producto ahora mismo. Se va actualizando con
        # cada reemplazo, porque es lo que permite reconocer la foto recién
        # subida entre todas las del producto.
        presentes = {m["id"] for m in prod["media"]["nodes"]}

        for i, medio in enumerate(medios):
            etiqueta = f"{prod['handle']}-{i + 1}"
            try:
                crudo = descargar(medio["image"]["url"])
            except Exception as e:
                print(f"  {i + 1}. no se pudo descargar: {e}")
                fallidas += 1
                continue

            with open(os.path.join(SALIDA, "originales", etiqueta + ".img"), "wb") as fh:
                fh.write(crudo)

            img = Image.open(io.BytesIO(crudo))
            estudio, color, motivo = es_de_estudio(img.convert("RGB"))

            if not estudio and not args.forzar:
                print(f"  {i + 1}. se salta — {motivo}")
                informe.append(f"SALTADA  {etiqueta}  {motivo}")
                saltadas += 1
                continue

            rgba = recortar(img, color, args.tolerancia)
            borrado = proporcion_borrada(rgba)

            # Si borró casi todo o casi nada, algo salió mal. Mejor avisar que
            # subir una silueta vacía.
            if borrado < 0.02 or borrado > 0.92:
                print(f"  {i + 1}. sospechoso, se salta — borró el {borrado:.0%}")
                informe.append(f"SOSPECHA {etiqueta}  borró el {borrado:.0%}")
                saltadas += 1
                continue

            buffer = io.BytesIO()
            rgba.save(buffer, "PNG", optimize=True)
            datos = buffer.getvalue()

            destino = os.path.join(SALIDA, "recortadas", etiqueta + ".png")
            with open(destino, "wb") as fh:
                fh.write(datos)

            if args.aplicar:
                try:
                    nueva = reemplazar(prod["id"], medio["id"], i + 1,
                                       etiqueta + ".png", datos, presentes)
                    presentes.discard(medio["id"])
                    presentes.add(nueva)
                    print(f"  {i + 1}. reemplazada  (fondo {borrado:.0%})")
                except Exception as e:
                    print(f"  {i + 1}. falló al subir: {e}")
                    informe.append(f"ERROR    {etiqueta}  {e}")
                    fallidas += 1
                    continue
            else:
                print(f"  {i + 1}. recortada     (fondo {borrado:.0%})")

            informe.append(f"OK       {etiqueta}  fondo {borrado:.0%}  {motivo}")
            recortadas += 1

    with open(os.path.join(SALIDA, "informe.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(informe) + "\n")

    print(f"\n{recortadas} recortadas, {saltadas} saltadas, {fallidas} con error.")
    print(f"Archivos en {SALIDA}/  ·  detalle en fondos/informe.txt")
    if not args.aplicar:
        print("\nEsto fue una prueba: la tienda no se tocó. Mira las imágenes de")
        print("fondos/recortadas/ y, si te convencen, vuelve a correrlo con --aplicar.")


if __name__ == "__main__":
    main()

# Quitar el fondo de las fotos de producto

## Por qué

Las fotos vienen del proveedor sobre fondo blanco de estudio. Mientras la
tienda tuvo fondo casi blanco (`#FAFAFA`) no se notaba. Ahora que está en
blanco cálido (`#F7F4EF`) cada foto se lee como un rectángulo blanco pegado
sobre el crema.

El tema **no** tiene la culpa: se revisó y ni `.product-media` ni
`.card-gallery` pintan ningún fondo. El rectángulo está dentro del JPG.

Recortarlo aquí no se puede: `cdn.shopify.com` está bloqueado por la política
de red del entorno donde se produce este repositorio, así que no hay forma de
descargar las imágenes, procesarlas y volver a subirlas.

## Ya está borrado desde el tema

`theme/assets/levelup-fondos.css` lo resuelve sin tocar ni una imagen, con
`mix-blend-mode: darken`. El modo se queda, canal por canal, con el valor más
oscuro entre la foto y lo que hay detrás:

- Fondo blanco (255,255,255) contra el crema (247,244,239) → gana el crema en
  los tres canales. **El fondo desaparece exacto.**
- Cualquier píxel más oscuro que el crema → gana la foto, intacta. Un denim
  sale idéntico, sin tinte ni pérdida.

Se eligió `darken` y no `multiply`, que era la opción obvia: multiply oscurece
todo un 4-6% y le mete un velo cálido a la prenda entera. Darken no toca nada
que ya sea más oscuro que la página, que es prácticamente toda la prenda.

El archivo se carga en **todas** las páginas, no sólo en producto, porque las
tarjetas de producto están en todas partes. Va fuera de la condición
`template.name == 'product'` de la sección "Animaciones LevelUP" del pie.

### Los dos casos donde darken no alcanza

1. **Fondos grises en vez de blancos** (por debajo de `#F7F4EF` en algún
   canal): el recuadro se atenúa mucho pero no desaparece del todo.
2. **Productos blancos o muy claros**: se recortan al color de la página, o
   sea que un blanco puro se vería crema. Es el mismo mecanismo que borra el
   fondo — no distingue fondo de prenda. El candidato obvio es el Bolso Seúl,
   que además ya es PNG y puede que venga recortado de origen.

Los dos se arreglan recortando la foto de verdad. Y las dos cosas conviven
sin pelearse: sobre una foto ya recortada, darken no tiene nada blanco que
morder, y la parte transparente deja ver la página igual.

## Recortarlo de verdad, en todos los productos de una pasada

`quitar-fondos.py` hace el trabajo completo: baja cada foto, le recorta el
fondo y —si se lo pides— sube la recortada a Shopify y retira la original.

Hay que correrlo **en tu computadora**. Desde el entorno donde se genera este
repositorio no se puede: la política de red devuelve 403 en
`cdn.shopify.com`, así que las imágenes son inalcanzables desde ahí. Y
Shopify no expone su quitafondos por API — se comprobó contra el esquema:
no existen `imageRemoveBackground`, `fileRemoveBackground`,
`mediaRemoveBackground`, `productImageRemoveBackground`, ni un campo
`removeBackground` en `FileUpdateInput`.

### 1. El token

Admin de Shopify → **Configuración → Aplicaciones y canales de venta →
Desarrollar aplicaciones → Crear una aplicación**. Ponle el nombre que
quieras. En **Configurar ámbitos de Admin API** marca `read_products` y
`write_products`. Guarda, **Instalar**, y copia el token de acceso: empieza
con `shpat_`. Se muestra una sola vez.

### 2. Correrlo

```bash
pip install pillow requests

export SHOPIFY_TIENDA=levelupmx.myshopify.com
export SHOPIFY_TOKEN=shpat_loquetehayadado

python3 quitar-fondos.py                       # prueba, no toca la tienda
python3 quitar-fondos.py --producto stretchy-loose-straight-pants
python3 quitar-fondos.py --aplicar             # sube y reemplaza
```

Sin `--aplicar` **no escribe nada en Shopify**. Descarga, recorta, deja los
archivos en `fondos/recortadas/` y escribe `fondos/informe.txt`. Ábrelos,
míralos, y sólo entonces vuelve a correrlo con `--aplicar`. Con `--aplicar`
pide que escribas `SI` antes de empezar.

### Qué cuida

- **Guarda las originales** en `fondos/originales/` antes de tocar nada.
- **No borra la original hasta que la nueva está lista.** Sube el recorte,
  espera a que Shopify termine de procesarlo (`status: READY`) y sólo
  entonces retira la vieja. Si algo falla a medio camino, el producto se
  queda con la foto que tenía, nunca sin ninguna.
- **Respeta el blanco de dentro de la prenda.** No borra todo lo que se
  parezca al fondo —eso se comería una suela, un logo o el hueco de un asa—
  sino sólo lo que además esté pegado al borde, rellenando desde las cuatro
  esquinas. Está probado con un caso a propósito: un aro oscuro con un hueco
  blanco en medio; el hueco se queda.
- **Se salta las fotos que no son de estudio.** Mide si el marco de la foto
  es liso y claro; una foto de modelo en la calle no pasa el filtro y se
  deja intacta, porque recortarle el fondo deja a la persona flotando.
  `--forzar` lo salta si quieres decidir tú.
- **Avisa cuando el resultado es sospechoso.** Si el recorte borró menos del
  2% o más del 92% de la imagen, no la sube: eso pasa con las prendas
  blancas sobre fondo blanco, donde no hay forma de distinguir una de otro.
  Van al informe para que las hagas a mano.
- **Aguanta el degradado** de un ciclorama y la sombra suave bajo la prenda
  (tolerancia de 32 sobre 255, ajustable con `--tolerancia`).

### Lo que no pude probar

La parte de imagen está probada con seis casos sintéticos —fondo blanco
puro, ciclorama con degradado, blanco encerrado, foto ruidosa, pared con
textura y prenda blanca sobre blanco— y los seis dan lo esperado.

Lo que **no** pude ejecutar es el camino contra Shopify: descargar, subir y
reemplazar. Las consultas y mutaciones están validadas contra el esquema real
de la Admin API (`productCreateMedia`, `productReorderMedia`,
`productDeleteMedia`, `stagedUploadsCreate`), pero nunca corrieron. Por eso
el modo de prueba es el que viene por omisión y por eso conviene empezar con
`--producto` en uno solo. Si algo revienta, mándame el error y lo arreglo.

## A mano, desde el admin (para las que el programa deje fuera)

Shopify ya trae el quitafondos, gratis y sin instalar nada:

**Productos → abre el producto → clic en la imagen → Editar → Quitar fondo →
Guardar.**

Guarda una copia, así que si algo sale mal se puede volver a la original
desde la misma pantalla.

## Por dónde empezar

Son 22 productos y 147 imágenes en total. Hacerlas todas es mucho y, ahora
que el tema ya borra el blanco, **ya no es urgente**: sólo vale la pena en
las fotos donde se note que el fondo no era blanco del todo, y en los
productos claros.

Si aun así quieres hacerlo bien de una vez, este es el orden que rinde:

1. **Las 22 fotos principales.** Son las que salen en portada, colecciones,
   buscador, carrito y recomendados: el 90% del efecto por el 15% del trabajo.
2. **Las 2 o 3 primeras de cada ficha**, que son las que se ven antes de que
   el visitante decida seguir bajando.
3. El resto, si queda ánimo.

| Producto | Fotos |
|---|---|
| Blazer Cruzado Verona · Corte Sastre | 5 |
| Blusa París · Lunares con Olanes | 4 |
| Bolso Firenze · Estructurado de Mano | 11 |
| Bolso Praga · Tote Estampado XL | 10 |
| Bolso Seúl · Hombro Minimalista Blanco | 1 |
| Chaqueta Ivy · Denim Cropped | 6 |
| Chaqueta Margot · Lunares Retro | 6 |
| Chaqueta Sahara · Cropped Khaki | 3 |
| Gabardina Capri · Con Capucha | 6 |
| Hoodie Boston · Zipper Oversize | 11 |
| Jeans Brooklyn · Recto Holgado | 6 |
| Jeans Flare 70 · Corte Retro Hombre | 7 |
| Jeans Graff · Estampado Urbano Hombre | 3 |
| Jeans Nashville · Bootcut Vintage Rasgado | 6 |
| Jeans Runway · Largo Total con Cadena | 6 |
| Jeans Star · Wide-Leg Lavado Vintage | 6 |
| Pantalón Milán · Recto Stretch | 6 |
| Pantalón Osaka · Slim Stretch | 6 |
| Pantalón Sastre Esencial · 12 Colores | 16 |
| Pulsera Éterna · Zircón Engarzado Hombre | 7 |
| Top Amelie · Encaje Entallado | 5 |
| Vestido Noir · Bodycon Sin Mangas | 10 |

## Cuáles NO recortar

- **Fotos con modelo en un escenario real** (calle, interior, exterior). Ahí
  el fondo es parte de la imagen; recortarlo deja a la persona flotando y se
  ve peor que dejarlo. Esas conviene dejarlas tal cual: se leen como foto
  editorial, no como recuadro.
- **Tablas de medidas y fotos de detalle con texto.** El quitafondos puede
  comerse partes del gráfico.
- **Fotos que ya vienen sin fondo** (el Bolso Seúl ya es PNG; puede que no
  necesite nada).

Mezclar recortadas y con escenario en la misma ficha funciona bien: la
recortada manda en la rejilla y las de escenario aportan contexto más abajo.

## Del lado del tema ya está listo

- El blanco de las fotos se funde con la página en la ficha y en todas las
  tarjetas de producto (`levelup-fondos.css`).
- Las fotos caen directamente sobre el fondo de la página, sin caja ni borde
  ni sombra: se comprobó que el tema no pinta ninguna.
- Las esquinas de la galería están en 0, así que un recorte no queda
  redondeado por accidente.
- Se quitó el cuadro gris que Horizon pintaba detrás de la miniatura de la
  barra de compra fija en celular (`--color-background-secondary`), que con
  un PNG recortado se veía como un recuadro alrededor de la prenda.

## Qué avisar después

Tres cosas que hay que mirar y que no se pueden anticipar sin verlas — el
dominio de la tienda está bloqueado desde el entorno donde se generan estos
archivos:

1. **Si algún fondo se resiste.** Darken sólo borra lo que es más claro que
   `#F7F4EF`. Si alguna foto tenía fondo gris, va a quedar un recuadro
   tenue. Mándame cuáles y te digo si conviene recortarlas o subir un pelo la
   claridad de la página.
2. **El recorte de la galería.** La ficha usa proporción vertical (1/1.25) y
   recorta para llenar. Con el fondo ya fundido, la prenda queda más
   expuesta; en los bolsos, que son anchos, puede comerse un borde. Si pasa,
   se cambia la proporción a automática y las fotos se muestran enteras.
3. **El carrito.** No pude verificar si el cajón del carrito pinta un cuadro
   gris detrás de la miniatura, como hacía la barra de compra: el archivo son
   31 KB y no lo abrí entero. Agrega algo al carrito y mándame una captura;
   si aparece el cuadrito, es una línea de CSS.

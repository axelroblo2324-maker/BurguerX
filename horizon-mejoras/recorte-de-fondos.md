# Quitar el fondo de las fotos de producto

## Por qué

Las fotos vienen del proveedor sobre fondo blanco de estudio. Mientras la
tienda tuvo fondo casi blanco (`#FAFAFA`) no se notaba. Ahora que está en
blanco cálido (`#F7F4EF`) cada foto se lee como un rectángulo blanco pegado
sobre el crema.

El tema **no** tiene la culpa: se revisó y ni `.product-media` ni
`.card-gallery` pintan ningún fondo. El rectángulo está dentro del JPG.

Recortarlo desde el generador no se puede: `cdn.shopify.com` está bloqueado
por la política de red del entorno donde se produce este repositorio, así que
no hay forma de descargar las imágenes, procesarlas y volver a subirlas. Hay
que hacerlo desde el admin.

## Cómo

Shopify ya trae el quitafondos, gratis y sin instalar nada:

**Productos → abre el producto → clic en la imagen → Editar → Quitar fondo →
Guardar.**

Guarda una copia, así que si algo sale mal se puede volver a la original
desde la misma pantalla.

## Por dónde empezar

Son 22 productos y 147 imágenes en total. Hacerlas todas es mucho y no hace
falta: **la foto principal es la que aparece en la portada, en las
colecciones, en el buscador, en el carrito y en los recomendados.** Con esas
22 se arregla casi toda la tienda.

Orden sugerido:

1. **Las 22 fotos principales.** Es el 90% del efecto por el 15% del trabajo.
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

- Las fotos caen directamente sobre el fondo de la página, sin caja ni borde
  ni sombra. No hay nada que quitar.
- Las esquinas de la galería están en 0, así que un recorte no queda
  redondeado por accidente.
- Se quitó el cuadro gris que Horizon pintaba detrás de la miniatura de la
  barra de compra fija en celular (`--color-background-secondary`), que con
  un PNG recortado se veía como un recuadro alrededor de la prenda.

## Qué avisar después

Dos cosas que hay que mirar cuando estén las primeras recortadas, y que no
se pueden anticipar sin verlas:

1. **El recorte de la galería.** La ficha usa proporción vertical (1/1.25) y
   recorta para llenar. Con fondo blanco daba igual porque sobraba blanco por
   los lados; con la prenda recortada y centrada puede que se coma un borde,
   sobre todo en los bolsos, que son anchos. Si pasa, se cambia la proporción
   a automática y las fotos se muestran enteras. Dime y lo ajusto.
2. **El carrito.** No pude verificar si el cajón del carrito pinta un cuadro
   gris detrás de la miniatura, como hacía la barra de compra: el archivo son
   31 KB y no lo abrí entero. En cuanto tengas un producto recortado, ábrelo,
   agrégalo al carrito y mándame una captura; si aparece el cuadrito, es una
   línea de CSS.

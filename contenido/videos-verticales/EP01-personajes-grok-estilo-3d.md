# EP01 — PROMPTS DE PERSONAJE · ESTILO FIGURA 3D DE COLECCIÓN (GROK)

Sustituye el STYLE LOCK plano 2D del paquete `EP01-la-hamburguesa-fantasma.md` por el acabado de figura de colección en 3D. Este es el **único cambio de estilo permitido**: una vez aprobado, se mantiene idéntico en todas las escenas.

---

## 1. STYLE_3D — bloque fijo para las fichas de personaje

Va **al inicio** de todo prompt de personaje, sin cambiar ni una palabra:

> Stylized 3D collectible vinyl toy render, chunky rounded designer-toy proportions, mixed soft matte and glossy plastic materials with visible sculpted surface detail, clean studio product photography, seamless light grey backdrop, soft even key light with gentle falloff, subtle contact shadow under the feet, shallow depth of field, crisp high detail, vertical 9:16 composition, subject centered and fully inside the frame, no writing anywhere.

Variante para las escenas (**no** para las fichas): se cambia `clean studio product photography, seamless light grey backdrop` por `cinematic 3D animated movie lighting inside a real set`, y se conserva todo lo demás. Así los personajes siguen siendo la misma figura pero dejan de flotar en un fondo de estudio.

---

## 2. TOKENS DE IDENTIDAD 3D

Idénticos palabra por palabra en cada prompt donde aparezca el personaje. No cambies el orden ni añadas sinónimos.

**TOK_BOB_3D**
> Bob Esponja as a collectible toy figure: square yellow sponge body with soft matte foam texture and deep sculpted round holes, wavy soft edges, rosy blush on both cheeks, large glossy eyes with teal-green irises, thick dark sculpted eyebrows, two big white front teeth, white fabric-look shirt with a collar, red molded tie, brown shorts with a black belt and stitched loops, thin yellow arms and legs, white socks with one blue and one red stripe, glossy black shoes.

**TOK_KRABS_3D**
> Señor Cangrejo as a collectible toy figure: stout red crab with a smooth semi-glossy shell body, two big red claws with pale cream inner edges, six small pointed feet, two long thin eyestalks holding large glossy white eyes with small black pupils, a blunt nose bump, two small white teeth, soft light blue fabric-look shirt with dark blue collar and cuffs, brown belt, blue-grey trousers, no hat.

**TOK_SQUID_3D**
> Calamardo as a collectible toy figure: tall lean turquoise octopus with a soft matte skin finish, a large oval head bulb, a long drooping nose, half-lidded eyelids over glossy yellow eyes with tiny black pupils, four limbs only, two thin arms and two long legs, loose brown-orange fabric-look short-sleeved shirt with a wide collar, barefoot.

**TOK_PATTY_3D**
> Patty Cero as a collectible toy figure: tiny living burger the size of a coffee cup, glossy toasted golden buns with seven sculpted sesame seeds, thick dark patty, wavy green lettuce, flat red tomato slice, yellow cheese corner, two round pickle slices as glossy eyes with small black pupils, a thin glossy ketchup line as a smiling mouth, two short lettuce-stem arms with three-fingered mitten hands, no legs, holding a folded white napkin and a broken toothpick.

---

## 3. CHAR_BOB

**A · Maestro (la referencia que manda sobre todas las demás)**
> [STYLE_3D] Full body character reference, one character only: [TOK_BOB_3D] standing straight in a neutral pose, arms relaxed at his sides, both hands and both shoes fully visible, calm friendly face with a small closed smile, facing the camera straight on. Even soft studio light, faithful colors, plain seamless light grey backdrop, no props, no scenery, no other characters, no writing anywhere.

**B · Vistas (genera tres imágenes separadas, no una hoja)**
> [STYLE_3D] Full body character reference, one character only: [TOK_BOB_3D] standing straight in the exact same neutral pose with arms relaxed at his sides, calm face, seen from **[FRONT VIEW / THREE-QUARTER VIEW / SIDE PROFILE VIEW / BACK VIEW]**. Even soft studio light, plain seamless light grey backdrop, no props, no other characters, no writing anywhere.

**C · Retrato**
> [STYLE_3D] Head and shoulders portrait, one character only: [TOK_BOB_3D] in a soft three-quarter view turned slightly to the left, eyes to camera, calm neutral face with a small closed smile. Even soft studio light, plain seamless light grey backdrop, shallow depth of field, the whole head fully inside the frame, no other characters, no writing anywhere.

**D · Expresiones (una imagen por expresión, siempre el mismo prompt)**
> [STYLE_3D] Full body character reference, one character only: [TOK_BOB_3D] standing in the same neutral stance, arms relaxed at his sides, with a **[NEUTRAL CALM / BIG HAPPY OPEN-MOUTHED / SAD DROOPY / WIDE-EYED SCARED / ANGRY FROWNING / SHOCKED OPEN-MOUTHED]** face. Only the face changes, the body, clothes, colors and proportions stay exactly the same. Even soft studio light, plain seamless light grey backdrop, no props, no other characters, no writing anywhere.

**E · Acción**
> [STYLE_3D] Full body action shot, one character only: [TOK_BOB_3D] leaping with both feet off the ground, catching a long ribbon of blank pale paper with his left hand while a metal spatula stays raised high in his right hand, mouth wide open shouting, eyes huge. The paper is completely blank with no writing anywhere. Plain seamless light grey backdrop, soft studio light, slight low three-quarter angle, no other characters.

---

## 4. CHAR_CANGREJO

**A · Maestro**
> [STYLE_3D] Full body character reference, one character only: [TOK_KRABS_3D] standing straight in a neutral pose, both claws open and relaxed at his sides, all six little feet visible on the ground, eyestalks straight and parallel, calm face, facing the camera straight on. Even soft studio light, faithful colors, plain seamless light grey backdrop, no props, no scenery, no other characters, no writing anywhere.

**B · Vistas (tres imágenes separadas)**
> [STYLE_3D] Full body character reference, one character only: [TOK_KRABS_3D] standing straight in the exact same neutral pose with both claws relaxed at his sides and eyestalks straight, calm face, seen from **[FRONT VIEW / THREE-QUARTER VIEW / SIDE PROFILE VIEW / BACK VIEW]**. Even soft studio light, plain seamless light grey backdrop, no props, no other characters, no writing anywhere.

**C · Retrato**
> [STYLE_3D] Head and upper body portrait, one character only: [TOK_KRABS_3D] in a soft three-quarter view turned slightly to the right, eyestalks upright and fully inside the frame, eyes to camera, calm face. Even soft studio light, plain seamless light grey backdrop, shallow depth of field, no other characters, no writing anywhere.

**D · Expresiones (una imagen por expresión)**
> [STYLE_3D] Full body character reference, one character only: [TOK_KRABS_3D] standing in the same neutral stance with both claws at his sides, with a **[NEUTRAL CALM / GREEDY DELIGHTED / SAD DROOPY / SCARED SHRINKING / ANGRY SHOUTING / SHOCKED WIDE-EYED]** face and matching eyestalk tilt. Only the face and the eyestalks change, the body, shell, clothes, colors and proportions stay exactly the same. Even soft studio light, plain seamless light grey backdrop, no props, no other characters, no writing anywhere.

**E · Acción**
> [STYLE_3D] Full body action shot, one character only: [TOK_KRABS_3D] leaning far forward with both claws thrown wide open, one claw high and one low, all six feet planted apart, eyestalks stretched forward, mouth wide open in a shout. Plain seamless light grey backdrop, soft studio light, slight low three-quarter angle, no other characters, no writing anywhere.

---

## 5. CHAR_CALAMARDO

**A · Maestro**
> [STYLE_3D] Full body character reference, one character only: [TOK_SQUID_3D] standing straight in a neutral pose, arms hanging down at his sides, both hands and both feet fully visible, bored calm face, facing the camera straight on. Even soft studio light, faithful colors, plain seamless light grey backdrop, no props, no scenery, no other characters, no writing anywhere.

**B · Vistas (tres imágenes separadas)**
> [STYLE_3D] Full body character reference, one character only: [TOK_SQUID_3D] standing straight in the exact same neutral pose with arms hanging down, bored calm face, seen from **[FRONT VIEW / THREE-QUARTER VIEW / SIDE PROFILE VIEW / BACK VIEW]**. Even soft studio light, plain seamless light grey backdrop, no props, no other characters, no writing anywhere.

**C · Retrato**
> [STYLE_3D] Head and shoulders portrait, one character only: [TOK_SQUID_3D] in a soft three-quarter view turned slightly to the left, eyes to camera, flat bored face with a thin mouth. Even soft studio light, plain seamless light grey backdrop, shallow depth of field, the whole head bulb inside the frame, no other characters, no writing anywhere.

**D · Expresiones (una imagen por expresión)**
> [STYLE_3D] Full body character reference, one character only: [TOK_SQUID_3D] standing in the same neutral stance with arms hanging down, with a **[NEUTRAL BORED / SMUG PLEASED / MISERABLE SAD / STARTLED SCARED / IRRITATED ANGRY / SURPRISED WIDE-EYED]** face. Only the face changes, the body, skin, shirt, colors and proportions stay exactly the same. Even soft studio light, plain seamless light grey backdrop, no props, no other characters, no writing anywhere.

**E · Acción**
> [STYLE_3D] Full body action shot, one character only: [TOK_SQUID_3D] slumped sideways fast asleep over the edge of a plain wooden counter, cheek squashed against the wood, both arms dangling straight down, eyes closed, one small round air bubble at the tip of his nose. Plain seamless light grey backdrop, soft studio light, slight high three-quarter angle, no other characters, no writing anywhere.

---

## 6. CHAR_PATTY

**A · Maestro**
> [STYLE_3D] Full body character reference, one character only: [TOK_PATTY_3D] resting on a flat surface in a neutral pose, both mitten hands visible, pickle eyes looking straight at the camera, calm face, the folded napkin completely blank. Even soft studio light, faithful colors, plain seamless light grey backdrop, camera at burger height, no props, no other characters, no writing anywhere.

**B · Vistas (tres imágenes separadas)**
> [STYLE_3D] Full body character reference, one character only: [TOK_PATTY_3D] resting in the exact same neutral pose with both mitten hands visible, calm face, seen from **[FRONT VIEW / THREE-QUARTER VIEW / SIDE PROFILE VIEW / BACK VIEW]**, camera at burger height. Even soft studio light, plain seamless light grey backdrop, no props, no other characters, no writing anywhere.

**C · Retrato**
> [STYLE_3D] Close portrait framed from the lower bun upward, one character only: [TOK_PATTY_3D] in a soft three-quarter view turned slightly to the right, pickle eyes looking at the camera, calm face. Even soft studio light, plain seamless light grey backdrop, shallow depth of field, exactly seven sesame seeds visible, no other characters, no writing anywhere.

**D · Expresiones (una imagen por expresión)**
> [STYLE_3D] Full body character reference, one character only: [TOK_PATTY_3D] resting in the same neutral pose, with a **[NEUTRAL CALM / CHEERFUL / DISAPPOINTED / ALARMED / STERN / SURPRISED]** face made only with the pickle eyes and the ketchup mouth line. Only the face changes, the ingredient stack, the seven sesame seeds, the arms, the napkin and the toothpick stay exactly the same. Even soft studio light, plain seamless light grey backdrop, no other characters, no writing anywhere.

**E · Acción**
> [STYLE_3D] Full body action shot, one character only: [TOK_PATTY_3D] leaning forward over the folded white napkin and scribbling on it with the broken toothpick held like a pencil, one mitten hand pressing the napkin flat, pickle eyes narrowed in concentration. The napkin shows only a crude drawn doodle of a square face with two big round eyes, plain paper with a simple drawing and no writing anywhere. Plain seamless light grey backdrop, soft studio light, camera at burger height, no other characters.

---

## 7. LISTA DE DESCARTE PARA EL ACABADO 3D

Grok no acepta prompt negativo: los negativos se aplican al elegir la toma. Descarta y repite si ves:

**De estilo**
1. Acabado plano de dibujo 2D o de cómic en lugar de figura 3D.
2. Textura fotorrealista de esponja de cocina de verdad, o piel humana realista.
3. Peana, base de exhibición, caja de producto, etiqueta o precio.
4. Fondo con decorado, degradado de color fuerte o sombras duras de estudio.
5. Cualquier letra o número en la imagen.

**De identidad — Bob**
6. Agujeros pintados en vez de esculpidos, o cuerpo liso sin agujeros.
7. Cuerpo redondeado en vez de cuadrado, o proporciones más bajas y anchas que la referencia maestra.
8. Falta la corbata roja, el cinturón negro o las rayas azul y roja de los calcetines.
9. Zapatos mate en vez de negro brillante.
10. Cejas de forma distinta a la maestra: es la primera cosa que deriva.

**De identidad — Cangrejo**
11. Caparazón naranja o rosa, cuerpo alto o delgado, piernas humanas.
12. Pinzas iguales entre sí, ojos pegados a la cabeza sin pedúnculo, sombrero añadido.

**De identidad — Calamardo**
13. Más de cuatro extremidades, ventosas, nariz corta, ojos completamente abiertos y redondos, calzado añadido.

**De identidad — Patty Cero**
14. Tamaño de hamburguesa normal en vez de tamaño taza, piernas añadidas, ojos que no sean rodajas de pepinillo, número de semillas distinto de siete, comida fotorrealista.

**De continuidad entre personajes**
15. Que el nivel de brillo o la luz de estudio cambien entre las cuatro fichas maestras: deben parecer fotografiadas en la misma sesión.

---

## 8. ORDEN DE TRABAJO RECOMENDADO

1. Genera **solo el maestro de Bob** y repite hasta que uno te convenza del todo. Ese archivo es la vara de medir de todo el episodio.
2. Con el maestro aprobado, genera los tres maestros restantes **el mismo día y sin cambiar el bloque STYLE_3D**, para que compartan luz y acabado.
3. Recién entonces vistas, retratos, expresiones y acción.
4. Cuando los cuatro maestros estén aprobados, se cambia STYLE_3D en los nueve prompts de escena usando la variante cinematográfica del bloque 1.

Nota sobre las vistas: Grok falla con frecuencia al pedirle una hoja de cuatro vistas en una sola imagen. Sale mejor generar **una imagen por vista** con el mismo prompt y solo cambiar la palabra de la vista, que es como está escrito el bloque B de cada personaje.

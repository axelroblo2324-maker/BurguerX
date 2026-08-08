# EP01 — GUÍA DE PRODUCCIÓN CON GROK
Adaptación operativa del paquete `EP01-la-hamburguesa-fantasma.md` para generar imágenes y video con Grok Imagine.

> **Nota de verificación.** Grok Imagine cambia de versión con frecuencia. Los límites concretos (duración máxima de clip, selector de formato, número de generaciones por día, audio automático, edición de imagen existente) dependen de la versión y del plan que tengas activo: **[VERIFICAR]** en tu propia cuenta antes de planificar el lote. Todo lo demás de esta guía funciona igual en cualquier versión.

---

## 1. QUÉ CAMBIA AL USAR GROK

| El paquete asume | Grok Imagine | Qué hacemos |
|---|---|---|
| Campo de prompt negativo separado | No existe | Los negativos se convierten en **afirmaciones positivas** dentro del prompt («papel en blanco con un dibujo simple») y en criterio de descarte al elegir la toma |
| Prompts largos de 300–400 palabras con DNA completo | Rinde mejor con prompts cortos y concretos | Se usan **tokens de identidad** de 30–40 palabras + acción + entorno; total 70–110 palabras |
| Bloqueo de personaje / imagen de referencia / seed | Sin bloqueo fiable ni seed reutilizable | Consistencia por **token idéntico palabra por palabra** en los nueve prompts + lote de descarte agresivo |
| Clips de duración exacta (3,5 / 4,0 / 4,5 / 5,0 / 5,5 s) | Clips de duración fija corta, del orden de 6 s **[VERIFICAR]** | Se genera el clip completo y se **recorta en edición** al valor exacto del guion |
| Audio propio en post | Grok puede añadir audio generado **[VERIFICAR]** | Se **silencia siempre** la pista de Grok; el audio del episodio se arma aparte |
| Texto prohibido dentro de la imagen | Tiende a inventar letras en papeles y carteles | Los tickets y la servilleta llevan **solo un garabato**; si aparecen letras, se descarta la toma (no se arregla en edición) |

**Regla de oro con Grok:** los personajes se mantienen iguales por repetición literal del token, no por memoria. No cambies ni una palabra del token entre escenas, ni el orden.

---

## 2. FLUJO DE TRABAJO EN 7 PASOS

**Paso 1 · Hojas de personaje (30–45 min).**
Genera primero las cuatro referencias maestras, una por personaje, con los prompts del bloque 4.1. Guarda la mejor de cada uno como `REF_BOB.png`, `REF_KRABS.png`, `REF_SQUID.png`, `REF_PATTY.png`. No sirven para que Grok las «recuerde»: sirven para que **tú** compares y descartes derivas.

**Paso 2 · Los nueve stills, todos antes de animar nada (1,5–2,5 h).**
Genera S01 a S09 con los prompts del bloque 4.2. Cuatro intentos por escena como mínimo. Guarda como `S01.png` … `S09.png`.
No animes ninguno hasta terminar los nueve.

**Paso 3 · Pasada de continuidad sobre los stills (20 min).**
Pon los nueve en una carpeta y míralos en fila, en el móvil, a tamaño real. Revisa con la lista del bloque 5. Cualquier still que falle, se regenera ahora: **arreglar continuidad después de animar cuesta el triple**.

**Paso 4 · Animación imagen-a-video (1–2 h).**
Sube cada still aprobado a Grok y anima con el prompt del bloque 4.3. Dos o tres intentos por escena. Guarda como `V01.mp4` … `V09.mp4`.
Criterio de descarte: si la cara se deforma, si aparece un personaje nuevo o si el objeto clave (ticket, moneda, espátula, servilleta) se desdibuja, se repite.

**Paso 5 · Audio (40–60 min).**
- Voces: TTS en español latino con tres voces distintas siguiendo el diseño de la sección 16 del paquete (Bob agudo y rápido, Cangrejo grave y rasposo, Calamardo monótono). Exporta cada línea como archivo suelto, nombrado por timecode.
- Patty Cero **no habla**: solo el chirrido de servilleta y la campanilla.
- Música: una pista instrumental de misterio cómico, sin voces, que aguante 40 s.
- Efectos: los 27 puntos de la sección 18 del paquete.

**Paso 6 · Montaje (1–1,5 h).** Ver bloque 6.

**Paso 7 · Exportación y control final (15 min).** Ver bloque 7.

Tiempo total realista la primera vez: **5 a 7 horas**. A partir del segundo episodio, con los tokens ya probados, baja a 3 o 4.

---

## 3. CÓMO SE COMPRIME UN PROMPT DEL PAQUETE

Antes (paquete original, para motores con negativo):
> Vertical 9:16 medium close shot, slightly low angle, exactly one character. Bob Esponja. CHARACTER_DNA_BOB: … *(103 palabras)* … STYLE LOCK: … *(85 palabras)* … No text, no letters…
> **+ prompt negativo aparte de 120 palabras.**

Después (versión Grok, todo en uno, 95 palabras):
> 2D underwater cartoon comedy style, bold black outlines, flat saturated colors, simple readable shapes, bright even lighting, vertical 9:16 … Medium close shot … one character only: Bob Esponja, small rectangular yellow porous sea sponge … catching a long ribbon of **blank** paper … the top ticket shows **only a crude drawn doodle** of a square face with two big round eyes, plain paper with a simple drawing and **no writing anywhere**.

Las tres conversiones que importan:
1. «no text, no letters» → **«blank paper with a simple drawing, no writing anywhere»** (afirmativo primero, prohibición al final).
2. «no additional characters» → **«one character only»** al principio del prompt, donde pesa más.
3. «no identity drift» → **token idéntico repetido**, no una instrucción.

---

## 4. PACK DE PROMPTS PARA GROK

### 4.0 Bloques fijos — cópialos exactamente igual siempre

**STYLE (va al inicio de todo prompt de imagen):**
> 2D underwater cartoon comedy style, bold black outlines, flat saturated colors, simple readable shapes, bright even lighting, vertical 9:16 composition, subject centered, empty space in the lower third, clean image with no writing anywhere.

**TOK_BOB:**
> Bob Esponja, small rectangular yellow porous sea sponge, big round blue eyes, two square front teeth, three freckles per cheek, white shirt with red tie, brown square shorts, black shoes, folded white paper cook hat, metal spatula.

**TOK_KRABS:**
> Señor Cangrejo, short stout red cartoon crab, barrel shell body, two big red claws, long thin eyestalks with white eyes, light blue shirt with dark blue collar, brown belt, no hat.

**TOK_SQUID:**
> Calamardo, tall lean turquoise cartoon octopus, long drooping nose, half-lidded yellow eyes, four limbs, loose brown-orange short-sleeved shirt, barefoot.

**TOK_PATTY:**
> Patty Cero, tiny living cartoon burger the size of a cup, golden sesame buns, two pickle-slice eyes, thin ketchup smile, two little lettuce-stem arms with mitten hands, no legs, holding a folded white napkin and a broken toothpick.

### 4.1 Referencias de personaje

**REF_BOB**
> [STYLE] Full body character reference, one character only: [TOK_BOB] standing straight in a neutral pose, arms down, both hands and both shoes fully visible, calm face, facing the camera. Plain flat grey background, even soft light, no props, no scenery, no other characters, no writing anywhere.

**REF_KRABS**
> [STYLE] Full body character reference, one character only: [TOK_KRABS] standing straight in a neutral pose, both claws open and relaxed at his sides, all six little feet visible, eyestalks straight, calm face, facing the camera. Plain flat grey background, even soft light, no props, no other characters, no writing anywhere.

**REF_SQUID**
> [STYLE] Full body character reference, one character only: [TOK_SQUID] standing straight in a neutral pose, arms hanging down, both hands and both feet fully visible, bored calm face, facing the camera. Plain flat grey background, even soft light, no props, no other characters, no writing anywhere.

**REF_PATTY**
> [STYLE] Full body character reference, one character only: [TOK_PATTY] resting on a flat surface in a neutral pose, both mitten hands visible, pickle eyes looking at the camera, calm face. The napkin is completely blank and folded. Plain flat grey background, even soft light, no other characters, no writing anywhere.

### 4.2 Los nueve stills

**S01 · 3,5 s**
> [STYLE] Medium close shot, slightly low angle, one character only: [TOK_BOB] jumping with both feet off the ground in a bright undersea burger kitchen at midday, catching a long ribbon of blank pale paper with his left hand while the spatula stays raised in his right hand, mouth wide open shouting, eyes huge with tiny pupils. A wall printer on the left is spitting out the paper ribbon, which arcs across the frame. The top ticket faces the camera and shows only a crude drawn doodle of a square face with two big round eyes, plain paper with a simple drawing and no writing anywhere. Steel griddle glowing orange on the left, red and white checkerboard floor, warm hanging lamps, spatulas on a rail.

**S02 · 4,0 s**
> [STYLE] Medium two-shot, eye level, exactly two characters. On the right in the foreground: [TOK_KRABS] bursting in and holding up a torn paper ticket in the center of the frame with his right claw, eyestalks stretched forward, mouth wide open shouting. On the left behind him: [TOK_BOB] with a crumpled ribbon of paper in his left hand, eyebrows pinched together, pointing at the ticket with one finger. The held ticket faces the camera and shows only a crude drawn doodle of a square face with two big round eyes, plain paper with a simple drawing and no writing anywhere. Same bright undersea burger kitchen at midday, orange griddle glow, wall printer, checkerboard floor.

**S03 · 4,0 s**
> [STYLE] Wide shot of a dining room seen from inside a kitchen through a square service window, exactly two characters. On the left, framed by the window: [TOK_BOB] leaning his head and shoulders through, eyes narrowed, crooked doubtful mouth, scanning the room. Far away on the right: [TOK_SQUID] slumped fast asleep across a wooden cashier counter, cheek on the wood, arms dangling, eyes closed, one small air bubble at his nose. Between them six completely empty round tables with low stools and no customers at all. Wooden plank walls with rope trim, three portholes with deep blue underwater light, one warm hanging lantern, an old brass cash register, a plain blank wooden sign with no writing anywhere.

**S04 · 4,0 s**
> [STYLE] Macro close shot at counter level, low angle, shallow depth of field. In sharp focus: a single plain gold coin spinning on its edge on a steel kitchen counter, completely smooth with no engraving and no writing anywhere. Entering from the right, closing on the coin: the left claw of [TOK_KRABS], his face just behind with crossed eyestalks and a disbelieving open grin, a torn paper ticket in his other claw. Far in the blurred background on the left: [TOK_BOB] with a round open mouth. A wall printer with a small red bulb sits softly blurred behind the coin. Bright undersea burger kitchen at midday, warm orange griddle glow.

**S05 · 4,5 s**
> [STYLE] Lateral American shot, eye level, exactly two characters. On the left: a metal spatula floating in mid air all by itself over a long steel griddle, flipping a burger patty caught in mid air, with a visible empty hook on the spatula rail behind it and no hand touching it. In the center: [TOK_BOB] stepping backward, one eyebrow up and one down, mouth drawn as a wavy line. At the right edge: [TOK_KRABS] with a plain gold coin gripped in his left claw and a torn paper ticket in his right claw, both eyestalks locked on the griddle. Bright undersea burger kitchen at midday, sizzle sparks, checkerboard floor, warm lamps, no writing anywhere.

**S06 · 4,5 s**
> [STYLE] Over-the-shoulder medium shot, slightly low angle, exactly two characters seen from behind in three-quarter view. In the center: [TOK_BOB] with his right hand gripping a heavy metal lever handle, spatula tucked under his other arm, shoulders raised, teeth clenched, eyes very wide. Pressed behind his right shoulder: [TOK_KRABS] with a plain gold coin in his left claw and a torn ticket in his right claw, one eyestalk curled back in fear. In front of them a big heavy freezer door bulges outward in a shallow dent with frost cracks around a small round frosted window, cold vapor leaking along the floor. Bright undersea burger kitchen at midday, checkerboard floor, warm lamps, a completely plain door with no signs and no writing anywhere.

**S07 · 5,0 s**
> [STYLE] Low angle shot taken at burger height inside a small walk-in freezer, exactly two characters. In the center on a frosted crate: [TOK_PATTY] leaning forward, scribbling on the folded white napkin with the broken toothpick, pickle eyes lowered in concentration, about to drop the napkin into a low wall vent at the bottom left. The napkin shows only a crude drawn doodle of a square face with two big round eyes, plain paper with a simple drawing and no writing anywhere. On the right, crouching and eight times taller: [TOK_BOB] with a thin white frost dusting on his paper cook hat and shoulders, frozen stiff, tiny pupils, trembling open mouth. Ice-blue frosted metal walls, steel shelves, hanging frozen kelp, ice-crusted floor, low cold vapor, one caged pale cyan bulb, a metal tray heaped with plain gold coins on a back shelf.

**S08 · 5,5 s**
> [STYLE] Worm-eye low angle from the freezer floor, exactly two characters. On the right, towering in strong low angle: [TOK_KRABS] with both claws thrown wide, mouth open in delight, eyestalks stretched to full length, a plain gold coin still gripped in his left claw, loose gold coins piling around his six feet. Small in the left background on a frosted crate: [TOK_PATTY] calm and formal, both mitten hands pressed against the rim of a tipped metal tray. A wide avalanche of plain smooth gold coins pours diagonally from the upper left toward the camera, coins caught mid air and mid roll, with no engraving and no writing anywhere. Ice-blue frosted freezer, steel shelves, hanging frozen kelp, one caged cyan bulb, a strip of warm kitchen light spilling from the open doorway at the right edge.

**S09 · 5,0 s**
> [STYLE] Medium three-shot, eye level, with a paper ticket sharp in the left foreground, exactly three characters. On the right: [TOK_KRABS] shaking a thin lettuce-stem arm with his right claw, a plain gold coin still in his left claw, his proud grin dropping into alarm, eyestalks snapping to the left. In the center, sitting on the steel counter: [TOK_PATTY] impassive, pickle eyes aimed straight at the camera. In the left background: [TOK_BOB] with a thin white frost dusting on his paper cook hat and shoulders, mouth open, one arm pointing at the printer. At the left edge a wall printer has just fired a fresh ticket that curls toward the camera, and the ticket shows only a crude drawn doodle of a round crab face with two claws and two stalk eyes, plain paper with a simple drawing and no writing anywhere. Bright undersea burger kitchen at midday, and at the back an open freezer door with cold blue light and scattered gold coins on its floor.

### 4.3 Los nueve prompts de animación

Sube el still aprobado y usa el prompt correspondiente. Todos terminan con la misma coletilla de bloqueo: **«Keep the exact same character design, same clothes, same colors, same room. No new characters, no writing appearing anywhere.»**

**V01 (recortar a 3,5 s)** — The printer keeps firing paper so the ribbon grows longer and whips in a wide S curve while Bob lands on both feet and pulls the ribbon to his chest, mouth still open shouting, spatula still raised. Slow steady push in. Heat shimmer over the griddle, a few small bubbles drifting. + coletilla.

**V02 (4,0 s)** — The crab thrusts the ticket forward toward the camera and shakes it twice while shouting, eyestalks quivering; the sponge leans in behind and keeps pointing at the drawing. Camera holds steady after a small settle. The paper flexes as it is shaken. + coletilla.

**V03 (4,0 s)** — The sponge slowly turns his head and sweeps his gaze across the empty room from left to right, ending on the sleeping octopus, who does not wake and only breathes once as the small bubble at his nose grows and pops. Slow push in toward the empty tables, the hanging lantern swaying slightly. + coletilla.

**V04 (4,0 s)** — The coin rolls a short arc across the counter, wobbles, and the claw catches it and lifts it for a quick testing bite; the eyestalks cross inward to follow it and the mouth opens into a grin. Camera tracks the rolling coin then brakes. A highlight sweeps across the coin, which stays completely smooth. + coletilla.

**V05 (4,5 s)** — The floating spatula finishes the flip, catches the falling patty and presses it onto the griddle with a puff of steam, with no hand ever touching it; the sponge takes one more small step back and the crab leans forward slightly. Short lateral camera move to the left. Sizzle sparks and rising steam. + coletilla.

**V06 (4,5 s)** — The freezer door bulges outward twice more with heavy impacts, then the sponge slowly pulls the lever down until the door cracks open a finger's width and a thin blade of pale cyan light and cold vapor pours out; nothing inside is visible yet. Slow continuous push in toward the lever, with a tiny jolt on each impact. Frost dust falling. + coletilla.

**V07 (5,0 s)** — The tiny burger finishes one last scribble, turns its body and drops the napkin so it flutters down through the low wall vent, then picks up a fresh napkin; the pickle eyes lift level and the ketchup smile stays calm, while the frozen sponge only trembles and his mouth opens wider. Slow continuous push in from wide to tight on the napkin and the vent. Cold vapor drifting, kelp swaying. The napkin keeps only its simple drawing. + coletilla.

**V08 (5,5 s)** — The metal tray tips fully over and a wide avalanche of smooth gold coins pours diagonally toward the camera and washes over the crab's feet; his eyestalks stretch, his mouth opens wider in delight and both claws snap open and shut twice, while the tiny burger stays composed and only tilts forward. Small backward camera drift with a light shake when the coins reach the lens. Coins spinning and rolling in the foreground. + coletilla.

**V09 (5,0 s)** — Everyone holds still for a beat, then the printer fires a fresh ticket that curls toward the camera: the handshake stops mid motion, the crab's grin drops into alarm and his eyestalks snap left, the sponge lifts his arm to point, and the tiny burger simply turns its pickle eyes to the camera. Fast whip pan to the left that brakes on a tight framing of the new ticket, which keeps only its simple crab drawing. + coletilla.

---

## 5. LISTA DE DESCARTE (aplícala a cada generación)

Descarta y repite si ves cualquiera de estas ocho cosas. No negocies con una toma fallada: en un video de 40 s cada error se ve.

1. **Letras o números** en cualquier papel, cartel, moneda o pared.
2. **Número de personajes equivocado**: uno de más, uno de menos, o un clon del mismo personaje al fondo.
3. **Deriva de identidad**: Bob sin gorro o sin corbata roja, Cangrejo con sombrero o camisa de otro color, Calamardo con más de cuatro extremidades, Patty Cero con piernas o con ojos que no sean pepinillo.
4. **Props perdidos**: la espátula de Bob, la moneda en la pinza izquierda desde S04, la servilleta y el palillo de Patty.
5. **Escala rota**: Patty Cero debe medir como una taza junto a Bob, nunca como una hamburguesa de tamaño normal.
6. **Luz equivocada**: cocina siempre cálida de mediodía, congelador siempre cian frío. Nada de escenas nocturnas.
7. **Manos deformes** o dedos de más en un primer plano.
8. **Sujeto o texto en el tercio inferior**: ahí van los subtítulos.

Y dos específicos de continuidad que se cuelan fácil:
- Bob **sin escarcha** en S07, S08 y S09 → repetir.
- El congelador **sin monedas en el suelo** al fondo de S09 → repetir.

---

## 6. MONTAJE (CapCut, DaVinci Resolve o el editor que uses)

**6.1 Proyecto:** 1080 × 1920, 30 fps, 40,0 s exactos.

**6.2 Colocación y recorte.** Los clips de Grok salen más largos que la escena; recorta **conservando el arranque** de cada clip, que es la parte más estable, y corta antes de que empiece cualquier deformación.

| Clip | Entra en | Sale en | Duración final |
|---|---|---|---|
| V01 | 00,0 | 03,5 | 3,5 s |
| V02 | 03,5 | 07,5 | 4,0 s |
| V03 | 07,5 | 11,5 | 4,0 s |
| V04 | 11,5 | 15,5 | 4,0 s |
| V05 | 15,5 | 20,0 | 4,5 s |
| V06 | 20,0 | 24,5 | 4,5 s |
| V07 | 24,5 | 29,5 | 5,0 s |
| V08 | 29,5 | 35,0 | 5,5 s |
| V09 | 35,0 | 40,0 | 5,0 s |

**6.3 Silencia todos los clips de Grok.** El audio generado no coincide con el diseño sonoro y arruina el ritmo.

**6.4 Transiciones.** Todas son **cortes secos**, salvo tres: whip-pan corto de entrada en 03,5, match cut de brillo moneda→plancha en 15,5, y whip-pan en 35,0. En vertical, las transiciones vistosas cuestan retención: no agregues ninguna más.

**6.5 Voces.** Coloca las 11 líneas en los timecodes exactos de la sección 16 del paquete (00,9 / 04,4 / 08,6 / 13,2 / 17,0 / 21,0 / 22,6 / 27,2 / 32,4 / 36,0 / 38,2). Si una voz te queda 2 décimas larga, **acelérala un 3–5 %** en vez de mover el corte: la imagen manda.

**6.6 Subtítulos.** No uses el autosubtitulado tal cual: genera y luego **corrige contra la tabla de la sección 17**, que ya está partida en bloques de 2 a 5 palabras con la palabra enfatizada. Fuente gruesa con borde, al 12 % del borde inferior, palabra destacada al 130 % y en color distinto. Nunca dos líneas de más de 5 palabras.

**6.7 Efectos.** Los 27 puntos de la sección 18. Los tres que más rinden si tienes poco tiempo: el chirrido de impresora en 00,0 (antes que la música), el **silencio total de 23,9 a 24,5** y la avalancha de monedas en 29,8.

**6.8 El loop.** El corte de 39,9 a 00,0 debe ser instantáneo: música cortada en seco, sin fundido y sin negro largo. Míralo tres veces seguidas en bucle; si no notas dónde termina, está bien hecho.

---

## 7. EXPORTACIÓN Y CONTROL FINAL

- **Export:** MP4 H.264, 1080 × 1920, 30 fps, 10–14 Mbps, audio AAC 192 kbps, loudness alrededor de −14 LUFS.
- **Portada:** usa el fotograma de S01 con Bob en el aire, nunca un frame intermedio.
- **Prueba obligatoria antes de publicar:** míralo entero **en el móvil y sin sonido**. Si no entiendes la historia solo con imagen y subtítulos, el problema está en la imagen, no en el guion.
- **Segunda prueba:** míralo con sonido y cronómetro. Si en algún punto te dan ganas de deslizar, ese beat necesita un pattern interrupt: casi siempre se arregla adelantando el corte medio segundo.

---

## 8. PLAN B SI GROK NO SOSTIENE LOS PERSONAJES

Ordenados de menos a más esfuerzo:

1. **Reducir personajes por plano.** S09 es el punto más frágil con tres en cuadro: si falla, saca a Bob del encuadre y deja solo su voz señalando desde fuera.
2. **Ampliar el plano.** Los planos medios y generales derivan menos que los primeros planos; en las escenas problemáticas, aléjate.
3. **Congelar y animar el movimiento en edición.** Si un still es perfecto y el clip siempre sale deforme, usa el still fijo y crea el movimiento con zoom lento y desplazamiento en el editor. Con 3,5 a 5 segundos y un buen efecto de sonido, no se nota.
4. **Separar herramientas.** Genera los stills en un motor con imagen de referencia y usa Grok solo para imagen-a-video, que es donde más aporta. Es la ruta más fiable si vas a hacer una serie larga con los mismos personajes.

"""Contrasta cada valor de las plantillas contra el esquema de su seccion.

Shopify no avisa cuando un ajuste trae un valor que su esquema no acepta:
simplemente no lo aplica. Esto lo detecta antes de subir nada.
"""
import json, re, glob, os, sys

def schema_of(section_type):
    path = os.path.join('sections', section_type + '.liquid')
    if not os.path.exists(path):
        return None, path
    src = open(path, encoding='utf-8').read()
    m = re.search(r'\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}', src, re.S)
    if not m:
        return None, path
    return json.loads(m.group(1)), path

def index_settings(settings):
    return {s['id']: s for s in settings or [] if 'id' in s}

problems = []

def check_values(values, defs, where):
    for key, value in (values or {}).items():
        if key not in defs:
            problems.append(f"{where}: el ajuste «{key}» no existe en el esquema")
            continue
        spec = defs[key]
        kind = spec.get('type')
        if kind == 'select':
            allowed = [o['value'] for o in spec.get('options', [])]
            if value not in allowed:
                problems.append(f"{where}: «{key}» = {value!r} no esta entre {allowed}")
        elif kind == 'range':
            lo, hi, step = spec['min'], spec['max'], spec.get('step', 1)
            if not isinstance(value, (int, float)):
                problems.append(f"{where}: «{key}» = {value!r} deberia ser numero")
            elif value < lo or value > hi:
                problems.append(f"{where}: «{key}» = {value} fuera de [{lo}, {hi}]")
            elif abs(round((value - lo) / step) - (value - lo) / step) > 1e-9:
                problems.append(f"{where}: «{key}» = {value} no cae en el paso {step}")
        elif kind == 'checkbox' and not isinstance(value, bool):
            problems.append(f"{where}: «{key}» = {value!r} deberia ser true/false")

targets = sorted(glob.glob('templates/**/*.json', recursive=True) + glob.glob('sections/*-group.json'))
for tpl in targets:
    data = json.load(open(tpl, encoding='utf-8'))
    for sec_id, sec in (data.get('sections') or {}).items():
        stype = sec['type']
        schema, path = schema_of(stype)
        if schema is None:
            problems.append(f"{tpl} → {sec_id}: no hay esquema en {path}")
            continue
        check_values(sec.get('settings'), index_settings(schema.get('settings')), f"{tpl} → {sec_id} ({stype})")

        block_defs = {b['type']: b for b in schema.get('blocks', [])}
        for blk_id, blk in (sec.get('blocks') or {}).items():
            btype = blk['type']
            if btype not in block_defs:
                problems.append(f"{tpl} → {sec_id}.{blk_id}: el bloque «{btype}» no existe en {stype}")
                continue
            check_values(blk.get('settings'), index_settings(block_defs[btype].get('settings')),
                         f"{tpl} → {sec_id}.{blk_id} ({btype})")

        order = sec.get('block_order') or []
        blocks = sec.get('blocks') or {}
        for bid in order:
            if bid not in blocks:
                problems.append(f"{tpl} → {sec_id}: block_order menciona «{bid}», que no existe")
        for bid in blocks:
            if bid not in order:
                problems.append(f"{tpl} → {sec_id}: el bloque «{bid}» no esta en block_order")

    order = data.get('order') or []
    sections = data.get('sections') or {}
    for sid in order:
        if sid not in sections:
            problems.append(f"{tpl}: order menciona «{sid}», que no existe")
    for sid in sections:
        if sid not in order:
            problems.append(f"{tpl}: la seccion «{sid}» no esta en order")

# Ajustes globales contra config/settings_schema.json
schema_groups = json.load(open('config/settings_schema.json', encoding='utf-8'))
global_defs = {}
for group in schema_groups:
    for s in group.get('settings', []) or []:
        if 'id' in s:
            global_defs[s['id']] = s
current = json.load(open('config/settings_data.json', encoding='utf-8'))['current']
check_values(current, global_defs, 'config/settings_data.json')

print(f"plantillas revisadas: {len(targets)}")
if problems:
    print(f"\n{len(problems)} problema(s):")
    for p in problems:
        print('  -', p)
    sys.exit(1)
print("sin problemas")

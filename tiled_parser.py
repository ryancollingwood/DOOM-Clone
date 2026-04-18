import json

def parse_tiled_json(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)

    settings = {
        'seed': 21315,
        'cam_pos': None,
        'cam_target': None
    }

    scale = 1.0
    for prop in data.get('properties', []):
        if prop['name'] == 'seed':
            settings['seed'] = int(prop['value'])
        elif prop['name'] == 'cam_pos':
            vals = [float(x.strip()) for x in str(prop['value']).split(',')]
            settings['cam_pos'] = tuple(vals)
        elif prop['name'] == 'cam_target':
            vals = [float(x.strip()) for x in str(prop['value']).split(',')]
            settings['cam_target'] = tuple(vals)
        elif prop['name'] == 'scale':
            scale = float(prop['value'])

    sector_data = {}
    polygons = {}

    segments_layer = None
    sectors_layer = None

    for layer in data.get('layers', []):
        if layer.get('name') == 'sectors':
            sectors_layer = layer
        elif layer.get('name') == 'segments':
            segments_layer = layer

    if sectors_layer:
        for obj in sectors_layer.get('objects', []):
            if 'polygon' in obj:
                sec_id = obj['id']
                props = {p['name']: p['value'] for p in obj.get('properties', [])}

                s_data = {
                    'floor_h': float(props.get('floor_h', 0.0)),
                    'ceil_h': float(props.get('ceil_h', 3.0)),
                    'floor_tex_id': int(props.get('floor_tex_id', 0)),
                    'ceil_tex_id': int(props.get('ceil_tex_id', 0)),
                }

                if 'nested_sector_ids' in props:
                    val = props['nested_sector_ids']
                    if isinstance(val, str):
                        s_data['nested_sector_ids'] = [int(x.strip()) for x in val.split(',')]
                    else:
                        s_data['nested_sector_ids'] = [int(val)]

                sector_data[sec_id] = s_data

                base_x, base_y = obj['x'], obj['y']
                poly_pts = []
                for pt in obj['polygon']:
                    x = (base_x + pt['x']) * scale
                    y = (base_y + pt['y']) * scale
                    poly_pts.append((x, y))
                polygons[sec_id] = poly_pts

    custom_textures = {}
    segments_within_sectors = []

    if segments_layer:
        for obj in segments_layer.get('objects', []):
            pts = obj.get('polyline') or obj.get('polygon')
            if pts and len(pts) >= 2:
                props = {p['name']: p['value'] for p in obj.get('properties', [])}
                low = props.get('low_tex_id', None)
                mid = props.get('mid_tex_id', None)
                up = props.get('up_tex_id', None)

                if low is not None: low = int(low)
                if mid is not None: mid = int(mid)
                if up is not None: up = int(up)

                base_x, base_y = obj['x'], obj['y']

                if 'front_sector_id' in props:
                    front = int(props['front_sector_id'])
                    back = props.get('back_sector_id', None)
                    if back is not None: back = int(back)

                    for i in range(len(pts) - 1):
                        p0 = ((base_x + pts[i]['x']) * scale, (base_y + pts[i]['y']) * scale)
                        p1 = ((base_x + pts[i+1]['x']) * scale, (base_y + pts[i+1]['y']) * scale)
                        segments_within_sectors.append(
                            [(p0, p1), (front, back), (low, mid, up)]
                        )
                else:
                    for i in range(len(pts) - 1):
                        p0 = ((base_x + pts[i]['x']) * scale, (base_y + pts[i]['y']) * scale)
                        p1 = ((base_x + pts[i+1]['x']) * scale, (base_y + pts[i+1]['y']) * scale)

                        p0_r = (round(p0[0], 4), round(p0[1], 4))
                        p1_r = (round(p1[0], 4), round(p1[1], 4))

                        custom_textures[(p0_r, p1_r)] = (low, mid, up)
                        custom_textures[(p1_r, p0_r)] = (low, mid, up)

    edges_info = {}
    for sec_id, pts in polygons.items():
        n = len(pts)
        for i in range(n):
            p0 = pts[i]
            p1 = pts[(i + 1) % n]

            p0_r = (round(p0[0], 4), round(p0[1], 4))
            p1_r = (round(p1[0], 4), round(p1[1], 4))

            edges_info[(p0_r, p1_r)] = (p0, p1, sec_id)

    processed = set()
    segments_of_sector_boundaries = []

    for (p0_r, p1_r), (p0, p1, front_sec_id) in edges_info.items():
        if (p0_r, p1_r) in processed:
            continue

        back_sec_id = None
        if (p1_r, p0_r) in edges_info:
            _, _, back_sec_id = edges_info[(p1_r, p0_r)]
            processed.add((p1_r, p0_r))

        processed.add((p0_r, p1_r))

        tex = custom_textures.get((p0_r, p1_r), (None, None, None))

        segments_of_sector_boundaries.append(
            [(p0, p1), (front_sec_id, back_sec_id), tex]
        )

    return settings, sector_data, segments_of_sector_boundaries, segments_within_sectors

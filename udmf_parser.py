import re
import math

# We default CAM_HEIGHT if we can't import settings, to avoid pyray dependency during tests/parsing
CAM_HEIGHT = 0.6
try:
    from settings import CAM_HEIGHT
except ImportError:
    pass

UDMF_SCALE = 1.0

def _parse_texture(tex_str):
    if not tex_str or tex_str == '-':
        return None
    # Try to extract trailing digits, otherwise return 0
    match = re.search(r'\d+$', tex_str)
    if match:
        return int(match.group())
    return 0

class UDMFParser:
    def __init__(self, filepath=None, udmf_string=None):
        if filepath:
            with open(filepath, 'r') as f:
                self.udmf_string = f.read()
        elif udmf_string:
            self.udmf_string = udmf_string
        else:
            raise ValueError("Must provide either filepath or udmf_string")

        self.blocks = {'vertex': [], 'sector': [], 'sidedef': [], 'linedef': [], 'thing': []}
        self.parse()

    def parse(self):
        # Remove comments
        s = re.sub(r'//.*', '', self.udmf_string)
        s = re.sub(r'/\*.*?\*/', '', s, flags=re.DOTALL)

        block_pattern = re.compile(r'([A-Za-z0-9_]+)\s*\{([^}]*)\}')
        for match in block_pattern.finditer(s):
            block_type = match.group(1).lower()
            block_content = match.group(2)

            properties = {}
            prop_pattern = re.compile(r'([A-Za-z0-9_]+)\s*=\s*([^;]+);')
            for prop_match in prop_pattern.finditer(block_content):
                key = prop_match.group(1).lower()
                val = prop_match.group(2).strip()

                if val.startswith('"') and val.endswith('"'):
                    val = val[1:-1]
                elif val.lower() == 'true':
                    val = True
                elif val.lower() == 'false':
                    val = False
                else:
                    try:
                        if '.' in val or 'e' in val.lower():
                            val = float(val)
                        else:
                            val = int(val, 0)
                    except ValueError:
                        pass
                properties[key] = val

            if block_type in self.blocks:
                self.blocks[block_type].append(properties)

    def generate_engine_data(self):
        settings = {
            'seed': 0,
            'cam_pos': [0.0, CAM_HEIGHT, 0.0],
            'cam_target': [1.0, CAM_HEIGHT, 0.0]
        }

        vertices = []
        for v in self.blocks['vertex']:
            vertices.append((v.get('x', 0.0) * UDMF_SCALE, v.get('y', 0.0) * UDMF_SCALE))

        # Build sector -> list of vertices mapping by tracing linedefs
        sector_vertices = {}
        sidedefs = self.blocks['sidedef']
        for line in self.blocks['linedef']:
            v1_idx = line.get('v1')
            v2_idx = line.get('v2')
            if v1_idx is None or v2_idx is None:
                continue

            p0 = vertices[v1_idx]
            p1 = vertices[v2_idx]

            sidefront_idx = line.get('sidefront', -1)
            sideback_idx = line.get('sideback', -1)

            if sidefront_idx != -1 and sidefront_idx < len(sidedefs):
                front_sec = sidedefs[sidefront_idx].get('sector')
                if front_sec is not None:
                    if front_sec not in sector_vertices:
                        sector_vertices[front_sec] = []
                    sector_vertices[front_sec].append(p0)
                    sector_vertices[front_sec].append(p1)

            if sideback_idx != -1 and sideback_idx is not None and sideback_idx < len(sidedefs):
                back_sec = sidedefs[sideback_idx].get('sector')
                if back_sec is not None:
                    if back_sec not in sector_vertices:
                        sector_vertices[back_sec] = []
                    sector_vertices[back_sec].append(p0)
                    sector_vertices[back_sec].append(p1)

        # Try to find player start (type 1)
        player_found = False
        for thing in self.blocks['thing']:
            if thing.get('type') == 1:
                x = thing.get('x', 0.0) * UDMF_SCALE
                y = thing.get('y', 0.0) * UDMF_SCALE
                angle_deg = thing.get('angle', 0.0)
                angle_rad = math.radians(angle_deg)
                settings['cam_pos'] = [x, CAM_HEIGHT, y]
                settings['cam_target'] = [x + math.cos(angle_rad), CAM_HEIGHT, y + math.sin(angle_rad)]
                player_found = True
                break

        # If no player found, calculate largest sector and use its center
        if not player_found and sector_vertices:
            largest_area = -1
            best_center = (0.0, 0.0)

            for sec_id, verts in sector_vertices.items():
                if not verts: continue
                # Simple bounding box area
                min_x = min(v[0] for v in verts)
                max_x = max(v[0] for v in verts)
                min_y = min(v[1] for v in verts)
                max_y = max(v[1] for v in verts)

                area = (max_x - min_x) * (max_y - min_y)
                if area > largest_area:
                    largest_area = area
                    best_center = (min_x + (max_x - min_x) / 2.0, min_y + (max_y - min_y) / 2.0)

            settings['cam_pos'] = [best_center[0], CAM_HEIGHT, best_center[1]]
            settings['cam_target'] = [best_center[0] + 1.0, CAM_HEIGHT, best_center[1]]

        sector_data = {}
        for i, sec in enumerate(self.blocks['sector']):
            floor_h = sec.get('heightfloor', 0.0) * UDMF_SCALE
            ceil_h = sec.get('heightceiling', 0.0) * UDMF_SCALE

            floor_tex_id = _parse_texture(sec.get('texturefloor'))
            ceil_tex_id = _parse_texture(sec.get('textureceiling'))

            sector_data[i] = {
                'floor_h': floor_h,
                'ceil_h': ceil_h,
                'floor_tex_id': floor_tex_id if floor_tex_id is not None else 0,
                'ceil_tex_id': ceil_tex_id if ceil_tex_id is not None else 0,
                'nested_sector_ids': []
            }

        segments_of_sector_boundaries = []

        for line in self.blocks['linedef']:
            v1_idx = line.get('v1')
            v2_idx = line.get('v2')
            if v1_idx is None or v2_idx is None:
                continue

            p0 = vertices[v1_idx]
            p1 = vertices[v2_idx]

            sidefront_idx = line.get('sidefront', -1)
            sideback_idx = line.get('sideback', -1)

            front_sec = None
            back_sec = None

            lo_tex, mid_tex, up_tex = None, None, None

            if sidefront_idx != -1 and sidefront_idx < len(sidedefs):
                sd_front = sidedefs[sidefront_idx]
                front_sec = sd_front.get('sector')

                mid_tex = _parse_texture(sd_front.get('texturemiddle'))
                up_tex = _parse_texture(sd_front.get('texturetop'))
                lo_tex = _parse_texture(sd_front.get('texturebottom'))

            if sideback_idx != -1 and sideback_idx is not None and sideback_idx < len(sidedefs):
                sd_back = sidedefs[sideback_idx]
                back_sec = sd_back.get('sector', None)

            if front_sec is None:
                continue

            segments_of_sector_boundaries.append([
                (p0, p1),
                (front_sec, back_sec),
                (lo_tex, mid_tex, up_tex)
            ])

        return {
            'SETTINGS': settings,
            'SECTOR_DATA': sector_data,
            'SEGMENTS_OF_SECTOR_BOUNDARIES': segments_of_sector_boundaries,
            'SEGMENTS_WITHIN_SECTORS': []
        }

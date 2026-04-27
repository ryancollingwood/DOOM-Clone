import pytest
from udmf_parser import UDMFParser, _parse_texture

def test_parse_texture():
    assert _parse_texture("WALL1") == 1
    assert _parse_texture("FLAT2") == 2
    assert _parse_texture("SOME_TEXTURE42") == 42
    assert _parse_texture("NOTEXTURE") == 0
    assert _parse_texture("-") is None
    assert _parse_texture("") is None

def test_udmf_parser_basic():
    udmf_data = """
    namespace = "ZDoom";

    thing { id=1; type=1; x=5.0; y=5.0; angle=90; }

    vertex { x=0.0; y=0.0; }
    vertex { x=10.0; y=0.0; }

    sector { heightfloor=0.0; heightceiling=3.0; texturefloor="FLAT1"; textureceiling="FLAT2"; }

    sidedef { sector=0; texturemiddle="WALL3"; }

    linedef { v1=0; v2=1; sidefront=0; sideback=-1; }
    """

    parser = UDMFParser(udmf_string=udmf_data)
    engine_data = parser.generate_engine_data()

    settings = engine_data['SETTINGS']
    assert settings['cam_pos'][0] == pytest.approx(5.0)
    assert settings['cam_pos'][2] == pytest.approx(5.0)

    sector_data = engine_data['SECTOR_DATA']
    assert len(sector_data) == 1
    assert sector_data[0]['floor_h'] == pytest.approx(0.0)
    assert sector_data[0]['ceil_h'] == pytest.approx(3.0)
    assert sector_data[0]['floor_tex_id'] == 1
    assert sector_data[0]['ceil_tex_id'] == 2

    segments = engine_data['SEGMENTS_OF_SECTOR_BOUNDARIES']
    assert len(segments) == 1
    p0, p1 = segments[0][0]
    front_sec, back_sec = segments[0][1]
    lo_tex, mid_tex, up_tex = segments[0][2]

    assert p0 == (0.0, 0.0)
    assert p1 == (10.0, 0.0)
    assert front_sec == 0
    assert back_sec == None
    assert mid_tex == 3

def test_udmf_parser_defaults():
    udmf_data = """
    vertex {}
    sector {}
        sidedef { sector=0; }
    linedef { v1=0; v2=0; sidefront=0; }
    """

    parser = UDMFParser(udmf_string=udmf_data)
    engine_data = parser.generate_engine_data()

    sector_data = engine_data['SECTOR_DATA']
    assert sector_data[0]['floor_h'] == 0.0
    assert sector_data[0]['ceil_h'] == 0.0
    assert sector_data[0]['floor_tex_id'] == 0
    assert sector_data[0]['ceil_tex_id'] == 0

    segments = engine_data['SEGMENTS_OF_SECTOR_BOUNDARIES']
    lo_tex, mid_tex, up_tex = segments[0][2]
    assert lo_tex is None
    assert mid_tex is None
    assert up_tex is None

def test_fallback_player_start():
    udmf_data = """
    vertex { x=0.0; y=0.0; }
    vertex { x=10.0; y=0.0; }
    vertex { x=10.0; y=10.0; }
    vertex { x=0.0; y=10.0; }

    vertex { x=20.0; y=20.0; }
    vertex { x=50.0; y=20.0; }
    vertex { x=50.0; y=50.0; }
    vertex { x=20.0; y=50.0; }

    sector { heightfloor=0.0; heightceiling=3.0; }
    sector { heightfloor=0.0; heightceiling=3.0; }

    sidedef { sector=0; }
    sidedef { sector=1; }

    // Sector 0: 10x10 area
    linedef { v1=0; v2=1; sidefront=0; }
    linedef { v1=1; v2=2; sidefront=0; }
    linedef { v1=2; v2=3; sidefront=0; }
    linedef { v1=3; v2=0; sidefront=0; }

    // Sector 1: 30x30 area (should be chosen as largest)
    linedef { v1=4; v2=5; sidefront=1; }
    linedef { v1=5; v2=6; sidefront=1; }
    linedef { v1=6; v2=7; sidefront=1; }
    linedef { v1=7; v2=4; sidefront=1; }
    """

    parser = UDMFParser(udmf_string=udmf_data)
    engine_data = parser.generate_engine_data()

    settings = engine_data['SETTINGS']
    # The largest sector is from 20 to 50 on x and y, so center is (35, 35)
    assert settings['cam_pos'][0] == pytest.approx(35.0)
    assert settings['cam_pos'][2] == pytest.approx(35.0)

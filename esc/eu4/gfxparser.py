from pathlib import Path

from ck2parser import SimpleParser
from eu4.eu4lib import DLC

class SpriteType:

    def __init__(self, name: str, texture_file: str, dlc: DLC = None):
        self.name = name
        self.texture_file = texture_file
        self.dlc = dlc


class GfxParser:

    def __init__(self, parser):
        self.parser = parser

    def parse_gfx_file(self, gfx_file: str|Path, gfx_prefix: str, dlc: DLC = None):
        result = {}
        # if isinstance(gfx_file, Path):
        if isinstance(gfx_file, str):
            parsed_file = self.parser.parse_file(gfx_file)
        else:
            with gfx_file.open('rb') as gfx_fp:
                parsed_file = self.parser.parse(gfx_fp.read().decode('cp1252'))
        if 'spriteTypes' not in parsed_file:
            return result
        for n, v in parsed_file['spriteTypes']:
            if n.val.lower() in ['progressbartype', 'frameanimatedspritetype', 'cursor_offset', 'textspritetype', 'corneredtilespritetype', 'maskedshieldtype', 'piecharttype', 'linecharttype']:
                continue

            if n.val.lower() != 'spritetype':
                raise Exception(f'Unexpected section {n.val}')
            picture_name = v['name'].val
            if 'texturefile' in v:
                texture_file = v['texturefile'].val
            elif 'textureFile' in v:
                texture_file = v['textureFile'].val
            else:
                raise Exception(f'no texturefile for {picture_name}')

            texture_file = texture_file.replace('\\', '/')
            normalized_name = picture_name.removeprefix(gfx_prefix)
            result[normalized_name] = SpriteType(normalized_name, texture_file, dlc)
        return result

    def parse_all_gfx_files(self, dlcs: list[DLC] = None):
        sprite_types = {}
        for dlc in dlcs:
            if dlc.name == 'base':
                glob = 'interface/**/*.gfx'
            else:
                glob = '*.gfx'
            for gfx_path in dlc.glob(glob):
                if 'interface/assets' in str(gfx_path):
                    # these files don't have spritetypes and some can't be parsed
                    continue
                sprites_from_file = self.parse_gfx_file(gfx_path, '', dlc)
                sprite_types.update(sprites_from_file)

        return sprite_types
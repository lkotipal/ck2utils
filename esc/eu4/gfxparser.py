import glob
from pathlib import Path

import funcparserlib

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

    def _parse_file(self, gfx_file, encoding='cp1252'):
        # if isinstance(gfx_file, Path):
        if isinstance(gfx_file, str):
            parsed_file = self.parser.parse_file(gfx_file, encoding=encoding)
        else:
            with gfx_file.open('rb') as gfx_fp:
                file_contents = gfx_fp.read()
                try:
                    parsed_file = self.parser.parse(file_contents.decode(encoding))
                except funcparserlib.parser.NoParseError:
                    file_contents += b'}'
                    parsed_file = self.parser.parse(file_contents.decode(encoding))
        return  parsed_file

    def parse_gfx_file(self, gfx_file: str|Path, gfx_prefix: str, dlc: DLC = None):
        result = {}

        try:
            parsed_file = self._parse_file(gfx_file, 'cp1252')
        except UnicodeDecodeError:
            parsed_file = self._parse_file(gfx_file, 'utf8')

        if 'spriteTypes' not in parsed_file:
            return result
        for n, v in parsed_file['spriteTypes']:
            if n.val.lower() in ['progressbartype', 'frameanimatedspritetype', 'cursor_offset', 'textspritetype', 'corneredtilespritetype', 'maskedshieldtype', 'piecharttype', 'linecharttype', 'circularprogressbartype']:
                continue

            if n.val.lower() != 'spritetype':
                raise Exception(f'Unexpected section {n.val}')
            picture_name = v['name'].val
            if 'texturefile' in v:
                texture_file = v['texturefile'].val
            elif 'textureFile' in v:
                texture_file = v['textureFile'].val
            elif picture_name in ['GFX_mapicon_unit_large_flag_stripe', 'GFX_mapicon_unit_flag_stripe', 'GFX_mapicon_unit_flag_stripe_visible']:
                # hoi4 comment says: Texture file is ste in code to proper flag
                continue
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

    def parse_all_gfx_files_hoi4(self):
        sprite_types = {}
        for glob_str in [
            'interface/**/*.gfx',
            'dlc/*/interface/**/*.gfx',
            'integrated_dlc/*/interface/**/*.gfx',
        ]:
            # print(glob_str)
            # for gfx_path in glob.glob(str(self.parser.basedir) + glob_str):
            for gfx_path in self.parser.files(glob_str):
                # print(gfx_path)
                if 'interface/assets' in str(gfx_path):
                    # these files don't have spritetypes and some can't be parsed
                    continue
                sprites_from_file = self.parse_gfx_file(gfx_path, '')
                sprite_types.update(sprites_from_file)

        return sprite_types

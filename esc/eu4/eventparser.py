import hashlib
import re
import zipfile
from pathlib import PurePath, Path
from zipfile import ZipFile

from eu4.parser import Eu4Parser
from eu4.eu4lib import Event, EventPicture, BaseGame, DLC
from eu4.cache import cached_property


class Eu4EventParser(Eu4Parser):

    @cached_property
    def all_events(self):
        events = {}
        mandatory_attributes = ['id', 'title', 'desc']
        for eventfile, tree in self.parser.parse_files('events/*'):
            namespace = ''
            for n, v in tree:
                if n.val == 'namespace':
                    namespace = v.val
                elif n.val == 'normal_or_historical_nations':
                    pass  # ignore
                elif n.val == 'country_event' or n.val == 'province_event':
                    attributes = {}
                    eventid = None
                    for n2, v2 in v:
                        attributes[n2.val] = v2
                    missing_attributes = [a for a in mandatory_attributes if a not in attributes]
                    if len(missing_attributes) > 0:
                        raise Exception('Event is missing attributes {}'.format(', '.join(missing_attributes)))
                    event = Event(self, attributes, eventfile.name)
                    if event.id in events:
                        raise Exception('duplicate event id "{}"'.format(event.id))
                    events[event.id] = event
                else:
                    raise Exception('unknown key "{}" in file "{}"'.format(n.val, eventfile))
        return events

    @cached_property
    def events_by_title(self):
        events_by_title = {}
        for event in self.all_events.values():
            if event.title in events_by_title:
                # print('duplicate event title "{}"'.format(event.title))
                if not isinstance(events_by_title[event.title], list):
                    events_by_title[event.title] = [events_by_title[event.title]]
                events_by_title[event.title].append(event)
            else:
                events_by_title[event.title] = event
        return events_by_title

    @cached_property
    def event_pictures(self) -> list[EventPicture]:
        pictures = []
        pictures_by_gfx_file = {}
        for dlc in self.dlcs_including_base_game:
            if dlc.name == 'base' or dlc.category in ['content_pack', 'expansion']:
                for gfx_path in dlc.glob('interface/*eventpictures*.gfx'):
                    pictures_by_gfx_file[gfx_path.name] = self._get_pictures_from_gfx_file(dlc, gfx_path)
                    pictures.extend(pictures_by_gfx_file[gfx_path.name])
        self._add_overriding_information(pictures_by_gfx_file)
        return pictures

    def _add_overriding_information(self, pictures_by_gfx_file: dict[str, list[EventPicture]]):
        pictures_by_name = {}
        for gfx, pictures in sorted(pictures_by_gfx_file.items()):
            for picture in pictures:
                if picture.name in pictures_by_name:
                    for overridden in pictures_by_name[picture.name]:
                        overridden.overridden_by.append(picture)
                    pictures_by_name[picture.name].append(picture)
                else:
                    pictures_by_name[picture.name] = [picture]

    def _get_pictures_from_gfx_file(self, dlc, gfx_path: Path) -> list[EventPicture]:
        with gfx_path.open('rb') as gfx_file:
            pictures_by_name = {}
            for n, v in self.parser.parse(gfx_file.read().decode('cp1252'))['spriteTypes']:
                if n.val != 'spriteType':
                    raise Exception(f'Unexpected section {n.val} in {gfx_file}')
                picture_name = v['name'].val
                picture_filename = v['texturefile'].val.replace('\\', '/')
                wiki_filename = self._generate_wiki_filename(picture_filename)
                picture_data = dlc.get_file_contents(picture_filename)
                picture_sha = hashlib.sha256(picture_data).hexdigest()
                picture = EventPicture(picture_name, picture_filename, wiki_filename, dlc, [], picture_sha,
                                       picture_data)
                # if there is already an entry with the same name in this gfx file, it will be overwritten,
                # because I assume that the game would do the same(as of version 1.34,
                # the only duplications have identical values)
                pictures_by_name[picture_name] = picture
        return pictures_by_name.values()

    def _generate_wiki_filename(self, picture_filename):
        wiki_filename = picture_filename.removeprefix('gfx/event_pictures/').removesuffix(
            '.dds').replace('/', '-').replace('__', '_') + '.jpg'
        wiki_filename = wiki_filename[0].upper() + wiki_filename[1:]
        return wiki_filename

    @cached_property
    def event_pictures_by_hash(self) -> dict[str, list[EventPicture]]:
        pictures_by_file = {}
        for picture in self.event_pictures:
            if picture.sha_hash not in pictures_by_file:
                pictures_by_file[picture.sha_hash] = []
            pictures_by_file[picture.sha_hash].append(picture)
        return pictures_by_file

    @cached_property
    def unused_event_pictures_by_hash(self) -> dict[str, list[EventPicture]]:
        """These pictures are not referenced in any GFX file, but they exist in a subfolder of gfx/event_pictures"""
        used_sha = set()
        filenames_by_dlc = {}
        for picture in self.event_pictures:
            used_sha.add(picture.sha_hash)
            if picture.dlc.name not in filenames_by_dlc:
                filenames_by_dlc[picture.dlc.name] = []
            filenames_by_dlc[picture.dlc.name].append(picture.filename)

        unused_pictures = {}
        for dlc in self.dlcs_including_base_game:
            for picture_path in dlc.glob('gfx/event_pictures/*/*.dds'):
                picture_filename = re.sub(r'^.*gfx/event_pictures', 'gfx/event_pictures', str(picture_path))
                if dlc.name not in filenames_by_dlc or picture_filename not in filenames_by_dlc[dlc.name]:
                    picture_data = dlc.get_file_contents(picture_filename)
                    picture_sha = hashlib.sha256(picture_data).hexdigest()
                    if picture_sha not in used_sha:
                        if picture_sha not in unused_pictures:
                            unused_pictures[picture_sha] = []
                        unused_pictures[picture_sha].append(EventPicture('none', picture_filename, self._generate_wiki_filename(picture_filename), dlc, [], picture_sha, picture_data))
        return unused_pictures

import re
import zipfile
from pathlib import Path, PurePath
from zipfile import ZipFile

from ck2parser import String
from common.paradox_lib import NameableEntity, PdxColor
from eu4.provincelists import coastal_provinces
from eu4.cache import cached_property


class Province(object):

    def __init__(self, provinceID, parser=None):
        self.id = provinceID
        self.parser = parser
        self.name = parser.localize('PROV{}'.format(provinceID))
        self.center_of_trade = 0
        self.attributes = {}

    def __str__(self, *args, **kwargs):
        return '{} ({})'.format(self.name, self.id)

    def __setitem__(self, key, value):
        if key in ['ID', 'Name', 'Type', 'Continent', 'center_of_trade']:
            setattr(self, key.lower(), value)
        else:
            self.attributes.__setitem__(key, value)

    def __getitem__(self, key):
        if hasattr(self, key.lower().replace(' ', '')):
            return getattr(self, key.lower().replace(' ', ''))
        return self.attributes.__getitem__(key)

    def __contains__(self, key):
        if hasattr(self, key.lower().replace(' ', '')):
            return True
        return key in self.attributes

    def get(self, key, default=None):
        if hasattr(self, key.lower().replace(' ', '')):
            return getattr(self, key.lower().replace(' ', ''))
        return self.attributes.get(key, default)

    @property
    def type(self):
        return self.parser.get_province_type(self.id)

    @cached_property
    def continent(self):
        return self.parser.get_continent(self)

    @cached_property
    def area(self):
        return self.parser.get_area(self)

    @cached_property
    def region(self):
        return self.parser.get_region(self.area.name)

    @cached_property
    def superregion(self):
        return self.parser.get_superregion(self.region.name)

    @cached_property
    def tradenode(self):
        return self.parser.get_trade_node(self)

    @cached_property
    def has_port(self):
        return self.id in coastal_provinces

    def format_center_of_trade_string(self):
        if self.has_port:
            cot_names = {1: 'Natural Harbor', 2: 'Entrepot', 3: 'World Port'}
        else:
            cot_names = {1: 'Emporium', 2: 'Market Town', 3: 'World Trade Center'}
        return cot_names[self.center_of_trade]


class NameableEntityWithProvinces(NameableEntity):

    def __init__(self, name, display_name, provinces=None, provinceIDs=None, parser=None):
        super().__init__(name, display_name)
        self._provinces = provinces
        self._provinceIDs = provinceIDs
        self.parser = parser

    @cached_property
    def provinces(self):
        if self._provinces is None:
            self._provinces = [self.parser.all_provinces[provinceID] for provinceID in self._provinceIDs]
        return self._provinces

    @cached_property
    def provinceIDs(self):
        if self._provinceIDs is None:
            self._provinceIDs = [province.id for province in self._provinces]
        return self._provinceIDs


class NameableEntityWithProvincesAndColor(NameableEntityWithProvinces):
    def __init__(self, name, display_name, provinces=None, provinceIDs=None, parser=None, color=None):
        super().__init__(name, display_name, provinces, provinceIDs, parser)
        self.color = color


class Continent(NameableEntityWithProvinces):
    pass


class Area(NameableEntityWithProvinces):

    def __init__(self, name, display_name, provinces=None, provinceIDs=None, parser=None, color=None):
        super().__init__(name, display_name, provinces, provinceIDs, parser)
        self.color = color

    @cached_property
    def region(self):
        return self.parser.get_region(self.name)

    @cached_property
    def contains_land_provinces(self):
        for province in self.provinces:
            if province.type == 'Land':
                return True
        return False

    @cached_property
    def contains_inland_seas(self):
        for province in self.provinces:
            if province.type == 'Inland sea':
                return True
        return False


class Region(NameableEntity):

    def __init__(self, name, display_name, areas=None, area_names=None, parser=None):
        super().__init__(name, display_name)
        self._areas = areas
        self.area_names = area_names
        self.parser = parser
        self._provinceIDs = None
        self._provinces = None

    @property
    def areas(self):
        if not self._areas:
            self._areas = [self.parser.all_areas[area_name] for area_name in self.area_names if
                           area_name in self.parser.all_areas]
        return self._areas

    @cached_property
    def superregion(self):
        return self.parser.get_superregion(self.name)

    @cached_property
    def contains_land_provinces(self):
        for area in self.areas:
            if area.contains_land_provinces:
                return True
        return False

    @cached_property
    def contains_inland_seas(self):
        for area in self.areas:
            if area.contains_inland_seas:
                return True
        return False

    @cached_property
    def provinceIDs(self):
        if self._provinceIDs is None:
            self._provinceIDs = []
            for area in self.areas:
                self._provinceIDs.extend(area.provinceIDs)
        return self._provinceIDs

    @cached_property
    def provinces(self):
        if self._provinces is None:
            self._provinces = [self.parser.all_provinces[provinceID] for provinceID in self.provinceIDs]
        return self._provinces

    @cached_property
    def color(self):
        return self.parser.region_colors[self.name]


class Superregion(NameableEntity):

    def __init__(self, name, display_name, regions=None, region_names=None, parser=None):
        super().__init__(name, display_name)
        self._regions = regions
        self.region_names = region_names
        self.parser = parser

    @property
    def regions(self):
        if not self._regions:
            self._regions = [self.parser.all_regions[region_name] for region_name in self.region_names]
        return self._regions

    @cached_property
    def contains_land_provinces(self):
        for region in self.regions:
            if region.contains_land_provinces:
                return True
        return False


class ColonialRegion(NameableEntityWithProvincesAndColor):
    pass


class Terrain(NameableEntityWithProvincesAndColor):
    pass


class Event:

    def __init__(self, parser, attributes, source_file=None):
        self.parser = parser
        self.attributes = attributes
        self.id = attributes['id'].val_str()
        self.title = parser.localize(attributes['title'].val_str())
        self.source_file = source_file
        if isinstance(attributes['desc'], String):
            self.desc = parser.localize(attributes['desc'].val_str(), 'variable desc')
        else:
            self.desc = 'variable desc'


class Decision:

    def __init__(self, parser, decision_id, attributes, source_file=None):
        self.parser = parser
        self.attributes = attributes
        self.id = decision_id
        self.title = parser.localize('{}_title'.format(decision_id))
        self.desc = parser.localize('{}_desc'.format(decision_id), 'no desc')
        self.source_file = source_file


class Religion(NameableEntity):

    def __init__(self, name: str, display_name: str, group, color):
        super().__init__(name, display_name)
        self.group = group
        self.color = color


class TradeCompany(NameableEntityWithProvincesAndColor):
    pass


class TradeNode(NameableEntityWithProvincesAndColor):

    def __init__(self, name, display_name, location, outgoing_node_names=None, inland=False, endnode=False,
                 provinces=None, provinceIDs=None, parser=None, color=None):
        super().__init__(name, display_name, provinces, provinceIDs, parser, color)
        self.location = location
        if outgoing_node_names is not None:
            self.outgoing_node_names = outgoing_node_names
        else:
            self.outgoing_node_names = []
        self.inland = inland
        self.endnode = endnode

    @cached_property
    def outgoing_nodes(self):
        return [self.parser.all_trade_nodes[name] for name in self.outgoing_node_names]

    @cached_property
    def incoming_nodes(self):
        return [node for node in self.parser.all_trade_nodes.values() if self.name in node.outgoing_node_names]


class IdeaGroup(NameableEntity):
    overridden_display_names = {
        'horde_gov_ideas': 'Horde government Ideas',
        'latin_ideas': 'Italian (minor) ideas',
        'nubian_ideas': 'Nubian (minor) ideas',
        'ATJ_ideas': 'Acehnese/Pasai ideas',  # because they are also for Pasai which is not obvious
    }

    def __init__(self, name, display_name, ideas, bonus, traditions=None, category=None):
        if name in self.overridden_display_names:
            display_name = self.overridden_display_names[name]
        super().__init__(name, display_name)
        self.ideas = ideas
        bonus.idea_group = self
        self.bonus = bonus
        self.traditions = traditions
        if traditions:
            traditions.idea_group = self
        self.category = category
        for idea_counter, idea in enumerate(ideas):
            idea.idea_group = self
            idea.idea_counter_in_group = idea_counter + 1

    def is_basic_idea(self):
        return self.category is not None

    def get_ideas_including_traditions_and_ambitions(self):
        all_ideas = [self.bonus]
        if self.traditions:
            all_ideas.append(self.traditions)
        all_ideas.extend(self.ideas)
        return all_ideas

    def short_name(self):
        return self.display_name.replace(' Ideas', '')


class Idea(NameableEntity):
    overridden_display_names = {
        'horde_gov_ideas_bonus': 'Full Horde ideas',
        'theocracy_gov_ideas_bonus': 'Full Divine ideas',
        'ATJ_ideas_bonus': 'Acehnese/Pasai ambition',  # because they are also for Pasai which is not obvious
        'ATJ_ideas_start': 'Acehnese/Pasai traditions',
        'BLI_ideas_bonus': 'Balinese ambition',
        'SUN_ideas_bonus': 'Sundanese ambition',
        'TTL_ideas_start': 'Three Leagues traditions',  # the game calls them "League Traditions"
        'california_native_ideas_start': 'California Native traditions',
        'daimyo_ideas_start': 'Daimyo traditions',  # the game calls them "Sengoku Jidai"
        'fijian_ideas_start': 'Fijian traditions',
        'hawaiian_ideas_start': 'Hawaiian traditions',
        'latin_ideas_start': 'Italian (minor) traditions',
        'latin_ideas_bonus': 'Italian (minor) ambition',
        'maori_ideas_start': 'Iwi traditions',
        'nubian_ideas_start': 'Nubian (minor) traditions',
        'nubian_ideas_bonus': 'Nubian (minor) ambition',
        'nw_native_ideas_start': 'North Western Native traditions',
        'plains_native_ideas_start': 'Plains Native traditions',
        'samoan_ideas_start': 'Samoan traditions',
        'tongan_ideas_start': 'Tongan traditions',
    }

    def __init__(self, name, display_name, modifiers):
        if name in self.overridden_display_names:
            display_name = self.overridden_display_names[name]
        super().__init__(name, display_name)
        self.modifiers = modifiers
        self.idea_group = None
        self.idea_counter_in_group = None

    def formatted_name(self):
        if self.idea_group and self.idea_counter_in_group:
            return '{} {}: {}'.format(re.sub('ideas', 'idea', self.idea_group.display_name, flags=re.IGNORECASE),
                                      self.idea_counter_in_group, self.display_name)
        else:
            # capitalize first letter and make Traditions and Ambitions lowercase if they are not at the start of the string
            return self.display_name[0].upper() + self.display_name[1:].replace('Tradition', 'tradition').replace(
                'Ambition', 'ambition')

    def is_bonus(self):
        return self == self.idea_group.bonus

    def is_tradition(self):
        return self == self.idea_group.traditions


class Policy(NameableEntity):
    overridden_idea_group_names = {
        'horde_gov_ideas': 'Horde',  # override the overide from the IdeaGroup class
    }

    def __init__(self, name, display_name, description, category, modifiers, idea_groups):
        super().__init__(name, display_name)
        self.description = description
        self.category = category
        self.modifiers = modifiers
        self.idea_groups = idea_groups

    def get_idea_group_short_name(self, idea_group_number):
        idea_group = self.idea_groups[idea_group_number]
        if idea_group.name in self.overridden_idea_group_names:
            return self.overridden_idea_group_names[idea_group.name]
        else:
            return idea_group.short_name()

    def formatted_name(self):
        return '{}-{}: {}'.format(
            self.get_idea_group_short_name(0),
            self.get_idea_group_short_name(1),
            self.display_name)


class Eu4Color(PdxColor):

    @classmethod
    def new_from_parser_obj(cls, color_obj):
        """create an Eu4Color object from a ck2parser Obj.

        The Obj must contain a list/tuple of rgb values.
        For example if the following pdx script is parsed into the variable data:
            color = { 20 50 210 }
        then this function could be called in the following way:
            Eu4Color.new_from_parser_obj(data['color'])
        """
        return cls(color_obj.contents[0].val, color_obj.contents[1].val, color_obj.contents[2].val, is_upscaled=True)


class ModifierType:
    def __init__(self, name, icons, multiply_value_with=None):
        self.name = name
        self.icons = icons
        self.multiply_value_with = multiply_value_with

    def format_value(self, value, other_values):
        value = self.modify_value(value)
        other_values = [self.modify_value(v) for v in other_values]
        if isinstance(value, str):
            return value
        else:
            if self.max_decimal_places(other_values) > 0:
                formatstring = ':.{}f'.format(self.max_decimal_places(other_values))
            else:
                formatstring = ''
            if value > 0:
                return ('+{' + formatstring + '}').format(value)
            else:
                return ('−{' + formatstring + '}').format(value * -1)

    def max_decimal_places(self, value_list):
        return max([self.count_decimal_places(value) for value in value_list])

    def count_decimal_places(self, value):
        str_value = str(value)
        if '.' in str_value:
            str_value = re.sub('0+$', '', str_value)
            return len(str_value.split('.')[1])
        else:
            return 0

    def modify_value(self, value):
        if self.multiply_value_with is not None:
            value *= self.multiply_value_with
            if value == round(value):  # no decimal places
                value = int(value)
        return value


class MultiplicativeModifier(ModifierType):

    def __init__(self, name, icons, multiply_value_with=100):
        super().__init__(name, icons, multiply_value_with)

    def format_value(self, value, other_values):
        return super().format_value(value, other_values) + '%'


class AdditiveModifier(ModifierType):
    pass


class ConstantModifier(ModifierType):
    pass


class AdditiveModifierWithPercentageSign(AdditiveModifier):
    def format_value(self, value, other_values):
        return super().format_value(value, other_values) + '%'


class Mission(NameableEntity):
    def __init__(self, name, display_name, description: str = '', mission_group=None):
        super().__init__(name, display_name)
        self.mission_group = mission_group
        self.description = description


class MissionGroup:
    def __init__(self, name, source_file, potential, missions):
        self.name = name
        self.source_file = source_file
        self.potential = potential
        self.missions = missions
        for mission in missions:
            mission.mission_group = self


class GovernmentReform(NameableEntity):

    def __init__(self, name, display_name, government_type, tier_name, tier_number, basic_reform, attributes, icon,
                 modifiers, potential, trigger, effect, removed_effect, post_removed_effect, conditional
                 ):
        super().__init__(name, display_name)
        self.government_type = government_type
        self.tier_name = tier_name
        self.tier_number = tier_number
        self.basic_reform = basic_reform
        self.attributes = attributes
        self.icon = icon
        self.modifiers = modifiers
        self.potential = potential
        self.trigger = trigger
        self.effect = effect
        self.removed_effect = removed_effect
        self.post_removed_effect = post_removed_effect
        self.conditional = conditional


class Culture(NameableEntity):

    def __init__(self, name: str, display_name: str, culture_group: 'CultureGroup' = None):
        super().__init__(name, display_name)
        self.culture_group = culture_group


class CultureGroup(NameableEntity):
    def __init__(self, name: str, display_name: str, cultures: list[Culture]):
        super().__init__(name, display_name)
        self.cultures = cultures


class Country(NameableEntity):
    def __init__(self, tag, display_name, color=None, parser=None, country_file=None):
        super().__init__(tag, display_name)
        self.tag = tag
        self.color = color
        self.parser = parser
        self.country_file = country_file

    def get_color(self):
        if not self.color:
            self.color = self.parser.get_country_color(self)
        return self.color

    def get_history(self):
        return self.parser.country_histories[self.tag]

    def get_capital_id(self) -> int | None:
        if 'capital' in self.get_history():
            return self.get_history()['capital'].val
        else:  # REB, PIR and NAT
            return None

    def get_primary_culture(self) -> Culture | None:
        if 'primary_culture' in self.get_history():
            return self.parser.cultures[self.get_history()['primary_culture'].val]
        else:  # REB, PIR, NAT and SYN
            return None

    def get_religion(self) -> Religion | None:
        if 'religion' in self.get_history():
            return self.parser.all_religions[self.get_history()['religion'].val]
        else:  # REB, PIR, NAT and SYN
            return None


class DLC(NameableEntity):
    short_names = {
        'Conquest of Paradise': 'cop',
        'Wealth of Nations': 'won',
        'Res Publica': 'rp',
        'Art of War': 'aow',
        'El Dorado': 'ed',
        'Common Sense': 'cs',
        'The Cossacks': 'cos',
        'Mare Nostrum': 'mn',
        'Rights of Man': 'rom',
        'Mandate of Heaven': 'moh',
        'Third Rome': 'tr',
        'Cradle of Civilization': 'coc',
        'Rule Britannia': 'rb',
        'Golden Century': 'gc',
        'Dharma': 'dhr',
        'Emperor': 'emp',
        'Leviathan': 'lev',
        'Origins': 'org',
        'Lions of the North': 'lon',
        'Domination': 'dom',
    }

    def __init__(self, name: str, display_name: str, category: str, archive: Path = None):
        super().__init__(name, display_name)
        self.category = category
        self.archive = archive
        if display_name in self.short_names:
            self.short_name = self.short_names[display_name]
        else:
            self.short_name = ''

        self._open_dlc_archive = None

    def get_icon(self):
        if self.short_name != '':
            return '{{icon|' + self.short_name + '}}'
        else:
            return self.display_name

    def glob(self, glob: str):
        with ZipFile(self.archive) as dlc_archive:
            # store opened archive so that get_file_contents doesn't have to open it again
            self._open_dlc_archive = dlc_archive
            for filename in dlc_archive.namelist():
                if PurePath(filename).match(glob):
                    yield zipfile.Path(dlc_archive, filename)
            self._open_dlc_archive = None

    def get_file_contents(self, filepath):
        if self._open_dlc_archive:
            with self._open_dlc_archive.open(filepath) as file:
                return file.read()
        else:
            with ZipFile(self.archive) as dlc_archive:
                with dlc_archive.open(filepath) as file:
                    return file.read()


class BaseGame(DLC):

    def __init__(self, ck2parser):
        super().__init__('base', 'Base game', '')
        self.parser = ck2parser

    def get_icon(self):
        return ''

    def glob(self, glob: str):
        return self.parser.files(glob)

    def get_file_contents(self, filepath):
        with open(self.parser.file(filepath), 'rb') as file:
            return file.read()


class EventPicture:
    def __init__(self, name: str, filename: str, wiki_filename: str, dlc: DLC, overridden_by: list['EventPicture'],
                 sha_hash: str, picture_data: bytes):
        self.name = name
        self.filename = filename
        self.wiki_filename = wiki_filename
        self.dlc = dlc
        self.overridden_by = overridden_by
        self.sha_hash = sha_hash
        self.picture_data = picture_data

#!/usr/bin/env python3
import math
import os
import re
import sys
from locale import strxfrm, setlocale, LC_COLLATE
from operator import attrgetter
from pathlib import Path
from typing import Dict

# the MonumentList needs pyradox which needs to be imported in some way
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../../../../pyradox')
from pyradox.filetype.table import make_table, WikiDialect

# add the parent folder to the path so that imports work even if the working directory is the eu4 folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from eu4.wiki import WikiTextConverter, get_SVersion_header
from eu4.paths import eu4outpath
from eu4.parser import Eu4Parser
from eu4.mapparser import Eu4MapParser
from eu4.eu4lib import GovernmentReform
from eu4.eu4_file_generator import Eu4FileGenerator
from eu4.eventparser import Eu4EventParser
from ck2parser import Obj, Pair



class MonumentList:
    """needs the pyradox import and pdxparse must be in the path"""

    def __init__(self):
        self.parser = Eu4MapParser()
        self.monument_icons = None

    def get_monument_icon(self, monumentid):
        if self.monument_icons is None:
            self.monument_icons = {}
            for n, v in self.parser.parser.parse_file('interface/great_project.gfx'):
                for n2, v2 in v:
                    name = v2['name'].val.replace('GFX_great_project_', '')
                    image = v2['texturefile'].val.replace('gfx//interface//great_projects//', '').replace('.dds', '')
                    self.monument_icons[name] = image
        return self.monument_icons[monumentid]

    def parse_monuments(self):
        monuments = {}
        for monumentid, v in self.parser.parser.merge_parse('common/great_projects/*'):
            name = self.parser.localize(monumentid)
            monument_type = v['type']
            if monument_type == 'canal':
                build_cost = v['build_cost']
                if 'owner' in v['on_built'] and 'add_prestige' in v['on_built']['owner']:
                    prestige_gain = v['on_built']['owner']['add_prestige']
                else:
                    prestige_gain = None
            else:
                build_cost = None
                prestige_gain = None
            provinceID = v['start']
            prov = self.parser.all_provinces[provinceID]
            can_be_moved = v['can_be_moved'].val == 'yes'
            level = v['starting_tier'].val
            if len(v['can_use_modifiers_trigger']) > 0:
                trigger = v['can_use_modifiers_trigger'].str(self.parser.parser)
            else:
                trigger = None
            if len(v['can_upgrade_trigger']) > 0:
                can_upgrade_trigger = v['can_upgrade_trigger'].str(self.parser.parser)
            else:
                can_upgrade_trigger = None
            if len(v['build_trigger']) > 0:
                build_trigger = v['build_trigger'].str(self.parser.parser)
            else:
                build_trigger = None
            if trigger != can_upgrade_trigger:
                print('Warning: can_use_modifiers_trigger is {} but can_upgrade_trigger is {}'.format(trigger,
                                                                                                      can_upgrade_trigger))
            if trigger != build_trigger:
                print('Warning: can_use_modifiers_trigger is {} but build_trigger is {}'.format(trigger, build_trigger))
            if len(v['keep_trigger']) > 0:
                print('Warning: keep_trigger is not empty')
            tier_data = []
            for tier in range(4):
                values = v['tier_{}'.format(tier)]
                upgrade_time = values['upgrade_time'].inline_str(self.parser.parser)[0]
                if tier == 0:
                    expected_upgrade_time = 0
                    expected_upgrade_cost = 0
                if tier == 1:
                    expected_upgrade_time = 120
                    expected_upgrade_cost = 1000
                if tier == 2:
                    expected_upgrade_time = 240
                    expected_upgrade_cost = 2500
                if tier == 3:
                    expected_upgrade_time = 480
                    expected_upgrade_cost = 5000
                if upgrade_time != '{{ months = {} }}'.format(expected_upgrade_time):
                    print('Warning: unexpected upgrade_time "{}" on tier {}'.format(upgrade_time, tier))
                cost_to_upgrade = values['cost_to_upgrade'].inline_str(self.parser.parser)[0]
                if cost_to_upgrade != '{{ factor = {} }}'.format(expected_upgrade_cost):
                    print('Warning: unexpected cost_to_upgrade "{}" on tier {}'.format(cost_to_upgrade, tier))

                if 'province_modifiers' in values and len(values['province_modifiers']) > 0:
                    province_modifiers = values['province_modifiers'].inline_str(self.parser.parser)[0]
                else:
                    province_modifiers = None
                if 'area_modifier' in values and len(values['area_modifier']) > 0:
                    area_modifier = values['area_modifier'].inline_str(self.parser.parser)[0]
                else:
                    area_modifier = None
                if 'region_modifier' in values and len(values['region_modifier']) > 0:
                    region_modifier = values['region_modifier'].inline_str(self.parser.parser)[0]
                else:
                    region_modifier = None
                if 'country_modifiers' in values and len(values['country_modifiers']) > 0:
                    country_modifiers = values['country_modifiers'].inline_str(self.parser.parser)[0]
                else:
                    country_modifiers = None
                if 'on_upgraded' in values and len(values['on_upgraded']) > 0:
                    on_upgraded = values['on_upgraded'].inline_str(self.parser.parser)[0]
                else:
                    on_upgraded = None
                tier_data.append({'province_modifiers': province_modifiers, 'area_modifier': area_modifier,
                                  'region_modifier': region_modifier,
                                  'country_modifiers': country_modifiers, 'on_upgraded': on_upgraded})
            monuments[monumentid] = {'name': name, 'provinceID': provinceID, 'province': prov,
                                     'can_be_moved': can_be_moved, 'level': level, 'trigger': trigger,
                                     'tiers': tier_data, 'build_cost': build_cost, 'type': monument_type,
                                     'build_trigger': build_trigger, 'prestige_gain': prestige_gain,
                                     'icon': self.get_monument_icon(monumentid)}
        return monuments

    @staticmethod
    def _get_unique_key(monument, what, tier=None):
        if tier:
            return '{}_{}_{}'.format(monument, tier, what)
        else:
            return '{}_{}'.format(monument, what)

    @staticmethod
    def simplify_multiple_OR(conditions):
        modified_conditions = []
        or_regex = re.compile(r'^[* ]*(At least one of|Either):$')

        in_or = False
        in_or2 = False
        or_indent = 0
        for line in conditions.splitlines():
            if WikiTextConverter.calculate_indentation(line) <= or_indent:
                in_or = False
                in_or2 = False
            elif in_or2:
                if WikiTextConverter.calculate_indentation(line) <= (or_indent + 1):
                    in_or2 = False
                else:
                    # everything within the second OR can be moved up
                    line = WikiTextConverter.remove_indent(line)
            elif in_or:
                if or_regex.match(line) and WikiTextConverter.calculate_indentation(line) == (or_indent + 1):  # don't match ORs within other conditions
                    in_or2 = True
                    continue  # skip adding this line
            else:
                if or_regex.match(line):
                    in_or = True
                    or_indent = WikiTextConverter.calculate_indentation(line)
            modified_conditions.append(line)
        return_value = '\n'.join(modified_conditions)
        if return_value != conditions:
            # try to simplify some more
            return MonumentList.simplify_multiple_OR(return_value)
        else:
            # nothing was changed, so we stop the recursion
            return return_value

    @staticmethod
    def improve_requirements(requirements):
        culture = r'Culture is ([-a-zA-Z ]*)'
        accept = r'Culture is accepted by its owner'
        replacements = [
            (r'^([*]*)( ?)All of:\n\1\* '+culture+r'\n\1\* '+accept,
             r'\1\2{{icon|culture|24px}} Culture is \3 and is accepted by its owner'),
            (r'^([* ]*)'+culture+r'\n\1'+accept,
             r'\1{{icon|culture|24px}} Culture is \2 and is accepted by its owner'),
            (r'^([*]*)( ?)At least one of:\n\1\* ' +culture+r'\n\1\* '+culture+r'\n\1\2'+accept,
             r"\1\2{{icon|culture|24px}} Culture is \3 ''or'' \4 and is accepted by its owner"),
            (r'^([*]*)( ?)At least one of:\n\1\* '+culture+r'\n\1\* '+culture+r'\n\1\* '+culture+r'\n\1\2'+accept,
             r"\1\2{{icon|culture|24px}} Culture is \3, \4 ''or'' \5 and is accepted by its owner"),
        ]

        for pattern, replacement in replacements:
            requirements = re.sub(pattern, replacement, requirements, flags=re.MULTILINE)

        # without multiline so that it matches all requirements to make sure that there are no other conditions
        requirements = re.sub(r'^([*]*)( ?)At least one of:\n\1\* [^ ]* '+culture+r' and is accepted by its owner\n\1\* [^ ]* '+culture+r' and is accepted by its owner$',
                              r"{{icon|culture|24px}} Culture is \3 ''or'' \4 and is accepted by its owner", requirements)

        requirements = MonumentList.simplify_multiple_OR(requirements)

        return requirements

    def run(self):
        self._writeFile('monuments', self.generate())

    def generate(self):

        wiki_converter = WikiTextConverter()

        trigger_and_effects = {}
        modifiers = {}
        monuments = self.parse_monuments()

        for monument, data in monuments.items():
            if data['trigger']:
                trigger_and_effects[self._get_unique_key(monument, 'trigger')] = data['trigger']
            for tier in range(4):
                tier_data = data['tiers'][tier]
                for mod_type in ['province_modifiers', 'area_modifier', 'region_modifier', 'country_modifiers']:
                    if tier_data[mod_type]:
                        modifiers[self._get_unique_key(monument, mod_type,
                                                       tier)] = wiki_converter.remove_surrounding_brackets(
                            tier_data[mod_type])
                if tier_data['on_upgraded']:
                    trigger_and_effects[self._get_unique_key(monument, 'on_upgraded', tier)] = tier_data['on_upgraded']

        wiki_converter.to_wikitext(province_scope=trigger_and_effects, modifiers=modifiers, strip_icon_sizes=True)

        trigger_effects_modifiers = {**trigger_and_effects, **modifiers}

        for monument, data in monuments.items():
            if data['trigger']:
                # add linebreak because the conditions are lists
                data['Requirements'] = '\n' + wiki_converter.remove_superfluous_indents(
                    self.improve_requirements(trigger_and_effects[self._get_unique_key(monument, 'trigger')]))
            else:
                data['Requirements'] = ''
            for tier in range(1, 4):
                effects = ''
                tier_data = data['tiers'][tier]
                for effect_type, description in {'province_modifiers': 'Province modifiers',
                                                 'area_modifier': 'Area modifiers',
                                                 'region_modifier': 'Region modifiers',
                                                 'country_modifiers': 'Global modifiers',
                                                 'on_upgraded': 'When upgraded'}.items():
                    if self._get_unique_key(monument, effect_type, tier) in trigger_effects_modifiers:
                        effects_list = trigger_effects_modifiers[self._get_unique_key(monument, effect_type, tier)]
                        # indenting the effects compared to the description looks better, but there is not enough space
                        # in the table in the current layout
                        # effects_list = wiki_converter.add_indent(effects_list)
                        effects += '\n' + description + ':\n{{plainlist|\n' + effects_list + '\n}}'
                data['tier_' + str(tier)] = effects

        monuments = {k: v for (k, v) in monuments.items() if v['type'] == 'monument'}

        monuments = dict(sorted(monuments.items(), key=lambda x: x[1]['name']))
        for i, monument in enumerate(monuments.items(), start=1):
            monument[1]['number'] = i

        column_specs = [
            ('', 'id="%(name)s" | %(number)d'),
            ('Name',
             'style="text-align:center; font-weight: bold; font-size:larger" | %(name)s\n\n[[File:%(icon)s.png|%(name)s]]'),
            ('Location', lambda k, v: '{{plainlist|\n*%s\n*%s\n}}\n%s' % (
                v['province'].superregion,
                v['province'].region,
                v['province'])),
            ('Level', '%(level)d'),
            # yes/no style might work better for mobile devices for which the column seems to be broken
            # ('[[File:Great project level icon move.png|24px|Can be relocated]]', lambda k,v: 'yes' if v['can_be_moved'] else 'no')
            ('[[File:Great project level icon move.png|24px|Can be relocated]]',
             lambda k, v: '{{icon|%s}}' % ('yes' if v['can_be_moved'] else 'no')),
            ('Requirements', '%(Requirements)s'),
            ('[[File:Great project level icon tier 1.png|24px]] Noteworthy level', '%(tier_1)s'),
            ('[[File:Great project level icon tier 2.png|24px]] Significant level', '%(tier_2)s'),
            ('[[File:Great project level icon tier 3.png|24px]] Magnificent level', '%(tier_3)s'),
        ]

        dialect = WikiDialect
        dialect.row_cell_begin = lambda s: ''
        dialect.row_cell_delimiter = '\n| '

        table = make_table(monuments, 'wiki', column_specs, table_style='', table_classes=['mildtable'], sortable=True)
        return get_SVersion_header(scope='table') + '\n' + table

    @staticmethod
    def _writeFile(name, content):
        output_file = eu4outpath / 'eu4{}.txt'.format(name)
        with output_file.open('w') as f:
            f.write(content)


class AreaAndRegionsList:

    def __init__(self):
        self.parser = Eu4MapParser()

    def formatSuperRegions(self):
        lines = ['{{MultiColumn|']
        for superregion in self.parser.all_superregions.values():
            if not superregion.contains_land_provinces:
                continue
            lines.append('; {} subcontinent'.format(superregion.display_name))
            for region in superregion.regions:
                lines.append('* {}'.format(region.display_name))
            lines.append('')  # blank lines to separate the superregions
        lines.pop()  # remove last blank line
        lines.append('|4}}')
        return '\n'.join(lines)

    def formatSeaRegions(self):
        regionsWithInlandSeas = [region for region in self.parser.all_regions.values() if region.contains_inland_seas]
        regionsWithOnlyHighSeas = [region for region in self.parser.all_regions.values() if
                                   not region.contains_inland_seas and not region.contains_land_provinces]

        lines = ['{{MultiColumn|']
        lines.append('; With some inland sea zones {{icon|galley}}')
        for region in regionsWithInlandSeas:
            lines.append('* {}'.format(region.display_name))
        lines.append('')  # blank lines to separate the superregions

        lines.append('; Without any inland sea zones')
        for region in regionsWithOnlyHighSeas:
            lines.append('* {}'.format(region.display_name))
        lines.append('|4}}')
        return '\n'.join(lines)

    def formatLandAreas(self):
        lines = ['{{MultiColumn|']
        regionsWithRegionInLink = [country.display_name for country in self.parser.all_countries.values()]
        regionsWithRegionInLink.append('Britain')

        for region in sorted(self.parser.all_regions.values(), key=lambda r: strxfrm(r.display_name)):
            if not region.contains_land_provinces:
                continue
            if region.display_name in regionsWithRegionInLink:
                link = '{0} (region)|{0}'.format(region.display_name)
            else:
                link = region.display_name
            lines.append('; [[{}]]'.format(link))
            for area in region.areas:
                lines.append('* {}'.format(area.display_name))
            lines.append('')  # blank lines to separate the regions
        lines.pop()  # remove last blank line
        lines.append('|5}}')
        return '\n'.join(lines)

    def formatSeaAreas(self):
        lines = ['{{MultiColumn|']

        for region in sorted(self.parser.all_regions.values(), key=lambda r: strxfrm(r.display_name)):
            if region.contains_land_provinces:
                continue
            lines.append('; {}'.format(region.display_name))
            for area in region.areas:
                lines.append('* {}'.format(area.display_name))
            lines.append('')  # blank lines to separate the regions
        lines.pop()  # remove last blank line
        lines.append('|5}}')
        return '\n'.join(lines)

    def formatSuperregionsColorTable(self):
        lines = ['{| class="wikitable" style="float:right; clear:right; width:300px; text-align:center; "',
                 '|+ Subcontinents',
                 '|']
        sregions_per_column = math.ceil(
            len([s for s in self.parser.all_superregions.values() if s.contains_land_provinces]) / 3)
        columns = []
        currentColumn = []
        for i, sregion in enumerate(self.parser.all_superregions.values()):
            if not sregion.contains_land_provinces:
                continue
            color = self.parser.color_list[i]
            currentColumn.append(
                '| style="background-color:{}"|{}'.format(color.get_css_color_string(), sregion.display_name))
            if len(currentColumn) == sregions_per_column:
                columns.append('{| style="width:100px;"\n' + '\n|-\n'.join(currentColumn) + '\n|}')
                currentColumn = []
        columns.append('{| style="width:100px;"\n' + '\n|-\n'.join(currentColumn) + '\n|}')
        lines.append('\n|\n'.join(columns))
        lines.append('|}')
        return '\n'.join(lines)

    def formatEstuaryList(self):
        lines = [get_SVersion_header(),
                 '{{desc|Estuary|' + self.parser.localize('desc_river_estuary_modifier') + '}}',
                 'River estuaries give {{icon|local trade power}} {{green|+10}} local trade power.<ref name="emod">See in {{path|common/event_modifiers/00_event_modifiers.txt}}</ref> ',
                 '{{MultiColumn|'
                 ]
        estuary_lines = []
        for estuary, provinces in self.parser.estuary_map.items():
            if len(provinces) > 1:
                ref = '<ref name=split>The estuary is shared between two provinces in which case both receive {{icon|local trade power|24px}} {{green|+5}} local trade power.</ref> '
            else:
                ref = ''
            estuary_lines.append('* {} ({}){}'.format(
                ' and '.join([p.name for p in provinces]),
                self.parser.localize(estuary)
                , ref

            ))
        lines.extend(sorted(estuary_lines))
        lines.append('|4}}')

        return '\n'.join(lines)

    def writeSuperRegionsList(self):
        self.writeFile('superregions',
                       self.formatSuperregionsColorTable() + '\n\nAll of the land regions are grouped together to form the following in-game subcontinents:\n' + self.formatSuperRegions())

    def writeSeaRegionsList(self):
        self.writeFile('searegions', self.formatSeaRegions())

    def writeLandAreaList(self):
        self.writeFile('landareas', self.formatLandAreas())

    def writeSeaAreaList(self):
        self.writeFile('seaareas', self.formatSeaAreas())

    def writeEstuaryList(self):
        self.writeFile('estuaries', self.formatEstuaryList())

    def writeFile(self, name, content):
        output_file = eu4outpath / 'eu4{}.txt'.format(name)
        with output_file.open('w') as f:
            f.write(content)


class GovernmentReforms:
    icon_map = {'admiral_king_reform': 'Reform admiral king', 'admiralty_reform': 'Reform admiralty',
                'all_under_tengri_reform': 'Reform all under tengri',
                'austrian_archduchy_reform': 'Reform austrian archduchy',
                'austrian_dual_monarchy_reform': 'Reform austrian dual monarchy',
                'become_rev_empire_reform': 'Reform become rev empire',
                'become_rev_republic_reform': 'Reform become rev republic', 'black_army_reform': 'Black army reform',
                'church_and_state_reform': 'Reform church and state', 'commander_king_reform': 'Reform commander king',
                'conciliarism_reform': 'Reform conciliarism',
                'consolidate_power_in_cities_reform': 'Reform consolidate power in cities',
                'consolidate_power_in_doge_reform': 'Reform consolidate power in doge',
                'crown_highlighted': 'Crown highlighted', 'divine_guidance_reform': 'Reform divine guidance',
                'egalite_reform': 'Reform egalite',
                'emperor_of_the_revolution_reform': 'Reform emperor of the revolution',
                'enlightened_monarchy_reform': 'Reform enlightened monarchy',
                'equal_electorate_reform': 'Reform equal electorate', 'feuillant_reform': 'Reform feuillant',
                'fraternite_reform': 'Reform fraternite',
                'government_for_people_reform': 'Reform government for people',
                'holy_state_reform': 'Reform holy state', 'horde_riding_highlighted': 'Horde riding highlighted',
                'imperial_nobility_reform': 'Reform imperial nobility',
                'integrated_sejmiks_reform': 'Integrated sejmiks reform', 'king_2_highlighted': 'King 2 highlighted',
                'king_highlighted': 'King highlighted', 'kingdom_of_god': 'Reform kingdom of god',
                'legion_of_honor_reform': 'Reform legion of honor',
                'legislative_assembly_reform': 'Reform legislative assembly',
                'legislative_sejm_reform': 'Legislative sejm reform', 'liberte_reform': 'Reform liberte',
                'military_dictatorship_reform': 'Reform military dictatorship',
                'mission_to_civilize_reform': 'Reform mission to civilize',
                'mission_to_kill_pirates_reform': 'Reform mission to kill pirates',
                'monastic_breweries_reform': 'Reform monastic breweries',
                'monastic_elections_reform': 'Reform monastic elections', 'muslim_highlighted': 'Muslim highlighted',
                'national_constituent_reform': 'Reform national constituent',
                'native_clan_council_reform': 'Native clan council reform',
                'native_codified_power_reform': 'Native codified power reform',
                'native_land_tradition_reform': 'Native land tradition reform',
                'native_martial_tradition_reform': 'Native martial tradition reform',
                'native_oral_tradition_reform': 'Native oral tradition reform',
                'native_seasonal_travel_reform': 'Native seasonal travel reform',
                'native_settle_down_reform': 'Native settle down reform',
                'native_trading_with_foreigners_reform': 'Native trading with foreigners reform',
                'native_war_band_reform': 'Native war band reform',
                'organising_our_religion_reform': 'Reform organising our religion',
                'parliament_highlighted': 'Parliament highlighted',
                'partial_secularisation_reform': 'Reform partial secularisation',
                'pope_highlighted': 'Pope highlighted',
                'protectorate_parliament_reform': 'Reform protectorate parliament',
                'regionally_elected_commanders': 'Reform regionally elected commanders',
                'religious_harmony_reform': 'Reform religious harmony',
                'religious_leader_highlighted': 'Religious leader highlighted',
                'religious_permanent_revolution_reform': 'Reform religious permanent revolution',
                'revolutionary_council_reform': 'Reform revolutionary council',
                'sakdina_system_reform': 'Sakdina system reform', 'signoria_reform': 'Reform signoria',
                'three_classes_reform': 'Reform three classes', 'united_cantons_reform': 'Reform united cantons',
                'uparaja_reform': 'Uparaja reform', 'warrior_monks_reform': 'Reform warrior monks'}
    table_header = '''{| class="mildtable sortable" style="width:100%"
! style="width:150px" | Type
! style="width:300px" class="unsortable" | Effects
! class="unsortable" | Description & notes'''

    icon_table_header = '''{{| class="eu4box-inline mw-collapsible mw-collapsed" style="text-align: center; margin: auto; max-width: 550px;"
|+ <span style="white-space: nowrap;">{{{{icon|gov_{icon}|32px}}}} \'\'\'{adjective} government reforms\'\'\'</span>'''

    def __init__(self):
        self.parser = Eu4Parser()
        self._reforms_have_been_converted_to_wikitext = False

    def get_icon(self, reform):
        if reform.icon in self.icon_map:
            return self.icon_map[reform.icon]
        else:
            return self.pretty_icon_name('Gov ' + reform.icon)

    def pretty_icon_name(self, icon):
        return icon.capitalize().replace('_', ' ')

    def create_icon_mapping(self):
        name_icon_mapping = {}
        with open(Path('~/Daten/eu4/temp/2022-09-14_reform_icons.txt').expanduser()) as file:
            for icon, name in re.findall(r'\{\{Navicon\|([^|]*)\|([^}]*)}}', file.read()):
                name_icon_mapping[name] = self.pretty_icon_name(icon)
        reform_icon_mapper = {}
        gov_counter = 0
        reform_counter = 0
        found_counter = 0
        total = 0
        for reform in self.parser.all_government_reforms.values():
            if reform.basic_reform:
                continue
            if reform.display_name in name_icon_mapping:
                total += 1
                icon = self.pretty_icon_name(reform.icon)
                if icon != name_icon_mapping[reform.display_name]:
                    gov_icon = self.pretty_icon_name('Gov ' + icon)
                    if gov_icon != name_icon_mapping[reform.display_name]:
                        reform_icon = self.pretty_icon_name('Reform ' + icon.replace(' reform', ''))
                        if reform_icon != name_icon_mapping[reform.display_name]:
                            print('different icons "{}" / "{}" for {}'.format(name_icon_mapping[reform.display_name],
                                                                              icon, reform.name))
                        else:
                            reform_icon_mapper[reform.icon] = reform_icon
                            reform_counter += 1
                    else:

                        gov_counter += 1
                else:
                    reform_icon_mapper[reform.icon] = icon
                    found_counter += 1
            else:
                print('missing reform: {}'.format(reform.display_name))
        print(dict(sorted(reform_icon_mapper.items())))
        print('total: {}, gov: {}, reform: {}, found: {}, not found: {}'.format(total, gov_counter, reform_counter,
                                                                                found_counter,
                                                                                total - gov_counter - found_counter - reform_counter))

    def run(self):
        for gov_type, adjective in [('monarchy', 'Monarchic'), ('republic', 'Republican'), ('theocracy', 'Theocratic'),
                                    ('tribal', 'Tribal'), ('native', 'Native')]:
            self.writeFile('government_reform_' + gov_type, self.generate(gov_type, adjective))
            self.writeFile('government_reform_' + gov_type + '_icons', self.generate_icon_table(gov_type, adjective))
        self.writeFile('government_reform_common', self.generate_common_reforms())

    def format_reform_attribute(self, attribute_name, value):
        mapping_if_true = {
            'lock_level_when_selected': '* {{Locked reform}}',
            'locked_government_type': '* Prohibits switching [[government type]].',
            'can_use_trade_post': '{{#lst:Republic|trade_post}}',
            'can_form_trade_league': '{{#lst:Republic|trade_league}}',
            'boost_income': '{{#lst:Republic|merchant_republic_mechanics}}<!-- boost_income = yes -->',
            'is_merchant_republic': '{{#lst:Republic|is_merchant_republic}}<!-- is_merchant_republic = yes -->',
            'has_parliament': '* Has access to {{icon|parliament}} parliament',
            'rulers_can_be_generals': '* Rulers can be generals.',
            'heirs_can_be_generals': '* Heirs can be generals.',
            'enables_aristocratic_idea_group': '* Enables the [[Aristocratic ideas|Aristocratic]] idea group.',
            'enables_plutocratic_idea_group': '* Enables the [[Plutocratic]] idea group.',
            'enables_divine_idea_group': '* Enables the [[Idea_groups#Divine|Divine]] idea group.',
            'royal_marriage': '* Allows royal marriages.',
            'militarised_society': '* Uses {{icon|militarization of state}} militarization mechanics\n{{see also|Prussia#Prussian monarchy{{!}}Prussia § Prussian monarchy}}',
            'disables_nobility': '* Disables the {{icon|nobility}} nobility estate.',
            'blocked_call_diet': '* Disables “[[Call diet]]”'
        }
        mapping_if_false = {
            'has_term_election': '* Ruler reigns for life. No elections.',
            'enables_plutocratic_idea_group': '* Disables the [[Plutocratic]] idea group.',
            'enables_aristocratic_idea_group': '* Disables the [[Aristocratic ideas|Aristocratic]] idea group.',
            'enables_divine_idea_group': '* Disables the [[Idea_groups#Divine|Divine]] idea group.',
        }
        if attribute_name in mapping_if_true and value is True:
            return mapping_if_true[attribute_name]
        elif attribute_name in mapping_if_false and value is False:
            return mapping_if_false[attribute_name]
        elif attribute_name == 'fixed_rank':
            if value == 0:
                return '* Unlocks the ability to change [[Government rank]]'
            ranks = ['', 'Duchy', 'Kingdom', 'Empire']
            return '* Fixed rank: {{{{icon|{0}}}}} {0}'.format(ranks[value])
        elif attribute_name == 'trade_city_reform':  # the wiki doesnt really mention it
            return ''

        else:
            if isinstance(value, Obj):
                value = value.str(self.parser.parser)
            return '* <pre>{}: {}</pre>'.format(attribute_name, value)

    def _compare_attributes(self, attributes1, attributes2):
        if len(attributes1) != len(attributes2):
            return False
        for k, v in attributes1.items():
            if k not in attributes2:
                return False
            if type(v) != type(attributes2[k]):
                return False
            if isinstance(v, Obj):
                if v.str(self.parser.parser) != attributes2[k].str(self.parser.parser):
                    return False
            else:
                if v != attributes2[k]:
                    return False

        return True

    def simplify_dlc_conditionals(self, conditionals):
        one_dlc_conditions_mapping = {}
        multiple_dlc_conditions = []
        processed_conditions = []
        for condition, condition_attributes in conditionals:
            if len(condition) > 1 and condition.contents[0].key == 'has_dlc':
                needed_dlcs, not_dlcs = self.get_dlcs(condition)
                if len(needed_dlcs) == 1:
                    if needed_dlcs[0] in one_dlc_conditions_mapping:
                        raise Exception('two conditionals for the same dlc')
                    one_dlc_conditions_mapping[needed_dlcs[0]] = condition_attributes
                    processed_conditions.append((Obj([Pair('has_dlc', needed_dlcs[0])]), condition_attributes))
                else:
                    multiple_dlc_conditions.append((needed_dlcs, condition_attributes))
            else:
                processed_conditions.append((condition, condition_attributes))

        for dlcs, condition_attributes in multiple_dlc_conditions:
            attributes_from_single_dlcs = {k: v for dlc in dlcs for k, v in one_dlc_conditions_mapping[dlc].items()}
            if not self._compare_attributes(attributes_from_single_dlcs, condition_attributes):
                raise Exception('multiple DLC conditions dont match: {}\n{}'.format(attributes_from_single_dlcs, condition_attributes))

        return processed_conditions

    def get_dlcs(self, condition):
        needed_dlcs = []
        not_dlcs = []
        for k, v in condition:
            if k == 'has_dlc':
                needed_dlcs.append(v.val)
            elif k == 'NOT' and len(v) == 1 and v.contents[0].key == 'has_dlc':
                not_dlcs.append(v.contents[0].value.val)
            else:
                raise Exception(
                    'dont know what to do with the dlc condition: {}'.format(condition.str(self.parser.parser)))
        return needed_dlcs, not_dlcs

    def generate_common_reforms(self, excluded_reforms=None):
        if not excluded_reforms:
            excluded_reforms = set()
        print(set(self.parser.common_government_reforms.keys()) - set(excluded_reforms))
        lines = [self.table_header,
                 '! style="width:50px" | {{nowrap|{{icon|monarchy}} Tier}}',
                 '! style="width:50px" | {{nowrap|{{icon|republic}} Tier}}',
                 '! style="width:50px" | {{nowrap|{{icon|theocracy}} Tier}}']
        for reform_id, gov_tiers in self.parser.common_government_reforms.items():
            if reform_id in excluded_reforms:
                continue
            reform = self.parser.all_government_reforms[reform_id]
            lines.append('<section begin={}/>'.format(reform.display_name))
            lines.extend(self.get_reform_lines(reform))
            lines.append('<section end={}/>'.format(reform.display_name))
            for gov_type in ['monarchy', 'republic', 'theocracy']:
                if gov_type in gov_tiers:
                    lines.append('| {}'.format(gov_tiers[gov_type]))
                else:
                    lines.append('|')
            lines.append('|}')
            lines.append('')
        return '\n'.join(lines)

    def generate(self, government_type, adjective, excluded_reforms=None):
        if not excluded_reforms:
            excluded_reforms = set()
        # return self.generate_icon_table(government_type, adjective)
        self.convert_reform_attributes_to_wikitext(self.parser.all_government_reforms)
        lines = []
        for tier, reforms_ids in self.parser.government_type_with_reform_tiers[government_type].items():
            if tier == 'basic' or len(set(reforms_ids) - set(excluded_reforms)) == 0:
                continue
            lines.append('=== {} ==='.format(self.parser.localize(tier)))
            lines.append(self.table_header)
            for reform_id in reforms_ids:
                if reform_id in excluded_reforms:
                    continue
                reform = self.parser.all_government_reforms[reform_id]
                if reform_id in self.parser.common_government_reforms:
                    lines.append('<!-- transcluded from the page "Common government reforms" -->')
                    lines.append('{{{{#lst:Common government reforms|{}}}}}'.format(reform.display_name))
                else:
                    lines.extend(self.get_reform_lines(reform))

                lines.append('')
            lines.append('|}')
            lines.append('')
        return '\n'.join(lines)

    def get_reform_lines(self, reform):
        lines = ['|-', "| id=\"{0}\" | '''{0}'''".format(reform.display_name), '|']
        if reform.modifiers:
            lines.append(reform.modifiers)
        lines.append(
            '| {{{{desc|{}|{}|image={}}}}}'.format(reform.display_name, self.parser.localize(reform.name + '_desc'),
                                                   self.get_icon(reform)))
        if reform.potential:
            lines.append('Conditions to see the reform:')
            lines.append(reform.potential)
        if reform.trigger:
            lines.append('Conditions to enact the reform:')
            lines.append(reform.trigger)
        if reform.potential or reform.trigger:
            lines.append('----')
        if reform.effect:
            lines.append('Effect when enacting:')
            lines.append(reform.effect)
        if reform.removed_effect:
            lines.append('Effect when removing:')
            lines.append(reform.removed_effect)
        if reform.post_removed_effect:
            lines.append('Effect after removing:')
            lines.append(reform.post_removed_effect)
        if reform.effect or reform.removed_effect or reform.post_removed_effect:
            lines.append('----')
        for attribute_name, value in reform.attributes.items():
            lines.append(self.format_reform_attribute(attribute_name, value))
        for condition, condition_attributes in self.simplify_dlc_conditionals(reform.conditional):
            if len(condition) == 1 and condition.contents[0].key == 'has_dlc':
                lines.append('{{{{expansion|{}}}}}'.format(self.parser.dlcs_by_name[condition.contents[0].value].short_name))
            else:
                lines.append(condition.str(self.parser.parser))
            for attribute_name, value in condition_attributes.items():
                lines.append(self.format_reform_attribute(attribute_name, value))
        return lines

    def generate_icon_table(self, government_type, adjective):
        lines = [self.icon_table_header.format(icon=government_type, adjective=adjective)]
        tier_num = 0
        for tier, reforms_ids in self.parser.government_type_with_reform_tiers[government_type].items():
            if tier_num == 0:
                tier_num += 1
                continue
            lines.append('')
            lines.append('|-')
            lines.append('! class="gridBG header" style="text-align: left; color: white;" | Tier {tier_num}: [[#{tier}|{tier}]]'.format(
                tier_num=tier_num,
                tier=self.parser.localize(tier)))
            lines.append('|-')
            lines.append('| {{box wrapper}}')
            for reform_id in reforms_ids:
                reform = self.parser.all_government_reforms[reform_id]
                lines.append('{{{{Navicon|{}|{}}}}}'.format(self.get_icon(reform), reform.display_name))
            lines.append('{{end box wrapper}}')
            tier_num += 1
        lines.append('|}')
        lines.append('')
        return '\n'.join(lines)

    def convert_reform_attributes_to_wikitext(self, reforms: Dict[str, GovernmentReform]):
        if self._reforms_have_been_converted_to_wikitext:
            return reforms
        modifiers = {reform.name: reform.modifiers.str(self.parser.parser) for reform in reforms.values() if reform.modifiers}
        country_scope = {}
        for reform in reforms.values():
            for attribute in ['potential', 'trigger', 'effect', 'removed_effect', 'post_removed_effect']:
                value = getattr(reform, attribute)
                if value:
                    country_scope[reform.name + '_' + attribute] = value.str(self.parser.parser)
        converter = WikiTextConverter()
        converter.to_wikitext(modifiers=modifiers, country_scope=country_scope, strip_icon_sizes=True)

        for reform_name, wikified_modifiers in modifiers.items():
            reforms[reform_name].modifiers = wikified_modifiers

        for reform in reforms.values():
            for attribute in ['potential', 'trigger', 'effect', 'removed_effect', 'post_removed_effect']:
                if getattr(reform, attribute):
                    setattr(reform, attribute, country_scope[reform.name + '_' + attribute])

        self._reforms_have_been_converted_to_wikitext = True
        return reforms

    def writeFile(self, name, content):
        output_file = eu4outpath / 'eu4{}.txt'.format(name)
        with output_file.open('w') as f:
            f.write(content)


class EventPicturesList(Eu4FileGenerator):
    parser: Eu4EventParser

    def __init__(self):
        super().__init__()
        self.parser = Eu4EventParser()

    def generate_event_pictures(self) -> str:
        table_data = []
        for sha, pictures in self.parser.event_pictures_by_hash.items():
            names = []
            dlcs = sorted(set(p.dlc for p in pictures), key=attrgetter('archive'))
            filenames = sorted(set(p.filename.removeprefix("gfx/event_pictures/") for p in pictures))
            for p in pictures:
                name = p.name
                if len(dlcs) > 1:
                    name += ' (' + p.dlc.get_icon() + ')'
                if len(p.overridden_by) > 0:
                    name += ' (' + ', '.join([f'Replaced by [[#{o.filename.removeprefix("gfx/event_pictures/")}|{o.filename.removeprefix("gfx/event_pictures/")}]] with {o.dlc.get_icon()}' for o in p.overridden_by]) + ')'
                names.append(name)
            table_data.append({
            'File': f'id="{pictures[0].filename.removeprefix("gfx/event_pictures/")}"|[[File:{pictures[0].wiki_filename}|frame|{", ".join(filenames)}]]',
            'Names': self.create_wiki_list(names),
            'DLC': ' / '.join(dlc.get_icon() for dlc in dlcs),
        })
        table = self.make_wiki_table(table_data, table_classes=['mildtable', 'plainlist'],
                                     one_line_per_cell=True,
                                     )

        return self.get_SVersion_header() + '\n' + table

    def generate_event_picture_overview(self):
        dlc_names = [pictures[0].dlc.display_name for pictures in self.parser.event_pictures_by_hash.values()]
        dlc_names = list(dict.fromkeys(dlc_names))  # remove duplicates without changing order
        lines = [self.get_SVersion_header()]
        for dlc in dlc_names:
            lines.append(f'===={dlc}====')
            dlc_pictures = [p for p in self.parser.event_pictures_by_hash.values() if p[0].dlc.display_name == dlc]
            for pictures in dlc_pictures:
                lines.append(f'[[File:{pictures[0].wiki_filename}|128px|link=#{pictures[0].filename.removeprefix("gfx/event_pictures/")}|{", ".join(sorted(p.name for p in pictures))}]]')
        return '\n'.join(lines)

    def generate_event_picture_unused(self):
        table_data = []
        for sha, pictures in self.parser.unused_event_pictures_by_hash.items():
            dlcs = sorted(set(p.dlc for p in pictures), key=attrgetter('archive'))
            filenames = sorted(set(p.filename.removeprefix("gfx/event_pictures/") for p in pictures))
            table_data.append({
                'File': f'id="{pictures[0].filename.removeprefix("gfx/event_pictures/")}"|[[File:{pictures[0].wiki_filename}]]',
                'Filenames': self.create_wiki_list(filenames),
                'DLC': ' / '.join(dlc.get_icon() for dlc in dlcs),
            })
        table = self.make_wiki_table(table_data, table_classes=['mildtable', 'plainlist'],
                                     one_line_per_cell=True,
                                     )

        return self.get_SVersion_header('table') + '\n' + table


if __name__ == '__main__':
    # for correct sorting. en_US seems to work even for non english characters, but the default None sorts all non-ascii characters to the end
    setlocale(LC_COLLATE, 'en_US.utf8')
    GovernmentReforms().run()
    MonumentList().run()
    EventPicturesList().run([])

    list_generator = AreaAndRegionsList()
    list_generator.writeSuperRegionsList()
    list_generator.writeSeaRegionsList()
    list_generator.writeLandAreaList()
    list_generator.writeSeaAreaList()
    list_generator.writeEstuaryList()

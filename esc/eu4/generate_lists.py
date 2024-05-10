#!/usr/bin/env python3
import math
import os
import re
import sys
from locale import strxfrm, setlocale, LC_COLLATE
from operator import attrgetter
from pathlib import Path
from typing import Dict

from common.wiki import WikiTextFormatter

# the MonumentList needs pyradox which needs to be imported in some way
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../../../../pyradox')
from pyradox.filetype.table import make_table, WikiDialect

# add the parent folder to the path so that imports work even if the working directory is the eu4 folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from eu4.wiki import WikiTextConverter, get_SVersion_header
from eu4.paths import eu4outpath
from eu4.parser import Eu4Parser
from eu4.mapparser import Eu4MapParser
from eu4.eu4lib import GovernmentReform, Country, Estate, ColonialRegion, Culture
from eu4.eu4_file_generator import Eu4FileGenerator
from eu4.eventparser import Eu4EventParser
from ck2parser import Obj, Pair


class PdxparseToList(Eu4FileGenerator):

    def __init__(self):
        super().__init__()
        self.wiki_converter = WikiTextConverter()

    @staticmethod
    def _add_element_to_dict_and_create_list_for_duplicates(key, value, dictionary):
        if key in dictionary:
            if not isinstance(dictionary[key], list):
                dictionary[key] = [dictionary[key]]
            dictionary[key].append(value)
        else:
            dictionary[key] = value

    def get_data_from_files(self, glob, province_scope=[], country_scope=[], modifier_scope=[], extra_handlers=None, key_value_pair_list=[],
                            ignored=[], ignored_elements=[], localisation_with_title=False, localise_desc=False):
        if not extra_handlers:
            extra_handlers = {}
        province_params = {}
        country_params = {}
        modifier_params = {}
        extra_sections = {}
        key_value_pairs = {}
        unhandled_sections = {}
        elements = {}
        for element_id, data in self.parser.parser.merge_parse(glob):
            if element_id in ignored_elements:
                continue
            if localisation_with_title:
                elements[element_id] = self.parser.localize(element_id + '_title')
            else:
                elements[element_id] = self.parser.localize(element_id)
                # print(elements[element_id].replace('§J', '').replace('§!', ''))

            unhandled_sections[element_id] = ''
            for section_name, section_data in data:
                if section_name in province_scope:
                    self._add_element_to_dict_and_create_list_for_duplicates(f'{element_id}__{section_name}', section_data.inline_str(self.parser.parser)[0], province_params)
                elif section_name in country_scope:
                    self._add_element_to_dict_and_create_list_for_duplicates(f'{element_id}__{section_name}', section_data.inline_str(self.parser.parser)[0], country_params)
                elif section_name in modifier_scope:
                    self._add_element_to_dict_and_create_list_for_duplicates(f'{element_id}__{section_name}', section_data.inline_str(self.parser.parser)[0], modifier_params)
                elif section_name in extra_handlers:
                    self._add_element_to_dict_and_create_list_for_duplicates(f'{element_id}__{section_name}', extra_handlers[section_name](section_data), extra_sections)
                elif section_name in key_value_pair_list:
                    self._add_element_to_dict_and_create_list_for_duplicates(f'{element_id}__{section_name}', section_data.val, key_value_pairs)
                elif section_name in ignored:
                    pass
                else:
                    print(f'Warning: unhandled section "{section_name}" in "{element_id}"')
                    unhandled_sections[element_id] += f'\n{section_name} = {{\n{section_data}\n}}'

        self.wiki_converter.to_wikitext(province_scope=province_params, country_scope=country_params,
                                   modifiers=modifier_params, strip_icon_sizes=True)

        results = []
        for element_id, name in elements.items():
            result = {'id': element_id, 'name': name}
            if localise_desc:
                result['desc'] = self.parser.localize(element_id + '_desc')
            merged_sections = province_params | country_params | modifier_params | extra_sections | key_value_pairs
            for section_name in province_scope + country_scope + modifier_scope + list(extra_handlers.keys()) + key_value_pair_list:
                if f'{element_id}__{section_name}' in merged_sections:
                    result[section_name] = merged_sections[f'{element_id}__{section_name}']
                    if type(result[section_name]) == str and result[section_name].startswith('*'):
                        result[section_name] = '\n' + result[section_name]
                else:
                    result[section_name] = ''
            result['unhandled'] = unhandled_sections[element_id]
            results.append(result)

        return results


class Achievements(PdxparseToList):

    def __init__(self, min_id=0):
        super().__init__()
        self.min_id = min_id

    def remove_common_starting_conditions(self, conditions):

        regexes = [r'\* None of:\n\*\* <pre>num_of_custom_nations = 1</pre>',
                   r'\* Playing with normal or historical nations',
                   r'\* <pre>normal_province_values = yes</pre>',
                   r'\* <pre>ironman = yes</pre>',
                   r'\* The game is {{icon\|ironman}} ironman',
                   r'\* <pre>start_date = 1444.11.11</pre>']

        for regex in regexes:
            # to avoid empty lines, we remove a newline at the end if there is one(the last condition doesnt have a newline)
            conditions = re.sub(regex + r'\n?', '', conditions, flags=re.MULTILINE)
        if conditions.startswith('*'):
            conditions = '\n' + conditions
        return conditions

    def generate_achievement_list(self):
        currentVersion = self.parser.eu4_major_version.removeprefix('1.')
        achievements = [{
            'style="width:20%;" | Achievement': ' {{Achievement|' + self.parser.localize(achievement['localization'] + '_NAME') + '|' + self.parser.localize(achievement['localization'] + '_DESC') + '|extension=png}}',
            'class="mildtable sortable plainlist" style="width:18% | Starting conditions': self.remove_common_starting_conditions(achievement['possible']),
            'class="mildtable sortable plainlist" style="width:22%;" | Completion requirements': achievement['happened'],
            'class="mildtable sortable plainlist" style="width:37%;" | Notes': '',
            '{{icon|eu4|21px}}': '',
            'Ver': 'data-sort-value="{0}" | [[1.{0}]]'.format(currentVersion),
            'DI': '{{DI|UC}}',

        } for achievement in self.get_data_from_files('common/achievements.txt',
                                                      country_scope=['possible', 'happened'],
                                                      extra_handlers={'localization': lambda x: x,  # pass through localisation key for later
                                                                      'id': lambda x: x},
                                                      ignored=['visible', 'provinces_to_highlight']
                                                      ) if achievement['id'] >= self.min_id]
        table = self.make_wiki_table(achievements, one_line_per_cell=True, table_classes=['mildtable', 'plainlist'])

        return self.get_SVersion_header('table') + '\n' + table


class EocReforms(PdxparseToList):

    def generate_eoc_reforms_list(self):
        reforms = [{
            'Reform': reform['name'],
            'Trigger': reform['trigger'],
            'Emperor': reform['emperor'],
            'Tributaries': reform['member'],
            'Enacting effect': reform['on_effect'],
            'Revoking effect': reform['off_effect'],
            'Description': reform['desc'],
        } for reform in self.get_data_from_files('common/imperial_reforms/01_china.txt',
                                                 country_scope=['trigger', 'on_effect', 'off_effect'],
                                                 modifier_scope=['member', 'emperor'],
                                                 ignored=['empire'], localisation_with_title=True,
                                                 localise_desc=True)]
        table = self.make_wiki_table(reforms, one_line_per_cell=True)

        return self.get_SVersion_header('table') + '\n' + table


class EstatePrivileges(PdxparseToList):

    def __init__(self):
        super().__init__()
        self.all_privileges = None

    def passthrough_handler(self, section_data):
        return self.wiki_converter.remove_surrounding_brackets(section_data.inline_str(self.parser.parser)[0])

    def get_privileges_for_estate(self, estate: Estate):
        if not self.all_privileges:
            self.all_privileges = {}
            for privilege in self.get_data_from_files('common/estate_privileges/*',
                                country_scope = ['is_valid', 'can_select', 'can_revoke', 'on_granted', 'on_revoked', 'on_invalid', 'on_cooldown_expires'],
                                province_scope=['on_granted_province', 'on_invalid_province', 'on_revoked_province'],
                                modifier_scope = ['benefits', 'penalties', 'modifier_by_land_ownership'],
                                ignored = ['ai_will_do'],
                                key_value_pair_list=['icon', 'max_absolutism', 'influence', 'loyalty', 'land_share', 'cooldown_years'],
                                extra_handlers={'conditional_modifier': self.passthrough_handler,
                                                'loyalty_scaled_conditional_modifier': self.passthrough_handler,
                                                'influence_scaled_conditional_modifier': self.passthrough_handler,
                                                'mechanics': self.passthrough_handler,
                                                },
                                localise_desc=True):
                self.all_privileges[privilege['id']] = privilege
        return [self.all_privileges[name] for name in estate.privileges]

    @staticmethod
    def _format_conditional_modifiers(modifier_code):
        strip_re = re.compile(r'^\t', flags=re.MULTILINE)
        if not isinstance(modifier_code, list):
            modifier_code = [modifier_code]
        stripped_code = [
            strip_re.sub('', code)
            for code in modifier_code
            if code and not code.isspace()
        ]
        if len(stripped_code) > 0:
            return '<pre>' + ('</pre>\n----\n<pre>'.join(stripped_code)) + '</pre>'
        else:
            return ''

    def estate_privileges_list(self, estate: Estate):
        formatter = WikiTextFormatter()
        privileges = [{
            'id': privilege['name'],
            'class="unsortable" | [[File:Privilege_check.png|28px]]': f"[[File:{privilege['icon'].replace('_', ' ')}.png]]",
            'Privilege': privilege['name'],
            '[[File:Crownland.png|28px|Crownland share change]]': formatter.add_red_green(privilege["land_share"] * -1) if privilege["land_share"] else '',
            '{{icon|max absolutism}}': formatter.add_red_green(privilege["max_absolutism"]) if privilege["max_absolutism"] else '',
            '{{icon|friendly attitude|Estate loyalty equilibrium change}}': formatter.add_red_green(privilege["loyalty"] * 100) if privilege["loyalty"] else '',
            '{{icon|estate influence|Estate influence change}}': formatter.add_plus_minus(privilege["influence"] * 100, bold=True) if privilege['influence'] else '',
            'is_valid': privilege['is_valid'],
            'can_select': privilege['can_select'],
            'can_revoke': privilege['can_revoke'],
            'on_granted': privilege['on_granted'],
            'on_revoked': privilege['on_revoked'],
            'on_invalid': privilege['on_invalid'],
            'on_cooldown_expires': privilege['on_cooldown_expires'],
            'on_granted_province': privilege['on_granted_province'],
            'on_invalid_province': privilege['on_invalid_province'],
            'on_revoked_province': privilege['on_revoked_province'],
            'benefits': privilege['benefits'],
            'penalties': privilege['penalties'],
            'conditional_modifier': self._format_conditional_modifiers(privilege['conditional_modifier']),
            'modifier_by_land_ownership': privilege['modifier_by_land_ownership'],
            'loyalty_scaled_conditional_modifier': self._format_conditional_modifiers(privilege['loyalty_scaled_conditional_modifier']),
            'influence_scaled_conditional_modifier': self._format_conditional_modifiers(privilege['influence_scaled_conditional_modifier']),
            'cooldown_years': privilege['cooldown_years'],
            'mechanics': privilege['mechanics'],
            'Description': privilege['desc'],
        } for privilege in self.get_privileges_for_estate(estate)]
        table = self.make_wiki_table(privileges, one_line_per_cell=True, row_id_key='id')

        return f'=={estate.display_name}==\n{self.get_SVersion_header("table")}\n{table}\n'

    def run_for_all_estates(self):
        for estate in self.parser.all_estates.values():
            self._write_text_file(f'{estate.name}_privileges', self.estate_privileges_list(estate))


class MercenaryList(PdxparseToList):

    parser: Eu4MapParser

    def __init__(self):
        super().__init__()
        self.parser = Eu4MapParser()

    @staticmethod
    def get_composition(data):
        formatted = []
        if data['cavalry_weight'] != '' or data['artillery_weight'] != '':
            infantry = 1
            formatted.append('infantryplaceholder')
            if data['cavalry_weight']:
                cavalry_text = f"{data['cavalry_weight']:.0%} {{{{icon|cavalry}}}} cavalry"
                if data['cavalry_cap']:
                    cavalry_text += f' (capped at {data["cavalry_cap"]} regiments)'
                formatted.append(cavalry_text)
                infantry -= data['cavalry_weight']
            if data['artillery_weight']:
                try:
                    formatted.append(f"{data['artillery_weight']:.0%} {{{{icon|artillery}}}} artillery")
                    infantry -= data['artillery_weight']
                except:
                    print(data['artillery_weight'])
            formatted[0] = f"{infantry:.0%} {{{{icon|infantry}}}} infantry"
        if data['min_size'] and data['min_size'] != 4:
            formatted.append(f"Minimum size: '''{data['min_size']}'''")
        if data['max_size']:
            formatted.append(f"Maximum size: '''{data['max_size']}'''")
        return '<br/>'.join(formatted)

    def get_home_province(self, data):
        if data['home_province']:
            return str(self.parser.all_provinces[data['home_province']])
        else:
            return ''

    def get_cost_modifier(self, data):
        if data['cost_modifier']:
            try:

                if data['cost_modifier'] < 1:
                    return f'{{{{green|×{data["cost_modifier"]}}}}}'
                elif data['cost_modifier'] > 1:
                    return f'{{{{red|×{data["cost_modifier"]}}}}}'
            except:
                print('cost mod: ', data['cost_modifier'])
        return ''

    def get_modifiers(self, data):
        modifiers = data['modifier']
        if data['manpower_pool']:
            modifiers += f"\n* {{{{icon|mercenary manpower}}}} {{{{green|{data['manpower_pool'] * 1000}}}}} Manpower pool independent of the size"
        if data['no_additional_manpower_from_max_size'] == 'yes':
            modifiers += "\n* ''Manpower pool does not increase after the company has reached its maximum size''"
        if data['counts_towards_force_limit'] == 'no':
            modifiers += "\n* {{green|''Costs no force limit to maintain.''}}"
        if data['mercenary_desc_key']:
            desc = data['mercenary_desc_key']
            if desc == 'FREE_OF_ARMY_PROFESSIONALISM_COST':
                modifiers += "\n* {{green|''Does not reduce Army professionalism when recruited''}}"
            else:
                modifiers += "\n* " + self.parser.localize(desc)
        if modifiers != '':
            modifiers = '{{plainlist|' + modifiers + '\n}}'
        return modifiers

    def filter_conditions(self, conditions: str):
        # remove the default condition with either a preceding or a following linebreak, but don't remove both
        # in case the condition is in the middle
        for filter_condition in ['\n* <pre>is_allowed_to_recruit_mercenaries = yes</pre>',
                                 '* <pre>is_allowed_to_recruit_mercenaries = yes</pre>\n',
                                 '* <pre>is_allowed_to_recruit_mercenaries = yes</pre>']:
            if filter_condition in conditions:
                conditions = conditions.replace(filter_condition, '')
        return conditions

    def generate_mercenary_list(self):
        data = [{
            'Name': item['name'],
            'Regiments per development': item['regiments_per_development'],
            'Army composition': self.get_composition(item),
            'Home province': self.get_home_province(item),
            'Cost modifier': self.get_cost_modifier(item),
            'Conditions': self.filter_conditions(item['trigger']),
            'Modifiers': self.get_modifiers(item),
        } for item in self.get_data_from_files('common/mercenary_companies/*',
                                               country_scope=['trigger'],
                                               modifier_scope=['modifier'],
                                               key_value_pair_list=['regiments_per_development', 'cavalry_weight', 'cavalry_cap', 'artillery_weight', 'min_size', 'max_size', 'home_province',
                                                                    'cost_modifier', 'manpower_pool', 'mercenary_desc_key', 'counts_towards_force_limit', 'no_additional_manpower_from_max_size'],
                                               ignored_elements=['rnw_modifier_weights'],
                                               ignored=['sprites'])]
        table = self.make_wiki_table(data, one_line_per_cell=True)
        return self.get_SVersion_header('table') + '\n' + table


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
                if 'conditional_modifier' in values and len(values['conditional_modifier']) > 0:
                    conditional_modifier = values['conditional_modifier']['modifier'].inline_str(self.parser.parser)[0]
                    conditional_modifier_trigger = values['conditional_modifier']['trigger'].inline_str(self.parser.parser)[0]
                else:
                    conditional_modifier = None
                    conditional_modifier_trigger = None
                tier_data.append({'province_modifiers': province_modifiers, 'area_modifier': area_modifier,
                                  'region_modifier': region_modifier,
                                  'country_modifiers': country_modifiers, 'on_upgraded': on_upgraded,
                                  'conditional_modifier': conditional_modifier,
                                  'conditional_modifier_trigger': conditional_modifier_trigger})
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
            (r'^([*]+) If:\n\1\* Limited to:\n\1\*\* ([^\n]*)\n\1\* ',  # ifs with a single clause
             r'\1 If \2:\n\1* '),
            (r'([*]+) If {{icon\|[^}]*}} [^\n]* estate exists:\n\1\*',
             r'\1')
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
                if tier_data['conditional_modifier']:
                    modifiers[self._get_unique_key(monument, 'conditional_modifier',
                                                   tier)] = wiki_converter.remove_surrounding_brackets(
                        tier_data['conditional_modifier'])
                    trigger_and_effects[self._get_unique_key(monument, 'conditional_modifier_trigger', tier)] = \
                    tier_data['conditional_modifier_trigger']

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
                                                 'conditional_modifier_trigger': 'When the following conditions are met',
                                                 'conditional_modifier': 'then the following modifiers are applied',
                                                 'on_upgraded': 'When upgraded',
                                                 }.items():
                    if self._get_unique_key(monument, effect_type, tier) in trigger_effects_modifiers:
                        effects_list = trigger_effects_modifiers[self._get_unique_key(monument, effect_type, tier)]
                        effects_list = self.improve_requirements(effects_list)
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


class AreaAndRegionsList(Eu4FileGenerator):
    parser: Eu4MapParser

    def __init__(self):
        super().__init__()
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
        return lines

    def generate_searegions(self):
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
        return lines

    def generate_landareas(self):
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
        return lines

    def generate_seaareas(self):
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
        return lines

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
        return lines

    def generate_estuaries(self):
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

        return lines

    def generate_superregions(self):
        return self.formatSuperregionsColorTable() + ['', 'All of the land regions are grouped together to form the following in-game subcontinents:', ] + self.formatSuperRegions()

    def _get_key_provinces(self, region: ColonialRegion) -> str:
        key_provinces = {'cotlvl3': [],
                         'cotlvl2': [],
                         'cotlvl1': [],
                         'estuary': []}
        for province in region.provinces:
            if province in self.parser.all_estuary_provinces:
                key_provinces['estuary'].append(province)
            if province.center_of_trade > 0:
                key_provinces[f'cotlvl{province.center_of_trade}'].append(province)

        lines = [f'{{{{icon|{prov_type}}}}} {", ".join(sorted(province.name for province in provinces))}'
                 for prov_type, provinces in key_provinces.items()
                 if len(provinces) > 0]
        return '{{plainlist|\n' + self.create_wiki_list(lines) + '\n}}'

    def generate_colonial_regions(self):
        return self.get_SVersion_header('table') + '\n' + \
            self.make_wiki_table([{
                'Continent': ', '.join(continent.display_name for continent in region.continents),
                'Colonial region': region,
                'class="unsortable" width="75px" | Colour': f'style="background:{region.color.get_css_color_string()}"|',
                '№ of provinces': len(region.provinces),
                '№ of ports': region.port_count,
                '% ports': f'{region.port_count / len(region.provinces):.0%}',
                'class="unsortable" | Key provinces': self._get_key_provinces(region),
            } for region in self.parser.all_colonial_regions.values()
            ], one_line_per_cell=True)


class GovernmentReforms:

    table_header = '''{| class="mildtable sortable" style="width:100%"
! style="width:150px" | Type
! style="width:300px" class="unsortable" | Effects
! class="unsortable" | Description & notes'''

    icon_table_header = '''{{| class="eu4box-inline mw-collapsible mw-collapsed" style="text-align: center; margin: auto; max-width: 550px;"
|+ <span style="white-space: nowrap;">{{{{icon|gov_{icon}|32px}}}} \'\'\'{adjective} government reforms\'\'\'</span>'''

    def __init__(self):
        self.parser = Eu4Parser()
        self._reforms_have_been_converted_to_wikitext = False

    def create_icon_mapping(self):
        name_icon_mapping = {}
        with open(Path('~/Daten/eu4/temp/2022-09-14_reform_icons.txt').expanduser()) as file:
            for icon, name in re.findall(r'\{\{Navicon\|([^|]*)\|([^}]*)}}', file.read()):
                name_icon_mapping[name] = GovernmentReform.pretty_icon_name(icon)
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
                icon = GovernmentReform.pretty_icon_name(reform.icon)
                if icon != name_icon_mapping[reform.display_name]:
                    gov_icon = GovernmentReform.pretty_icon_name('Gov ' + icon)
                    if gov_icon != name_icon_mapping[reform.display_name]:
                        reform_icon = GovernmentReform.pretty_icon_name('Reform ' + icon.replace(' reform', ''))
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
                        # raise Exception('two conditionals for the same dlc' + str(conditionals))
                        print('two conditionals for the same dlc' + str(conditionals))
                    one_dlc_conditions_mapping[needed_dlcs[0]] = condition_attributes
                    processed_conditions.append((Obj([Pair('has_dlc', needed_dlcs[0])]), condition_attributes))
                else:
                    multiple_dlc_conditions.append((needed_dlcs, condition_attributes))
            else:
                processed_conditions.append((condition, condition_attributes))

        for dlcs, condition_attributes in multiple_dlc_conditions:
            attributes_from_single_dlcs = {}
            for dlc in dlcs:
                if dlc in one_dlc_conditions_mapping:
                    for k, v in one_dlc_conditions_mapping[dlc].items():
                        attributes_from_single_dlcs[k] = v
                else:
                    print('dlc {} missing from {} multiples: '.format(dlc, one_dlc_conditions_mapping))
            if not self._compare_attributes(attributes_from_single_dlcs, condition_attributes):
                # raise Exception('multiple DLC conditions dont match: {}\n{}'.format(attributes_from_single_dlcs, condition_attributes))
                print('multiple DLC conditions dont match: {}\n{}'.format(attributes_from_single_dlcs, condition_attributes))
                return conditionals

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
            lines.append('')
        lines.append('|}')
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
                                                   reform.get_icon()))
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
                lines.append('{{{{Navicon|{}|{}}}}}'.format(reform.get_icon(), reform.display_name))
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


class CountryList(Eu4FileGenerator):
    parser: Eu4MapParser

    link_overrides = {
        'NAT': 'Colonization#Natives',
        'HAW': 'Oceanian_super-region#Hawai\'i'
    }

    flag_overrides = {'HAW': 'HAW.png'}

    def __init__(self):
        super().__init__()
        self.parser = Eu4MapParser()

    def _get_flag_file(self, country: Country):
        if country.tag in self.flag_overrides:
            return self.flag_overrides[country.tag]
        else:
            return f'{country.display_name}.png'

    def _get_link(self, country: Country):
        if country.tag in self.link_overrides:
            return f'[[{self.link_overrides[country.tag]}|{country.display_name}]]'
        else:
            return f'[[{country.display_name}]]'

    def _get_notes(self, tag: str):
        all_formable_tags = self.parser.formable_tags_by_decision | self.parser.formable_tags_by_event | \
                            self.parser.formable_tags_by_mission | self.parser.formable_tags_by_federations

        notes = []
        if tag in all_formable_tags:
            formable_notes = []
            if tag in all_formable_tags - self.parser.formable_tags_by_decision:
                if tag in self.parser.formable_tags_by_decision:
                    formable_notes.append('by decision')
                if tag in self.parser.formable_tags_by_event:
                    formable_notes.append('by event')
                if tag in self.parser.formable_tags_by_mission:
                    formable_notes.append('by mission')
                if tag in self.parser.formable_tags_by_federations:
                    formable_notes.append('by uniting a federation')
            if tag in self.parser.existing_tags:
                formable_notes.append('exists in 1444')
            if formable_notes:
                formable_notes = f' ({", ".join(formable_notes)})'
            else:
                formable_notes = ''
            notes.append(f'[[File:Execute decision.png|link=|28px]] Formable{formable_notes}')
        if tag in self.parser.releasable_tags:
            notes.append('[[File:Liberty desire in subjects.png|link=|28px]] Releasable')
        if tag in self.parser.releasable_tags_by_event and tag not in self.parser.existing_tags:
            notes.append('Appears by event')
        if tag in self.parser.releasable_tags_by_decision and tag not in self.parser.existing_tags:
            notes.append('Appears by decision')
        if tag in self.parser.releasable_tags_by_mission and tag not in self.parser.existing_tags:
            notes.append('Appears by missions')
        if tag not in (all_formable_tags | self.parser.releasable_tags | self.parser.existing_tags |
                       self.parser.releasable_tags_by_event | self.parser.releasable_tags_by_decision |
                       self.parser.releasable_tags_by_mission):
            notes.append('[[File:Separatist rebels.png|link=|18px]] Revolter')

        # special tags override all other notes
        if tag in ['REB', 'PIR', 'NAT']:
            notes = ['Special game tag']
        elif tag in ['JMN', 'SYN']:
            notes = ['Special country (can be spawned only with console)']

        return ' / '.join(notes)

    def _get_capital_location(self, country: Country):
        if country.get_capital_id():
            province = self.parser.all_provinces[country.get_capital_id()]
            return f'{province.superregion} / {province.region} / {province}'
        else:
            return '–'

    def generate_country_list(self):
        countries = [{
            '': i,
            # optional version with colors as discussed on the talk page
            # '': f'style="width: 2px; background-color: {country.get_color().css_color_string}"|{i}',
            'Country': f"[[File:{self._get_flag_file(country)}|50px|border]] '''{self._get_link(country)}'''",
            'Tag': country.tag,
            'Capital Subcontinent / Region / Province': self._get_capital_location(country),
            # 'Capital Province ID': country.get_capital_id(),
            # 'Primary Culture': country.get_primary_culture(),
            # 'Default Religion': country.get_religion(),
            'Notes': self._get_notes(country.tag)
        } for i, country in enumerate(self.parser.all_countries.values(), start=1)]
        table = self.make_wiki_table(countries)

        return self.get_SVersion_header('table') + '\n' + table


class CultureList(Eu4FileGenerator):
    def __init__(self):
        super().__init__()
        self.name_to_culture_map = None

    def _get_extra_text(self, culture: Culture) -> str:
        if self.name_to_culture_map is None:
            name_to_culture_map = {}
            for culture in self.parser.cultures.values():
                if culture.display_name not in name_to_culture_map:
                    name_to_culture_map[culture.display_name] = []
                name_to_culture_map[culture.display_name].append(culture)
            self.name_to_culture_map = name_to_culture_map

        if len(self.name_to_culture_map[culture.display_name]) == 1:
            return ''
        if len(self.name_to_culture_map[culture.display_name]) == 2:
            count = 'two'
        else:
            count = 'multiple'

        return f"<ref name={culture.display_name}>There are {count} cultures with the name ''“{culture.display_name}”'': " + \
            ' and '.join([f"<tt>{culture.name}</tt> in the group ''“{culture.culture_group.display_name}”''" for culture in self.name_to_culture_map[culture.display_name]]) + \
            '</ref>'


    def generate_culture_list(self):
        lines = [self.get_SVersion_header(), '{{Box wrapper}}']
        for group in sorted(self.parser.culture_groups.values(), key=lambda c: strxfrm(c.display_name)):
            lines.append('{{Culture group')
            lines.append(f'|group={group.display_name}')
            lines.append('|cultures=')
            for culture in sorted(group.cultures, key=lambda c: strxfrm(c.display_name)):
                lines.append(f'{{{{Culture|{culture.display_name}{self._get_extra_text(culture)}{"|" + self.parser.all_countries[culture.primary].display_name if culture.primary else ""}}}}}')
            lines.append('}}')
            lines.append('')

        lines.append('{{end box wrapper}}')

        return lines


if __name__ == '__main__':
    # for correct sorting. en_US seems to work even for non english characters, but the default None sorts all non-ascii characters to the end
    setlocale(LC_COLLATE, 'en_US.utf8')
    Achievements(365).run([])
    EstatePrivileges().run_for_all_estates()
    EocReforms().run([])
    GovernmentReforms().run()
    MercenaryList().run([])
    MonumentList().run()
    EventPicturesList().run([])
    CountryList().run([])
    AreaAndRegionsList().run([])
    CultureList().run([])

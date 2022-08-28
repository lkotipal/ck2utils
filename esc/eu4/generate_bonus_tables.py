#!/usr/bin/env python3
import csv
import os
import re
import sys
# add the parent folder to the path so that imports work even if the working directory is the eu4 folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from eu4.paths import eu4_major_version, eu4outpath
from eu4.mapparser import Eu4Parser
from eu4.eu4lib import Idea, Policy
from eu4.modifier_list import all_modifiers


class BonusTableGenerator:

    header = '''<includeonly>{{SVersion|''' + eu4_major_version() + '''|table}}
{{{!}} class="mildtable plainlist mw-collapsible {{#ifeq: {{lc:{{{collapse|}}}}}|yes|mw-collapsed|}}"
! style="width:30px" {{!}} {{icon|{{{1}}}|24px}}
! style="min-width:120px" {{!}} Traditions
! style="min-width:240px" {{!}} Ideas
! style="min-width:120px" {{!}} Bonuses
! style="min-width:240px" {{!}} Policies
{{#switch:{{lc:{{{1}}}}}'''

    footer = '''| national revolt risk
| global revolt risk = {{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">The modifier ''“national revolt risk”'' was removed/renamed with patch 1.8.</span>[[Category:Bonus table outdated]]
| merchant steering towards inland
| merchant steering to inland = {{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">The modifier ''“merchant steering towards inland”'' was removed with patch 1.10.</span>[[Category:Bonus table outdated]]
| building power cost
| build power cost = {{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">The modifier ''“building power cost”'' was removed with patch 1.12.</span>[[Category:Bonus table outdated]]
| goods produced nationally
| global trade goods size = {{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">The modifier ''“goods produced nationally”'' was renamed with patch 1.12.</span>[[Category:Bonus table outdated]]
| national trade income modifier
| global trade income modifier = {{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">The modifier ''“national trade income modifier”'' was removed with patch 1.13.</span>[[Category:Bonus table outdated]]
| time to fabricate claims
| fabricate claims time = {{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">The modifier ''“time to fabricate claims”'' was renamed with patch 1.16.</span>[[Category:Bonus table outdated]]
| time to justify trade conflict
| justify trade conflict time = {{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">The modifier ''“time to justify trade conflict”'' was renamed with patch 1.16.</span>[[Category:Bonus table outdated]]
| national spy defense
| global spy defense = {{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">The modifier ''“national spy defense”'' was renamed with patch 1.16.</span>[[Category:Bonus table outdated]]
| spy offense = {{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">The modifier ''“spy offense”'' was renamed with patch 1.16.</span>[[Category:Bonus table outdated]]
| covert action relation impact
| discovered relations impact = {{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">The modifier ''“covert action relation impact”'' is no more used since patch 1.17.</span>[[Category:Bonus table outdated]]
| accepted culture threshold = {{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">The modifier ''“accepted culture threshold”'' was removed with patch 1.18.</span>[[Category:Bonus table outdated]]
| better relations over time = {{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">The modifier ''“better relations over time”'' was merged with ''“improve_relation_modifier”'' with patch 1.19.</span>[[Category:Bonus table outdated]]
| build cost = {{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">The modifier ''“build cost”'' was renamed to ''“construction cost”'' patch 1.19.</span>[[Category:Bonus table outdated]]
| reduce inflation cost
| inflation reduction cost ={{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">Since patch 1.28 no ideas and policies have the modifier ''“reduce inflation cost”''.</span>[[Category:Bonus table outdated]]
| transport power
| transport combat ability =
{{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">Since patch 1.26 no ideas and policies have the modifier ''“transport combat ability”''.</span>[[Category:Bonus table outdated]]
| number of states =
{{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">The modifier ''“number of states”'' was removed with patch 1.30.</span>[[Category:Bonus table outdated]]
| available mercenaries =
{{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">The modifier ''“available mercenaries”'' was replaced by ''“mercenary manpower”'' with patch 1.30.</span>[[Category:Bonus table outdated]]
| migration cooldown =
{{!}}-
{{!}}colspan="5"{{!}} <span style="color: red;">The modifier ''“migration cooldown”'' was replaced by ''“migration cost”'' with patch 1.31.</span>[[Category:Bonus table outdated]]

| #default = {{!}}-
{{!}}colspan="5"{{!}}<span style="color: red;">(invalid bonus type “{{lc:{{{1}}}}}” for [[Template:Bonus table]])</span>
}}
{{!}}}</includeonly><noinclude>[[Category:Templates]]{{template doc}}</noinclude>'''

    def __init__(self):
        self.eu4parser = Eu4Parser()
        self.parser = self.eu4parser.parser

    def run(self):
        lines = [self.header]
        processed_modifier_names = set()
        for modifier in sorted(all_modifiers, key=lambda m: m.icons[0]):
            lines.append('| {} ='.format("\n| ".join(modifier.icons)))
            if modifier.name not in self.eu4parser.ideas_and_policies_by_modifier:
                lines.append('{{!}}-')
                lines.append('{{!}}colspan="5"{{!}} <span style="color: red;">In patch ' + eu4_major_version() +
                             ' no ideas and policies have the modifier \'\'“' + modifier.icons[0] +
                             '”\'\'</span>[[Category:Bonus table outdated]]')
                continue
            all_values_for_modifier = self.eu4parser.ideas_and_policies_by_modifier[modifier.name].keys()
            for value in sorted(self.eu4parser.ideas_and_policies_by_modifier[modifier.name].keys(), key=lambda x: x if isinstance(x, str) else abs(x)*(-1) ):
                ideas = self.eu4parser.ideas_and_policies_by_modifier[modifier.name][value]
                template_params = {'t': [], 'i': [], 'b': [], 'p': []}
                for idea in self.sort_ideas(ideas):
                    if isinstance(idea, Policy):
                        template_params['p'].append(idea.formatted_name())
                    else:
                        if idea.idea_group.is_basic_idea():
                            formatted_name = '{{grey-bd|' + idea.formatted_name() + '}}'
                        else:
                            formatted_name = idea.formatted_name()
                        if idea.is_bonus():
                            if idea.idea_group.is_basic_idea():
                                if not idea.formatted_name().startswith('Full'):
                                    print('"{}"({})  is the bonus of an idea group with an unclear name'.format(idea.formatted_name(), idea.name))
                            else:
                                if 'ambition' not in formatted_name.lower():
                                    print('"{}"({})  is an ambition with an unclear name'.format(formatted_name, idea.name))
                            template_params['b'].append(formatted_name)
                        elif idea.is_tradition():
                            if 'tradition' not in formatted_name.lower():
                                print('"{}"({}) is a tradition with an unclear name'.format(formatted_name, idea.name))
                            template_params['t'].append(formatted_name)
                        else:
                            template_params['i'].append(formatted_name)

                lines.append('{{BTRow|' + modifier.format_value(value, all_values_for_modifier))
                for param, ideas in template_params.items():
                    if len(ideas) > 0:
                        lines.append("\t|{}= *{}".format(param, "\n*".join(ideas)))
                lines.append('}}')
            processed_modifier_names.add(modifier.name)
        unprocessed_modifier_names = set(self.eu4parser.ideas_and_policies_by_modifier.keys()) - processed_modifier_names
        if unprocessed_modifier_names:
            print('Some idea and policy modifiers are missing from all_modifiers:', file=sys.stderr)
            for modifier in unprocessed_modifier_names:
                print('{}: {}'.format(modifier, [
                    idea.formatted_name() for idea_list in self.eu4parser.ideas_and_policies_by_modifier[modifier].values()
                    for idea in idea_list
                    ]), file=sys.stderr)
        lines.append(self.footer)
        self.writeFile('bonus_tables', "\n".join(lines))

    def sort_ideas_key_function(self, idea):
        key = idea.formatted_name()
        if isinstance(idea, Idea) and idea.idea_group.is_basic_idea():
            key = '0' + key # make sure basic ideas get sorted first
        return key

    def sort_ideas(self, ideas):
        return sorted(ideas, key = self.sort_ideas_key_function)

    def writeFile(self, name, content):
        output_file = eu4outpath / '{}.txt'.format(name)
        with output_file.open('w') as f:
            f.write(content)

if __name__ == '__main__':
    generator = BonusTableGenerator()
    generator.run()



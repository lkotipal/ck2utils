from tempfile import TemporaryDirectory, mkstemp
import os
import subprocess
import re

from common.wiki import WikiTextFormatter
from eu4.paths import eu4_major_version


def get_SVersion_header(scope=None):
    """generate a SVersion wiki template for the current version

    for example {{SVersion|1.33}}

    @param scope a string which is used as the second parameter to the template
    @see https://eu4.paradoxwikis.com/Template:SVersion
    """
    version_header = '{{SVersion|' + eu4_major_version()
    if scope:
        version_header += '|' + scope
    version_header += '}}'
    return version_header

def get_version_header():
    """generate a Version wiki template for the current version

    for example {{Version|1.33}}
    """
    return '{{Version|' + eu4_major_version() + '}}'

class WikiTextConverter:
    """Uses pdxparse to convert game code to wikitext.

    pdxparse has to be in the path so that it can be called by this class.
    """

    def to_wikitext(self, country_scope=None, province_scope=None, modifiers=None, strip_icon_sizes=False):
        """calls pdxparse to convert the values of the parameter dicts from strings in pdxscript to wikitext. the dicts are modified in place

            most of the slowness of this function is the overhead from calling pdxparse
            and letting it parse the normal game files, so it is best to only call it once
            with everything which needs to be converted

            if strip_icon_sizes is True, the 28px which pdxparse adds to an icon template is removed
        """
        with TemporaryDirectory() as tmpfolder:
            inputfolder = tmpfolder + '/in'
            os.mkdir(inputfolder)
            outputfolder = tmpfolder + '/output/Anbennar'
            self._replace_values_by_filenames(inputfolder, country_scope)
            self._replace_values_by_filenames(inputfolder, province_scope)
            self._replace_values_by_filenames(inputfolder, modifiers)
            pdxparse_arguments = ['pdxparse', '--nowait', '-e']
            if country_scope:
                for file in country_scope.values():
                    if len(file) > 0:
                        pdxparse_arguments.append('--countryscope')
                        pdxparse_arguments.append(file)
            if province_scope:
                for file in province_scope.values():
                    if len(file) > 0:
                        pdxparse_arguments.append('--provincescope')
                        pdxparse_arguments.append(file)
            if modifiers:
                for file in modifiers.values():
                    if len(file) > 0:
                        pdxparse_arguments.append('--modifiers')
                        pdxparse_arguments.append(file)

            subprocess.run(pdxparse_arguments, check=True, cwd=tmpfolder)

            self._replace_filenames_with_values(outputfolder, country_scope)
            self._replace_filenames_with_values(outputfolder, province_scope)
            self._replace_filenames_with_values(outputfolder, modifiers)

            # self._strip_whitespace(country_scope)
            # self._strip_whitespace(province_scope)
            # self._strip_whitespace(modifiers)

            if strip_icon_sizes:
                self._strip_icon_sizes(country_scope)
                self._strip_icon_sizes(province_scope)
                self._strip_icon_sizes(modifiers)

    def add_indent(self, wikilist):
        return re.sub(r'^\*', '**', wikilist, flags=re.MULTILINE)

    @staticmethod
    def remove_indent(wikilist):
        if wikilist[0] == '*':
            return re.sub(r'^\*[\s]*', '', wikilist, flags=re.MULTILINE)
        return wikilist

    @staticmethod
    def calculate_indentation(wikiline):
        """count the number of * at the start of the string"""
        return len(wikiline) - len(wikiline.lstrip('*'))

    @staticmethod
    def remove_superfluous_indents(wikilist):
        lines = wikilist.splitlines()
        for i in range(len(lines)):
            if not lines[i].startswith('*'):
                # if there is one line which is not indented, we would break
                # the relative indentation if we remove one level
                return wikilist
            if i < (len(lines) - 1):
                if WikiTextConverter.calculate_indentation(lines[i]) == 1 \
                        and WikiTextConverter.calculate_indentation(lines[i+1]) == 1:
                    # mediawiki would merge these two lines if we remove the * from them
                    return wikilist
        # no problematic cases found, so we remove one level and call this function again to possibly remove more
        return_value = WikiTextConverter.remove_indent(wikilist)
        return WikiTextConverter.remove_superfluous_indents(return_value)

    def _create_temp_file(self, folder, contents):
        fp, filename = mkstemp(suffix='.txt', dir=folder)
        with os.fdopen(fp, mode='w') as file:
            file.write(contents)
        return filename

    def _readfile(self, filename):
        with open(filename) as file:
            return file.read()

    @staticmethod
    def remove_surrounding_brackets(string):
        """ remove {} from around a string

            this is needed, because ck2utils has no way of getting the inner code of a section
         """
        match = re.match(r'^[\s]*{(.*)}[\s]*$', string, re.DOTALL)
        if match:
            return match.group(1)
        else:
            return string

    def _replace_values_by_filenames(self, folder, dictionary):
        if dictionary:
            for key in dictionary:
                value = self.remove_surrounding_brackets(dictionary[key])
                if len(value) > 0:
                    dictionary[key] = self._create_temp_file(folder, value)
                else:
                    dictionary[key] = ''

    def _replace_filenames_with_values(self, folder, dictionary):
        if dictionary:
            for key in dictionary:
                if len(dictionary[key]) > 0:
                    dictionary[key] = self._readfile(folder + dictionary[key] + '/' + os.path.basename(dictionary[key]))

    def _strip_icon_sizes(self, dictionary):
        if dictionary:
            for key in dictionary:
                dictionary[key] = dictionary[key].replace('|28px}}', '}}')

    def _strip_whitespace(self, dictionary):
        strip_re = re.compile(r'\s+$', re.MULTILINE)
        if dictionary:
            for key in dictionary:
                dictionary[key] = strip_re.sub('', dictionary[key])


class Eu4WikiTextFormatter(WikiTextFormatter):

    @staticmethod
    def iconify(item: str, value: str = None) -> str:
        """add an icon in front of the item. This assumes that the item is also the icon key"""
        if value is None:
            return '{{icon|' + item.lower() + '}} ' + item
        else:
            return '{{icon|' + item.lower() + '}} ' + value + ' ' + item

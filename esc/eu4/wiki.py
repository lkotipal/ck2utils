from tempfile import TemporaryDirectory, mkstemp
import os
import subprocess
import re


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
            outputfolder = tmpfolder + '/output/Europa Universalis IV'
            self._replace_values_by_filenames(inputfolder, country_scope)
            self._replace_values_by_filenames(inputfolder, province_scope)
            self._replace_values_by_filenames(inputfolder, modifiers)
            pdxparse_arguments = ['pdxparse', '--nowait', '-e']
            if country_scope:
                for file in country_scope.values():
                    pdxparse_arguments.append('--countryscope')
                    pdxparse_arguments.append(file)
            if province_scope:
                for file in province_scope.values():
                    pdxparse_arguments.append('--provincescope')
                    pdxparse_arguments.append(file)
            if modifiers:
                for file in modifiers.values():
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

    def remove_surrounding_brackets(self, string):
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
                dictionary[key] = self._create_temp_file(folder, value)

    def _replace_filenames_with_values(self, folder, dictionary):
        if dictionary:
            for key in dictionary:
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

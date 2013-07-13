#!/usr/bin/env python

import os
import re
import subprocess
import distutils


class PandocRSTConverter(object):

    replacements = (
        # Remove lists with internal links (effectively, the TOC in a README).
        # We remove the TOC because the anchors in a github markdown file
        # are broken when the rst is displayed on pypi
        (re.compile(ur'(?ms)^\-  ((?:.(?!\n[\n\-]))*?\`__\n)'), u''),
        # (shorten link terminator from two underscores to one): `__ => `_
        (re.compile(ur'\`__'), u'`_'),
        # Replace, for example:
        #
        #     code sample:
        #
        #     ::
        #
        #         def example(): pass
        #
        # with:
        #
        #    code sample::
        #
        #        def example(): pass
        (re.compile(ur'(?ms)(\:)\n\n\:(\:\n\n)'), ur'\1\2'),
        # replace 3+ line breaks with 2
        (re.compile(ur'\n\n\n+'), u'\n\n'),
        # Remove syntax highlighting hints, which don't work on pypi
        (re.compile(ur'(?m)\.\. code\:\: .*$'), u'::'),
    )

    from_format = 'markdown'

    def convert(self, path_):
        path = path_ if path_[0] == '/' else os.path.join(
            os.path.dirname(__file__), '..', '..', path_)

        if not os.path.exists(path):
            raise distutils.errors.DistutilsSetupError("File '%s' does not exist" % path_)

        pandoc_path = distutils.spawn.find_executable("pandoc")
        if pandoc_path is None:
            raise distutils.errors.DistutilsSetupError(
                "pandoc must be installed and in PATH to convert markdown to rst")

        rst = subprocess.check_output([
            pandoc_path,
            "-f", self.from_format,
            "-t", "rst",
            path])
        rst = self.replace_header_chars(rst)
        for regex, replacement in self.replacements:
            rst = regex.sub(replacement, rst)
        return rst

    header_char_map = (
        ('=', '#'),
        ('-', '='),
        ('^', '-'),
        ("'", '.'),
    )

    def replace_header_chars(self, rst_string):
        """Replace the default header chars with more sensible ones"""
        for from_char, to_char in self.header_char_map:
            def replace(matchobj):
                return to_char * len(matchobj.group(0))
            regex = r'(?m)^%(from)s%(from)s+$' % {'from': re.escape(from_char), }
            rst_string = re.sub(regex, replace, rst_string)
        return rst_string

    def replace_section(self, rst, section_name, replacement):
        if replacement[-1] != u"\n":
            replacement = u"%s\n" % replacement
        replacement = u"\\1\n%s\n" % replacement    
        regex = (ur"""(?msx)
        (\n
            %(section_name)s\n
            ([%(header_chars)s])\2[^\n]+\n
        ).*?\n
        (?=(?:
            ^[^\n]+\n
            \2\2\2
          |
            \Z
        ))
        """) % {
            'section_name': re.escape(section_name),
            'header_chars': re.escape('-#=.'),
        }
        return re.sub(regex, replacement, rst)

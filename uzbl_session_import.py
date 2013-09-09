#!/usr/bin/python

#   uzbl_session_import.py, the most awesomest firefox-to-uzbl session
#   conversion utility ever.
#
#   This file is part of sessionstore-fiddle.
#
#   Copyright (C) 2013 Igor Almeida <igor.contato@gmail.com>
#
#   sessionstore-fiddle is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   sessionstore-fiddle is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with sessionstore-fiddle.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import tempfile, os

import sessionstore
import sessionconvert

def make_uzbl_session(tabs_list):
	""" Convert the list of tab dicts into a list of newline-terminated strings.
	
	Structure:
	[
		'taburl1 tabtitle1\n',
		'taburl2 tabtitle2\n',
		...
	]

	The return value can then be used with file.writelines().
	"""

	strs = [u'curtab = 0\n',]
	for tab in tabs_list:
		strs.append(u'{} {}\n'.format(tab['url'], tab['title']))
	return strs

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		formatter_class=argparse.ArgumentDefaultsHelpFormatter,
		description='Firefox to uzbl session convert utility.',
		epilog='This program extracts the tab groups from the' +
		' Firefox session store and converts them to uzbl session format,' +
		' one group per file.\nFile names are sanitized with \'_\' when' +
		' created.')
	parser.add_argument('input_file',
		help='path to Firefox\'s sessionstore.js file')

	args = parser.parse_args()
	session_file = args.input_file

	session_json = sessionstore.get_json(session_file)
	tabs_dict = sessionconvert.make_tabs_dict(session_json)

	groups = sessionstore.get_groups(session_json)
	print 'Found {} groups in {}'.format(
		len(groups), session_file)

	output_dir = tempfile.mkdtemp(prefix='uzbl_converted')
	print 'Created temp directory {}'.format(output_dir)

	count = 0
	for (group_id, session_title) in groups:
		session_string = make_uzbl_session(tabs_dict[group_id])
		#this avoids UnicodeEncodeError
		output_str = [unicode(i).encode('utf-8') for i in session_string]

		pretty_title = session_title.replace(
			' ','_').replace(
			'/','_').replace(
			'\\','_')
		if pretty_title == '':
			pretty_title = 'anon_{}'.format(group_id)
		outfile = '{}{}{}'.format(output_dir, os.sep, pretty_title)

		f = open(outfile, 'w')
		f.writelines(output_str)
		f.close()

		count += 1

	print '... done creating {} files! They were written in {}'.format(
		count, output_dir)


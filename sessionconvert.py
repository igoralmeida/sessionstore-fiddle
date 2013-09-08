#!/usr/bin/python

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

import json

import sessionstore

def make_tabs_dict(session_json):
	""" Create a dict-of-lists from the session JSON.

	Structure:
	{
	group_id: [
		{
		'url': 'URL 1',
		'title': 'Title 1'
		},
		{
		'url': 'URL 2',
		'title': 'Title 2'
		},
		{...}],
	another_group_id: [ list of tab dicts ],
	...
	}

	group_id and another_group_id are ints
	"""

	tabs_dict = {}
	main_window = sessionstore.get_window(session_json)
	tab_list = main_window['tabs']
	for tab in tab_list:
		group_id_json_str = tab['extData']['tabview-tab']
		group_id = json.loads(group_id_json_str)['groupID']

		if len(tab['entries']) == 0:
			tab_url = 'about:blank'
			tab_title = '(untitled)'
		else:
			tab_url = tab['entries'][0]['url']
			try:
				tab_title = tab['entries'][0]['title']
			except KeyError:
				tab_title = '(untitled)'

		if not group_id in tabs_dict:
			tabs_dict[group_id] = []

		tabs_dict[group_id].append({'url':tab_url, 'title':tab_title})

	return tabs_dict


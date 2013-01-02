#!/usr/bin/python

#To do:
#  Automatic sorting of the groups
#  Interactive group ordering

import json

def get_json(filepath):
	""" Load the session JSON present in the file. """

	f = open(filepath)
	js = json.load(f)
	f.close()
	return js

def get_window(session_json, which=0):
	""" Get some window in the session JSON. """

	return session_json['windows'][which]

def get_tabview_group(session_json, which_window=0):
	""" From the session JSON, load the string-encoded JSON tab group data,
	which holds location, title and id information for each tab group.
	"""
	window = get_window(session_json, which_window)

	groupinfo_str = window['extData']['tabview-group']
	groupinfo_json = json.loads(groupinfo_str)

	return groupinfo_json

def get_tabview_ui(session_json, which_window=0):
	""" From the session JSON, load the string-encoded JSON 'Tab Groups' UI
	data, which holds location information for 'Tab Groups' UI.
	"""
	window = get_window(session_json, which_window)

	ui_info_str = window['extData']['tabview-ui']
	ui_info_json = json.loads(ui_info_str)

	return ui_info_json

def get_groups(session_json, which_window=0):
	""" From the session JSON, return a list of 3-tuples
		(id_str, id_int, name_str)
	for each tab group.

	Example output:
	[(u'24', 24, u'uzbl'),
	(u'10', 10, u'py/cpp reference'),
	(u'12', 12, u'urxvt')]
	"""

	groupinfo_json = get_tabview_group(session_json, which_window)

	groups = [(id_key, info['id'], info['title'])
		for (id_key,info) in groupinfo_json.iteritems()]
	return groups

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
	main_window = get_window(session_json)
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

def tidy_groups(session_json, which_window=0, min_width=160, min_height=140,
	vertical_space=15, horizontal_space=15):
	""" In the session JSON, change the 'tabview-group' field in-place.
	See get_tabview_group().
	"""

	groupinfo_json = get_tabview_group(session_json, which_window)
	ui_info_json = get_tabview_ui(session_json, which_window)

	ui_width = ui_info_json['pageBounds']['width']
	ui_height = ui_info_json['pageBounds']['height']

	num_groups = len(groupinfo_json)
	max_groups_in_line = (ui_width /
		(horizontal_space + min_width))
	
	needed_rows = num_groups/max_groups_in_line + 1
	needed_height = (vertical_space + min_height) * needed_rows

	if needed_height > ui_height:
		error_str = ('Cannot fit {} groups (width {}, height {}, ' +
			'vspace {}, hspace {}) in the UI (width {}, height {}).')
		error_str = error_str.format(num_groups,
			min_width, min_height,
			vertical_space, horizontal_space,
			ui_width, ui_height)

		raise ValueError(error_str)

	group_count = 0
	for (id_key, info) in groupinfo_json.iteritems():
		new_top = ((vertical_space + min_height) *
			(group_count/max_groups_in_line) + vertical_space)

		new_left = ((horizontal_space + min_width) *
			(group_count % max_groups_in_line) + horizontal_space)

		new_height, new_width = min_height, min_width

		info['bounds'] = {
			'top': new_top,
			'left': new_left,
			'height': new_height,
			'width': new_width,
		}
		group_count += 1

	# the data in 'tabview-group' must be a string
	session_json['windows'][which_window]['extData']['tabview-group'] = json.dumps(
		groupinfo_json)

if __name__ == '__main__':

	session_file = 'sessionstore.js'

	session_json = get_json(session_file)
	groups = get_groups(session_json)
	if 0:
		for i in groups: print i

	if 1:
		tidy_groups(session_json)
		print json.dumps(session_json)


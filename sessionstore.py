#!/usr/bin/python

#Ideas:
#  Interactive group ordering with vim?

import json
import argparse
import os
import sys

#TODO list the actions alongside their entry functions so that the main code
#becomes a simple dispatcher
info_actions = [
	'list-groups',
]
change_actions = [
	'prettify-grid',
]
actions = info_actions + change_actions

_def_min_width = 140
_def_min_height = 110
_def_vert_space = 15
_def_horiz_space = 15

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

def set_tabview_group(session_json, which_window, tabviewgroup_json):
	""" Set the data in the 'tabview-group' item, see get_tabview_group() """

	session_json['windows'][which_window]['extData']['tabview-group'] = json.dumps(
		tabviewgroup_json)

def get_tabview_ui(session_json, which_window=0):
	""" From the session JSON, load the string-encoded JSON 'Tab Groups' UI
	data, which holds location information for 'Tab Groups' UI.
	"""
	window = get_window(session_json, which_window)

	ui_info_str = window['extData']['tabview-ui']
	ui_info_json = json.loads(ui_info_str)

	return ui_info_json

def get_groups(session_json, which_window=0):
	""" From the session JSON, return a list of tuples
		(id_int, name_str)
	for each tab group.

	Example output:
	[(24, u'uzbl'),
	(10, u'py/cpp reference'),
	(12, u'urxvt')]
	"""

	groupinfo_json = get_tabview_group(session_json, which_window)

	groups = [(info['id'], info['title'])
		for (_,info) in groupinfo_json.iteritems()]
	return groups

def tidy_groups(
	session_json,
	which_window=0,
	min_width=_def_min_width,
	min_height=_def_min_height,
	vertical_space=_def_vert_space,
	horizontal_space=_def_horiz_space):

	""" In the session JSON, change the 'tabview-group' field in-place.
	See get_tabview_group().

	Returns the number of groups that have changed
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

	if args.sort_by_name:
		sortfn = lambda (k1,one),(k2,two) : cmp(one['title'],two['title'])
	else: #args.sort_by_id
		sortfn = lambda (k1,one),(k2,two) : cmp(one['id'],two['id'])
	s = sorted(groupinfo_json.iteritems(), cmp=sortfn)

	group_count = 0
	for (id_key, info) in s:
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

	set_tabview_group(session_json, which_window, groupinfo_json)

	return group_count

def print_groups(session_json, args):
	groups = get_groups(session_json)

	if args.sort_by_name:
		sortfn = lambda (k1,a),(k2,b) : cmp(a,b)
	else: #args.sort_by_id
		sortfn = lambda (k1,a),(k2,b) : cmp(k1,k2)

	groups.sort(cmp=sortfn)

	print 'Found {} groups:'.format(len(groups))
	for (id,name) in groups:
		print id,'\t',name

def prettify_grid(j, args):
	w, h, vs, hs = (args.min_width, args.min_height,
		args.vert_space, args.horiz_space)

	in_file, out_file = args.input_file, args.output_file

	#TODO sanitize values

	num_existing_groups = len(get_groups(j))

	num_changed_groups = tidy_groups(j,
		which_window=0,
		min_width=w,
		min_height=h,
		vertical_space=vs,
		horizontal_space=hs)

	if num_existing_groups != num_changed_groups:
		print ('ERROR: There were {} groups before and {} groups ' +
			'after the tidying operation, aborting.\n').format(
			num_existing_groups, num_changed_groups)
		sys.exit(-1)

	f = open(out_file, 'w')
	f.write(json.dumps(j))
	f.close()

	print ('Successfully wrote {} tab groups to file {} with the ' +
		'following sizes:\n' +
		'Group width {} px\n' +
		'Group height {} px\n' +
		'Vertical spacing {} px\n' +
		'Horizontal spacing {} px\n').format(
			num_changed_groups, out_file,
			w, h, vs, hs)

if __name__ == '__main__':

	parser = argparse.ArgumentParser(
		formatter_class=argparse.ArgumentDefaultsHelpFormatter,
		description='Firefox session store ' +
			'handling utility.',
		epilog='This program works by modifying a copy of the input ' +
		'file. Currently, you must manually substitute the original ' +
		'session file with the one this program creates.')
	parser.add_argument('action', choices=actions,
		help='what to do with the Firefox session file')
	parser.add_argument('input_file',
		help='path to the original sessionstore.js file')
	parser.add_argument('-o', '--output_file',
		help='path to the modified sessionstore.js file ' +
		'(will not accept the same path as input-file)')
	parser.add_argument('--window', default=0,
		help='index of the window')

	parser.add_argument('--min_width', type=int, default=_def_min_width,
		help='width (pixels) of each tab group')
	parser.add_argument('--min_height', type=int, default=_def_min_height,
		help='height (pixels) of each tab group')
	parser.add_argument('--vert_space', type=int, default=_def_vert_space,
		help='vertical spacing (pixels) between tab groups')
	parser.add_argument('--horiz_space', type=int, default=_def_horiz_space,
		help='horizontal spacing (pixels) between tab groups')
	parser.add_argument('--sort_by_name', action='store_true',
		help='sort groups by name')
	parser.add_argument('--sort_by_id', action='store_true',
		help='sort groups by id')

	args = parser.parse_args()
	in_file = args.input_file
	out_file = args.output_file

	if not os.path.exists(in_file):
		e = "Error: Session file '{}' does not exist.".format(in_file)
		sys.exit(e)

	if (args.action in change_actions and (
		os.path.exists(out_file) or out_file == in_file)):
		e = ("Error: The output file cannot already exist " +
			"or be the same as the input file.")
		sys.exit(e)

	j = get_json(in_file)

	if args.action == 'list-groups':
		print_groups(j, args)

	elif args.action == 'prettify-grid':
		prettify_grid(j, args)


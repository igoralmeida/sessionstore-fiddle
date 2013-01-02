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

	strs = ['curtab = 0\n',]
	for tab in tabs_list:
		strs.append('{} {}\n'.format(tab['url'], tab['title']))
	return strs

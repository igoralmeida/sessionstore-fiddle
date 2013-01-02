#!/usr/bin/python

import sessionstore
import uzbl_session

if __name__ == '__main__':
	session_file = 'sessionstore.js'

	session_json = sessionstore.get_json(session_file)
	tabs_dict = sessionstore.make_tabs_dict(session_json)

	groups = sessionstore.get_groups(session_json)

	for (_, group_id, session_title) in groups:
		session_string = uzbl_session.make_uzbl_session(tabs_dict[group_id])

		pretty_title = session_title.replace(' ','_')
		outfile = '/tmp/{}'.format(pretty_title)

		f = open(outfile, 'w')
		f.writelines(session_string)
		f.close()

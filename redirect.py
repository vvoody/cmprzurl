#!/usr/bin/env python

# by vvoody <wxj{AT}vvoody.org>
# Licensed under GPLv3

import cgi, os, sys
import cgitb; cgitb.enable()

def check_alias( alias ):
    """
    Only redirect.py?alias=d8FjhA is valid.
    """
    for c in alias:
        if not c.isalnum():
            return False
    if alias != alias.strip():
        return False
    return True

form = cgi.FieldStorage()

if form.has_key('alias') and check_alias( form['alias'].value ):
    # fetch the longurl from db
    from pysqlite2 import dbapi2 as sqlite3
    con = sqlite3.connect('cmprzurl.db')
    con.isolation_level = None
    cur = con.cursor()
    #
    alias = form['alias'].value
    longurl = ""
    try:
        cur.execute("select longurl from mapurl where key='%s'" % alias)
    except:
        print "Content-Type: text/html\n"
        print "Oooooops... Something failed :("
	sys.exit(1)
    record = cur.fetchone()
    cur.close()
    con.close()
    if record != None: # redirect the alias to longurl
	longurl = record[0]
	print "Status: 301 Moved Permanently"
	print "Location: %s" % longurl
	print
    else:  # No alias for longurls
	print "Content-Type: text/html\n"
        print "We have no alias (%s) for the longurls" % alias
    # end if
else:
    print "Content-Type: text/html\n"
    print "Oooooops... Check you url! We have no idea about it :("
# end script

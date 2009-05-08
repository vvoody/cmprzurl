#!/usr/bin/env python

import cgi
import os
import cgitb; cgitb.enable() # for cgi debug, remove it later
from urlparse import urlparse

def check_url(aurl):
    """
    Check whether the url is valid or not.
    Although a valid URL is like: scheme://netloc/path;parameters?query#fragment
    but here we make it simple.
    """
    #
    if aurl == '':
	return False
    if urlparse(aurl)[0] == '': # scheme
	aurl = "http://" + aurl
    return True

query = os.environ['QUERY_STRING']
form = cgi.FieldStorage()
# get the longurl form query
longurl = query[(query.find('=')+1):] # remove 'longurl='
longurl = longurl.strip()

if form.has_key('longurl') and check_url(longurl):
    print "Content-Type: text/html\n"
    #
    # generate unique string for mapping longurl &
    # connect the db and write into it
    import random
    from pysqlite2 import dbapi2 as sqlite3
    #
    con = sqlite3.connect('cmprzurl.db')
    con.isolation_level = None
    cur = con.cursor()
    # ...
    randseed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    goon = True
    while goon:
        # generate a random string for mapping the longurl
        shorturl = ""
        for i in range(6):
            shorturl += random.choice(randseed)
        #
        # try write 'shorturl' and 'longurl' into db:
        # ...
        # except: used map string or same url
        #     del shorturl
        #     continue
	print shorturl
	try:
	    inskey = """insert into mapurl values('%s', NULL);""" % shorturl
	    cur.execute(inskey)
	except:
	    del shorturl
	    continue
	try:
	    inslongurl = """update mapurl set longurl='%s' where key='%s';""" % (longurl, shorturl)
	    cur.execute(inslongurl)
	except: # longurl is not unique, means that it had been shorted ;-)
	    # print """select key from mapurl where longurl=form['longurl'].value"""
	    print "This url had been shorted ;-)"
	    break
        goon = False
    #
    cur.close()
    con.close()
    # no except, genrate htmls. end here
    print ": ", longurl
else:
    print "Content-Type: text/html\n"
    print "Ooooops... Check you url!"

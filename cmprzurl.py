#!/usr/bin/env python

import cgi
import cgitb; cgitb.enable() # for cgi debug, remove it later
from urlparse import urlparse

def check_url(aurl):
    """
    Check whether the url is valid or not.
    Although a valid URL is like: scheme://netloc/path;parameters?query#fragment
    but here we make it simple.
    """
    #
    aurl = aurl.strip()
    if aurl == '':
	return False
    if urlparse(aurl).scheme == '':
	aurl = "http://" + aurl
    return True

form = cgi.FieldStorage()

if form.has_key('longurl') and check_url( form['longurl'].value ):
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
        shorterurl = ""
        for i in range(6):
            shorterurl += random.choice(randseed)
        #
        # try write 'shorterurl' and 'longurl' into db:
        # ...
        # except: used map string or same url
        #     del shorterurl
        #     continue
	print shorterurl
	try:
	    inskey = """insert into mapurl values('%s', NULL);""" % shorterurl
	    cur.execute(inskey)
	except:
	    del shorterurl
	    continue
	try:
	    inslongurl = """update mapurl set longurl='%s' where key='%s';""" % (form['longurl'].value, shorterurl)
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
else:
    print "Content-Type: text/html\n"
    print "Ooooops... Check you url!"

#!/usr/bin/env python

import cgi
import os, sys
import cgitb; cgitb.enable() # for cgi debug, remove it later
from urlparse import urlparse

def check_url(aurl):
    """
    Check whether the url is valid or not.
    Although a valid URL is like: scheme://netloc/path;parameters?query#fragment
    but here we make it simple.
    """
    #
    global longurl
    if aurl == '':
	return False
    if aurl[:8] != 'longurl=':
        return False
    aurl, longurl = aurl[8:], longurl[8:]
    if urlparse(aurl)[0] == '':    # scheme
        longurl = "http://" + aurl # 'g.cn' -> 'http://g.cn'
    return True

query = os.environ['QUERY_STRING']
form = cgi.FieldStorage()
#longurl = query[(query.find('=')+1):] # remove 'longurl='
longurl = query[::]
longurl = longurl.strip()

if form.has_key('longurl') and check_url(longurl):
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
        #
        # First, find whether the longurl has been mapped, then generate an alias
        #
        alias = ""
        for i in range(6):
            alias += random.choice(randseed)
        #
        # try write 'alias' and 'longurl' into db:
        #
	try: # alias is primary key
	    cur.execute("""insert into mapurl values('%s', NULL);""" % alias)
	except:
	    del alias
	    continue
	try: # longurl is unique
	    cur.execute("""update mapurl set longurl='%s' where key='%s';""" % (longurl, alias))
	except: # The 'longurl' had been shorted ;-)
	    break
        goon = False
    #
    # end while
    if goon == True: # fetch the alias of the already mapped longurl
        try:
            cur.execute("select key from mapurl where longurl='%s'" % longurl)
            alias = cur.fetchone()[0]
        except:
            print "Content-Type: text/html\n"
            print "Ooooooooops. Something failed :("
            sys.exit(1)
    #
    # close the db operation
    #
    cur.close()
    con.close()
    #
    # generate htmls
    #
    print "Content-Type: text/html\n"
    print """<html><body>
    <b>Now, visit your url via following link instead of the long one ;-)</b><br>
    <a href="http://%s/%s">http://%s/%s</a>
    </body></html>""" % ('vvoody.org', alias, 'vvoody.org', alias) 
    # end if
else:
    print "Content-Type: text/html\n"
    print "Ooooops... Check you url!"
# end script

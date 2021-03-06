#!/usr/bin/env python

# by vvoody <wxj{AT}vvoody.org>
# Licensed under GPLv3

import cgi
import os, sys
import cgitb; cgitb.enable() # for cgi debug, remove it later
from urlparse import urlparse

def check_url(aurl):
    """
    Check whether the url is valid or not.
    
    Although a valid URL is like: scheme://netloc/path;parameters?query#fragment
    but here we make it simple.
    http://yourdomain/j8ZhyA is invalid. Do not fool me :D
    """
    #
    global longurl, MYDOMAIN
    if aurl == '':
        return False
    if aurl[:8] != 'longurl=':
        return False
    aurl, longurl = aurl[8:], longurl[8:]
    # in Python 2.3 urlparse() returns tuple not class :(
    if urlparse(aurl)[0] == '':          # scheme
        longurl = "http://" + aurl       # 'g.cn' -> 'http://g.cn'
    urlelems = urlparse(longurl)
    if urlelems[1] == MYDOMAIN:          # /blog/?p=123 is ok, but /ak8DmN or /ak8DmN/ or /blog
        if longurl[:-1].count('/') == 3: # scheme://mydomain.com/blabla[/] is invalid
            return False
    return True

# By default, the compressed url is like http://vvoody.org/jUc2nA
ALIAS_SIZE = 6
MYDOMAIN = "vvoody.org"
RANDSEED = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
SQLITE3DB = "cmprzurl.db"

# Get whole query, cgi.FieldStorage() is not enough :(
query = os.environ['QUERY_STRING']
form = cgi.FieldStorage()
longurl = query[::]
longurl = longurl.strip()
# longurl is like: longurl=http://foo.com/bar?id=1234&longurl=fiajjfaejfja

if form.has_key('longurl') and check_url(longurl):
    #
    # generate unique alias for mapping longurl &
    # connect the db and write into it
    import random
    from pysqlite2 import dbapi2 as sqlite3
    #
    try:
        con = sqlite3.connect(SQLITE3DB)
    except:
        print "Content-Type: text/html\n"
        print "Failed to connect db %s." % SQLITE3DB
        sys.exit(1)
    #
    con.isolation_level = None
    cur = con.cursor()
    #
    goon, aliasgo = True, True
    #
    # 1. Insert longurl into db first to see if it had been mapped:
    #
    try:
        cur.execute("insert into mapurl values(NULL, '%s');" % longurl)
    except:
        aliasgo = False # No need to generate an alias
    #
    # 2. write the 'alias' into db:
    #
    while aliasgo:
        alias = ""
        for i in range(ALIAS_SIZE):
            alias += random.choice(RANDSEED)
        try: # alias is primary key
            cur.execute("""update mapurl set key='%s' where longurl='%s';""" % (alias, longurl))
        except:
            del alias
            continue
        goon, aliasgo = False, False
    #
    # end while
    #
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
    </body></html>""" % (MYDOMAIN, alias, MYDOMAIN, alias) 
    # end if
else:
    print "Content-Type: text/html\n"
    print "Ooooops... Check you url!"
# end script

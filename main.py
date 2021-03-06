""" Implementation of a simple guestbook server.
    Replacing "safeserver" with "webapp2" would introduce an injection
    vulnerability.  However, safeserver is able to properly mark input as
    dangerous, so queries through safesql reject injection attacks.
"""

import os
import sys

import json
import urllib
import cgi
import safeserver
import safesql
import jinja2
from google.appengine.ext.webapp.util import run_wsgi_app

import urllib2
import logging

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

_INSTANCE_NAME = 'injection-free-server:injection-free-server'

class Test(safeserver.RequestHandler):
    def post(self):
        self.response.headers["Access-Control-Allow-Origin"] = "*"
        self.response.headers["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept"
        self.response.headers["Access-Control-Allow-Methods"] = "POST, GET, PUT, OPTIONS"
        self.response.headers['Content-Type'] = 'application/json'
        url = "http://api.hackerrank.com/checker/submission.json"
        logging.warning(self.request.params)
        data = urllib.urlencode(self.request.params)
        logging.error(data)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        content = response.read()
        self.response.out.write(content)

class MainHandler(safeserver.RequestHandler):
    def get(self):
        # Display existing guestbook entries and a form to add new entries.
        env = os.getenv('SERVER_SOFTWARE')
        if (env and env.startswith('Google App Engine/')):
            db = safesql.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='guestbook', user='root', charset='utf8')
        else:
            db = safesql.connect(host='173.194.253.12', port=3306, db='guestbook', user='colin', charset='utf8')
            # Alternatively, connect to a Google Cloud SQL instance using:
            # db = safesql.connect(host='ip-address-of-google-cloud-sql-instance', port=3306, user='root', charset='utf8')

        guestlist = [];
        cursor = db.cursor()
        try:
            query = 'SELECT guestName, content, entryID FROM entries'
            user = self.request.get('user')
            if user:
                query += " WHERE guestName = '" + user + "'"
            cursor.execute(query)
            for row in cursor.fetchall():
                guestlist.append(dict([('name',cgi.escape(row[0])),
                                     ('message',cgi.escape(row[1])),
                                     ('ID',row[2])
                                     ]))
        except:
            pass

        # Create a list of guestbook entries to render with the HTML.

        variables = {'guestlist': guestlist}
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(variables))
        db.close()

class Guestbook(safeserver.RequestHandler):
    def post(self):
        # Handle the post to create a new guestbook entry.
        fname = self.request.get('fname')
        content = self.request.get('content')

        env = os.getenv('SERVER_SOFTWARE')
        if (env and env.startswith('Google App Engine/')):
            db = safesql.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='guestbook', user='root', charset='utf8')
        else:
            db = safesql.connect(host='173.194.253.12', port=3306, db='guestbook', user='colin', charset='utf8')
            # Alternatively, connect to a Google Cloud SQL instance using:
            # db = safesql.connect(host='ip-address-of-google-cloud-sql-instance', port=3306, db='guestbook', user='root', charset='utf8')

        cursor = db.cursor()
        # Note that the only format string supported is %s
        try:
            command = 'INSERT INTO entries (guestName, content) VALUES ("' + fname + '", "' + content + '")'
            cursor.execute(command)
        except:
            pass
        db.commit()
        db.close()

        self.redirect("/")



app = safeserver.WSGIApplication([
    ('/sign', Guestbook),
    ('/', MainHandler)
], debug=True)


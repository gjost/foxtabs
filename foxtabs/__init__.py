# -*- coding: utf-8 -*-

__author__ = 'Geoffrey Jost'
__email__ = 'geoffrey@jostwebwerks.com'
__version__ = '0.1.0'


DESCRIPTION = """Lists titles and URLs of current Firefox tabs"""

EPILOG = ""


import codecs
from ConfigParser import ConfigParser
from datetime import datetime
from htmlentitydefs import codepoint2name
import json
import os
import sys

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)


NOW = datetime.now().strftime('%c')

def profile_ini_path():
    """Path to profiles.ini in user's home dir.
    """
    return os.path.join('/home/', os.getlogin(), '.mozilla/firefox/profiles.ini')

def read_profiles(path):
    config = ConfigParser()
    configs_read = config.read(path)
    if not configs_read:
        raise NoConfigError('No config file!')
    return config

def profile_name(config):
    """Naively chooses what we hope is the default profile.
    """
    return config.get('Profile0','Path')

def sessionstore_path(profile):
    """Path to file that contains current session info.
    """
    return os.path.join('/home/', os.getlogin(), '.mozilla/firefox', profile, 'sessionstore.js')

def load_sessionstore(path):
    with open(path, 'r') as f:
        data = json.loads(f.read())
    return data

def extract_entries(data):
    """Extracts list of current URLs/titles from session data.
    """
    entries = []
    for window in data['windows']:
        for tab in window['tabs']:
            for entry in tab['entries']:
                title = unicode(entry.get('title', u'').strip())
                url = unicode(entry.get('url', u'').strip())
                entries.append({'title':title, 'url':url})
    return entries

def text(sspath, entries):
    """Output to text.
    """
    items = [
        u'Firefox tabs - ' + NOW,
        unicode(sspath),
        u'----------',
    ]
    for e in entries:
        if e.get('title', ''):
            item = u'- %s\n  %s' % (e['title'], e['url'])
        else:
            item = u'- %s' % e['url']
        items.append(item)
    return '\n'.join(items)

def unicode_to_htmlentities(text):
    """Convert unicode chars to HTML entities.
    """
    chars = []
    for t in text:
        if ord(t) < 128:
            c = t
        else:
            c = '&%s;' % codepoint2name[ord(t)]
        chars.append(c)
    return ''.join(chars)

def html(sspath, entries):
    """Output to HTML.
    """
    items = [
        u'<h1>Firefox tabs &mdash; %s</h1>' % NOW,
        u'<p>%s</p>' % sspath,
    ]
    items.append(u'<ul>')
    for e in entries:
        if e.get('title', ''):
            title = unicode_to_htmlentities(e['title'])
            item = u'<li><a href="%s">%s</a></li>' % (e['url'], title)
        else:
            item = u'<li><a href="%s">%s</a></li>' % (e['url'], e['url'])
        items.append(item)
    items.append(u'</ul>')
    return u'\n'.join(items)

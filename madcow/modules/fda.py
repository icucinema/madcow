"""Gets Film Info from the Film Distributors Association"""

from madcow.util.http import geturl, getsoup
from urlparse import urljoin
import re
from BeautifulSoup import BeautifulSoup, NavigableString
from madcow.util import Module, strip_html
from madcow.util.text import *

class Main(Module):

    """Module object loaded by madcow"""

    # module attributes
    pattern = re.compile(r'^\s*(?:(filminfo)\s+(.+?))\s*$', re.I)
    help = 'filminfo <film> - get details of film from Film Distributors Association'

    # urls
    fda_url = 'http://launchingfilms.com/'
    fda_search = urljoin(fda_url, '/release-schedule')

    # normalization regex
    year_re = re.compile(r'\(\d{4}\)\s*$')
    rev_article_re = re.compile(r'^(.*?),\s*(the|an?)\s*$', re.I)
    articles_re = re.compile(r'^\s*(the|an?)\s+', re.I)
    badchars_re = re.compile(r'[^a-z0-9 ]', re.I)
    whitespace_re = re.compile(r'\s+')
    and_re = re.compile(r'\s+and\s+', re.I)

#    def init(self):
        # Do nothing

    def response(self, nick, args, kwargs):
        if args[0] == 'filminfo':
            response = self.fdaSearch(args[1])
        else:
            raise ValueError('invalid args')
        return u'%s: %s' % (nick, response)

    def fdaSearch(self, name):
        """Get FDA Release Date and Distributor"""
        normalizedName = self.normalize(name)
        page = geturl(self.fda_search, {'filmSearch': normalizedName}, referer=self.fda_url)
        soup = BeautifulSoup(page)
        
        resultsTable = soup.table
        tbody = resultsTable.tbody

        row = tbody.tr
        outputItems = []
        currentDateString = ''

        print "searching"

        while row != None:
            if not isinstance(row, NavigableString):
                if row['class'] == 'dateRow':
                    print "DATE: "+row.td.h4.contents[0]
                    currentDateString = row.td.h4.contents[0]
                elif row['class'] == 'movieRow':
                    innerRow = row.td.table.tr

                    while innerRow != None:
                        if not isinstance(innerRow, NavigableString):
                            innerTd = innerRow.td
                            fTitle = innerTd.h5.contents[0]
                            innerTd = innerTd.nextSibling
                            while isinstance(innerTd, NavigableString):
                                innerTd = innerTd.nextSibling
                            innerTd = innerTd.nextSibling
                            while isinstance(innerTd, NavigableString):
                                innerTd = innerTd.nextSibling
                            try:
                                fDistributor = innerTd.span.contents[0]
                            except AttributeError:
                                fDistributor = "Unknown"
                            innerTd = innerTd.nextSibling
                            while isinstance(innerTd, NavigableString):
                                innerTd = innerTd.nextSibling
                            try:
                                fRelease = " ".join(innerTd.contents[0].split())
                            except AttributeError:
                                fRelease = "Unknown"
                            outputItems.append(fTitle+" :: "+currentDateString+" ("+fDistributor+") ["+fRelease+"]")
                        
                        innerRow = innerRow.nextSibling
    
            row = row.nextSibling
        
        return '\n'.join(outputItems)

    def normalize(self, name):
        """Normalize a movie title for easy comparison"""
        name = strip_html(name)
        name = self.year_re.sub('', name)              # strip trailing year
        name = self.rev_article_re.sub(r'\2 \1', name) # Movie, The = The Movie
        name = self.articles_re.sub('', name)          # strip leading the/an
        name = self.badchars_re.sub(' ', name)         # only allow alnum
        name = name.lower()                            # lowercase only
        name = name.strip()                            # strip whitespace
        name = self.whitespace_re.sub(' ', name)       # compress whitespace
        name = self.and_re.sub(' ', name)              # the word "and"
        return name

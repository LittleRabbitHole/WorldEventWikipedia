##
# Get edit activities from wiki revision records.
#
# revision request:
#  /w/api.php?action=query&prop=revisions&titles=[TITLE]
#             &rvprop=ids%7Ctags%7Cflags%7Ctimestamp%7Cuser%7Csize%7Cparsedcomment%7Ccomment
#             &rvend=[EARLIER TIME]&rvstart=[LATER TIME]&rvlimit=50&format=json&formatversion=2
#
# compare request:
#  /w/api.php?action=compare&fromrev=[REV DIFF BASE ID]&torev=[REV DIFF TARGET ID]
#             &prop=diff%7Ccomment%7Cuser%7Cparsedcomment&format=json&formatversion=2
#
# - the 'diffsize' in Wiki Compare API is the size different between 2 revision's HTML format
#   not the in actural wiki text size, which should be calculated based on the size of every
#   revision.
#
# - the 'parsedcomment' in Wiki Revision API is the raw HTML version of the comment showed in
#   the article's revision page, which has a special character contain information like "section
#   edit" (and the section title), "automatic edit summary". These information is not available
#   in Revision API to be accessed, but seems useful enough to be included. The extraction should
#   be a relatively easy job
##

import csv
import re
import pandas as pd
import datetime as dt
import requests

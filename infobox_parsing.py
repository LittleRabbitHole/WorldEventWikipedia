#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 12:58:16 2018

parsing info box to get the location
https://github.com/siznax/wptools/wiki

@author: angli
"""

import wptools
page = wptools.page('Alphen aan den Rijn shopping mall shooting')
page.get_parse()
page.data['infobox']['location']
page.data['infobox']['coordinates']

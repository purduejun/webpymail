# -*- coding: utf-8 -*-

# WebPyMail - IMAP python/django web mail client
# Copyright (C) 2008 Helder Guerreiro

## This file is part of WebPyMail.
##
## WebPyMail is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## WebPyMail is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with WebPyMail.  If not, see <http://www.gnu.org/licenses/>.

#
# Helder Guerreiro <helder@paxjulia.com>
#
# $Id: forms.py 421 2008-11-20 09:31:16Z helder $
#

"""Utility functions"""

from ConfigParser import SafeConfigParser
from django.conf import settings

def cmp_dict( key ):
    '''
    Returns a comparation function (similar to 'cmp') for dictionary lists.
    '''
    def cmpd( a, b ):
        return cmp( a[key], b[key] )
    return cmpd

def server_config():
    '''
    Returns the server(s) configuration.
    '''
    config = SafeConfigParser()

    config.read( settings.SERVERCONF )

    return config

def server_list():
    '''
    Returns a list of server configurations. This is the login server, ie, the
    server agains which the users autenticate.
    '''
    config = server_config()
    
    server_list = []
    k = 0
    for server in config.sections():
        s = {}
        s['label'] = server
        k += 1
        for option in config.options(server):
            s[option] = config.get( server, option )
        server_list.append(s) 
    server_list.sort(cmp_dict('name'))
    
    return server_list
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
# $Id: __init__.py 364 2008-06-16 11:46:37Z helder $
#

"""Reads the text configuration files.
"""

# Imports
from ConfigParser import SafeConfigParser
import os.path
import re

from django.conf import settings

from webpymail.util.mix import cmp_dict

# re:

identity_re = re.compile(r'^identity(?P<id_number>[0-9]+)$')

def user_config( server_name, user_name ):
    '''
    Read the user configuration.

    @param server_name: server the user has logged in against
    @param user_name: name used to make the login

    @return configuration object.
    '''
    config = SafeConfigParser()

    user_conf=os.path.join(USERCONFDIR, '%s@%s.conf' % (user_name, server_name))
    server_conf = os.path.join(SERVERCONFDIR, '%s.conf' % server_name )
    
    config.read( [ settings.FACTORYCONF,
                   settings.DEFAULTCONF,
                   user_conf,
                   server_conf,
                   settings.SYSTEMCONF ] )

    return config

def user_identities( config ):
    '''
    Returns a list of identities defined on the user configuration.

    @param config: configuration object

    @return a list of identities in dicionary form.
    '''
    identity_list = []
    for section in config.sections():
        identity_sec = identity_re.match(section)
        if resp:
            identity = {}
            identity['id_number'] = int(identity_sec.group('id_number'))
            for option in config.options(section):
                identity[option] = config.get( section, option )
            identity_list.append( identity )
    identity_list.sort(cmp_dict( 'id_number' ))
    
    return identity_list
    
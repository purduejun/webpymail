#!/usr/bin/env python
# -*- coding: utf-8 -*-

# hlimap - High level IMAP library
# Copyright (C) 2008 Helder Guerreiro

## This file is part of hlimap.
##
## hlimap is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## hlimap is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with hlimap.  If not, see <http://www.gnu.org/licenses/>.

#
# Helder Guerreiro <helder@paxjulia.com>
#
# $Id$
#

import os
import sys
import getopt
import getpass

from hlimap import ImapServer

## 
# Utility functions
##

def server_login(host, port, ssl, user):
    """Login to the server
    """
    # Get the password
    passwd = getpass.getpass('Password: ')
    # Login to the server:
    M = ImapServer(host, port, ssl)
    M.login(user, passwd)

    return M

##
# Main
##

def usage():
    print '''Usage: %(script_name)s [command] [options]\n
    Commands:
        --list-mailboxes
        --mark-read <mailbox>   Mark the messages read, accepts wildcards 

    Options:
        -o <imap server>
        --host <imap server>    (default: localhost) define the imap server to
                                connect to
        -u <user name>                        
        --user <user name>      (default: $USER) imap user name
        -s <type>
        --security <type>       (default: NONE) available options are: SSL,
                                NONE
        -p
        --port                  (default: 143) port to connect to, if SSL 
                                security is used the default changes to 993

        -h --help               This help screen\n
    Notes:
        The imap mailbox name wildcards are:
            * - matches zero or more characters, including the hierarchy 
                delimiter;   
            %% - is similar to "*", but it does not match a hierarchy delimiter
    ''' % { 'script_name': sys.argv[0] }

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ho:u:s:p:',
            ['list-mailboxes', 'mark-read=',
            'host=', 'user=', 'security=', 'port=', 
            'help'])
    except getopt.GetoptError, err:
        print str(err)
        print
        usage()
        sys.exit(1)

    # Defaults
    user = os.getenv('USER')
    host = os.getenv('IMAPSERVER', 'localhost')
    port = 143
    security = 'NONE'

    # Optional args
    for o, a in opts:
        if o in ('-o', '--host'):
            host = a
        elif o in ('-u', '--user'):
            user = a
        elif o in ('-p', '--port'):
            try:
                port = int(a)
            except ValueError:
                print 'The port number must be an integer'
                sys.exit(1)
        elif o in ('-s', '--security'):
            security = a.upper()
            if security not in ('TLS','SSL','NONE'):
                print 'The security type must be TLS, or SSL or None.'
                sys.exit(2)
            if security == 'SSL' and port == 143:
                port = 993

    # Mandatory args
    for o, a in opts:
        if o == '--list-mailboxes':
            ssl = security == 'SSL'            
            server = server_login(host, port, ssl, user)
            server.folder_iterator = 'iter_all'
            print
            print 'The available folders are:'
            print
            for folder in server:
                print folder.path
            sys.exit()
        elif o == '--mark-read':
            print 'Not implemented yet.'
            sys.exit()

    usage()
    sys.exit()

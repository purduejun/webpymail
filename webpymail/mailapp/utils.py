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
# $LastChangedDate: 2008-04-12 19:06:06 +0100 (Sat, 12 Apr 2008) $
# $LastChangedRevision: 308 $
# $LastChangedBy: helder $
# 

"""Utility functions
"""

# Imports:
import textwrap

# Mail
from hlimap import ImapServer

def serverLogin( request ):
    """Login to the server
    """
    # Login to the server:
    M = ImapServer(host=request.session['host'],port=request.session['port'], 
        ssl= request.session['ssl'])
    
    try:
        M.login(request.session['username'], 
            request.session['password'])
        return M
    except:
        raise Http404
        
def join_address_list( addr_list ):
    '''Returns a comma separated list of mail addresses.
    
    @param addr_list: a list of addresses on the form [ ("name","email"), ... ]
    
    @return: comma separated list of addresses on a string.
    '''
    if not addr_list:
        return ''
    addrs = []
    for addr in addr_list:
        addrs.append( mail_addr_str(addr) )
    
    return ','.join(addrs)
        
def mail_addr_str( mail_addr ):
    '''String representation of a mail address.
    
    @param mail_addr: a tuple in the form ("Name", "email address")
    
    @return: '"Name" <email address>' or only '<email address>' if there is no 
        name.
    '''
    if mail_addr[0]:
        return '"%s" <%s>' % ( mail_addr[0], mail_addr[1] )
    else:
        return '<%s>' % ( mail_addr[1] )

def mail_addr_name_str( mail_addr ):
    '''String representation of the person name in a mail address.
    
    @param mail_addr: a tuple in the form ("Name", "email address")
    
    @return: '"Name"' or '<email address>' if there is no name.
    '''
    if mail_addr[0]:
        return '%s' % ( mail_addr[0])
    else:
        return '<%s>' % ( mail_addr[1] )
        
def quote_wrap_lines(text, quote_char = '>', width = 60):
    '''Wraps and quotes a message text.split
    
    @param text: text of the message
    @param quote_char: que character to be appended on eaxh line (without extra 
        spaces)
    @param width: number of columns the text should have counting the quote_char

    @return: the quoted text.
    '''
    ln_list = text.split('\n')
    quote_char = '%s ' % quote_char
    width = width - len(quote_char)
    
    new_list = []
    for ln in ln_list:
        if len(ln) > width:
            ln = textwrap.fill( ln, width=width, initial_indent=quote_char, subsequent_indent=quote_char)
            new_list.append(ln)
        else:
            new_list.append('%s %s' % (quote_char, ln))

    return '\n'.join(new_list)
    
def show_addrs( label, addr_list, default ):
    '''Returns a text representation of the address list.
    '''
    txt = '%s: ' % label 
    if addr_list:
        for addr in addr_list:
            txt += '%s, ' % mail_addr_str(addr)
        txt = txt[:-2] + '\n'
    else:
        if default:
            txt += '%s\n' % default
        else:
            return ''
        
    return txt
    

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
# $LastChangedDate: 2008-04-18 17:08:14 +0100 (Fri, 18 Apr 2008) $
# $LastChangedRevision: 323 $
# $LastChangedBy: helder $
# 

"""Display folders and messages.
"""

# Global Imports
# Django:
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Local
from utils import serverLogin
        
@login_required
def showFoldersView(request):
    '''Show the account folders.
    '''
    # Login to the server:
    M = serverLogin( request )
    folders = M.folders
    
    return render_to_response('mail_folders.html',{'folders': folders})        
  
def calc_page_numbers( msg_num, page ):
    MESSAGES_PAGE = settings.MESSAGES_PAGE
    if msg_num == 0:
        msg_num = 1
    max_page = (msg_num // MESSAGES_PAGE)
    if msg_num % MESSAGES_PAGE:
        max_page += 1
    show = True
    if max_page == 1:
        show = False
    if page > max_page:
        page = max_page
    i = ( page - 1) * MESSAGES_PAGE
    j = page * MESSAGES_PAGE - 1
    if (j) > msg_num:
        j = msg_num
    previous = page - 1
    next = page + 1
    last = max_page
    first = 1    
    if page == 1:
        first = 0
        previous = 0
    if page == max_page:
        last = 0
        next = 0
        
    return first, previous, next, last, i, j, show

@login_required
def showMessageListView(request, folder=settings.DEFAULT_FOLDER):
    '''Show the selected Folder message list.
    '''
    M = serverLogin( request )    
    folder = M.folders[folder].select()
    
    # Set the search criteria:
    search_criteria = 'ALL'
    query = None
    
    flag = request.GET.get('flag', None)
        
    if flag:
        query = 'flag=%s' % flag
        search_criteria = 'KEYWORD %s' % flag
        
    folder.messages.change_search(search_criteria)
    
    # Set the current page
    msg_num = folder.messages.len()
    
    page = request.GET.get('page',1)
    try:
        page = int(page)
        if page < 1:
            page = 1
    except:
        page = 1
        
    # Calc the page numbers
    first, previous, next, last, i, j, show = calc_page_numbers( msg_num, page )

    message_list = folder.messages[i:j]
    
    # Show the message list
    return render_to_response('message_list.html',{'messages': message_list,
        'folder':folder, 'page': {'next':next, 'previous':previous, 
        'first': first, 'last': last, 'show':show }, 'query':query })

@login_required
def showMessage(request, folder, uid):
    '''Show the message
    '''
    
    M = serverLogin( request )
    folder = M.folders[folder].select()
    message = folder.messages[uid]

    return render_to_response('message_body.html',{'folder':folder, 
        'message':message})
        
@login_required
def message_header( request, folder, uid ):
    '''Show the message header
    '''
    
    M = serverLogin( request )
    folder = M.folders[folder].select()
    message = folder.messages[uid]
    
    return render_to_response('message_header.html',{'folder':folder, 
        'message':message})
    
@login_required
def message_structure( request, folder, uid ):
    '''Show the message header
    '''
    
    M = serverLogin( request )
    folder = M.folders[folder].select()
    message = folder.messages[uid]
    
    return render_to_response('message_structure.html',{'folder':folder, 
        'message':message})    

@login_required
def get_msg_part( request, folder, uid, part_number ):
    '''Gets a message part.
    '''
    M = serverLogin( request )
    folder = M.folders[folder].select()
    message = folder.messages[uid]
    part = message.bodystructure.find_part(part_number)

    response = HttpResponse(mimetype='%s/%s' % (part.media, part.media_subtype))
    
    if part.filename():
        filename = part.filename()
    else:
        filename = _('Unknown')

    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    response.write( message.part(part) )
    response.close()

    return response
    
def notImplemented(request):
    return render_to_response('not_implemented.html')
 
@login_required
def index(request):
    return HttpResponseRedirect(reverse('folder_list'))



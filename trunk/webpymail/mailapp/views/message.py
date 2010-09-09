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
# $Id$
#

"""Display folders and messages.
"""

# Global Imports
import base64
# Django:
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Local
from mail_utils import serverLogin
import msgactions

@login_required
def show_message(request, folder, uid):
    '''Show the message
    '''
    folder_name =  base64.urlsafe_b64decode(str(folder))

    M = serverLogin( request )
    folder = M[folder_name]
    message = folder[int(uid)]

    # If it's a POST request
    if request.method == 'POST':
        msgactions.message_change( request, message )

    return render_to_response('message_body.html',{'folder':folder,
        'message':message})

@login_required
def message_header( request, folder, uid ):
    '''Show the message header
    '''
    folder_name =  base64.urlsafe_b64decode(str(folder))

    M = serverLogin( request )
    folder = M[folder_name]
    message = folder[int(uid)]

    return render_to_response('message_header.html',{'folder':folder,
        'message':message})

@login_required
def message_structure( request, folder, uid ):
    '''Show the message header
    '''
    folder_name =  base64.urlsafe_b64decode(str(folder))

    M = serverLogin( request )
    folder = M[folder_name]
    message = folder[int(uid)]

    return render_to_response('message_structure.html',{'folder':folder,
        'message':message})

@login_required
def get_msg_part( request, folder, uid, part_number ):
    '''Gets a message part.
    '''
    folder_name =  base64.urlsafe_b64decode(str(folder))

    M = serverLogin( request )
    folder = M[folder_name]
    message = folder[int(uid)]
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

def not_implemented(request):
    return render_to_response('not_implemented.html')

@login_required
def index(request):
    return HttpResponseRedirect(reverse('folder_list'))



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
# $Id: msgactions.py 431 2008-12-03 17:49:12Z helder $
#

"""Actions on messages
"""

# Global Imports
# Django:
from django.http import Http404

# Local
from mailapp.forms import MessageActionForm

# System flags
DELETED = r'\Deleted'
SEEN = r'\Seen'
ANSWERED = r'\Answered'
FLAGGED = r'\Flagged'
DRAFT = r'\Draft'
RECENT = r'\Recent'

def message_change( request, message ):
    new_data = request.POST.copy()

    if new_data.has_key('delete'):
        message.set_flags(DELETED)
    elif new_data.has_key('undelete'):
        message.reset_flags(DELETED)

def batch_change(request, folder, message_list):
    new_data = request.POST.copy()
    if new_data.has_key('expunge'):
        folder.expunge()
        return

    if not new_data.getlist('messages'):
        # Do nothing if no messages are selected
        return

    # Validate the form
    form = MessageActionForm(new_data, message_list=message_list)
    if not form.is_valid():
        # Do nothing if the form isn't valid
        return

    selected_messages = form.cleaned_data['messages']
    try:
        selected_messages = [ int(Xi) for Xi in selected_messages ]
    except:
        return

    if new_data.has_key('delete'):
        folder.set_flags(selected_messages, DELETED)
    elif new_data.has_key('undelete'):
        folder.reset_flags(selected_messages, DELETED)
    elif new_data.has_key('read'):
        folder.set_flags(selected_messages, SEEN)
    elif new_data.has_key('unread'):
        folder.reset_flags(selected_messages, SEEN)




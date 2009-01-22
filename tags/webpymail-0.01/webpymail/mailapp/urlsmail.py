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
# $LastChangedDate: 2008-04-22 15:57:47 +0100 (Tue, 22 Apr 2008) $
# $LastChangedRevision: 325 $
# $LastChangedBy: helder $
# 

"""Mail interface"""

# Global imports:
from django.conf.urls.defaults import patterns, url

folder_pat = r'FOLDER_(?P<folder>[A-Za-z0-9+.&%_=-]+)'

urlpatterns = patterns('webpymail.mailapp.viewsmail',   
    url(r'^$', 'showFoldersView', name='folder_list'),
    
    url(r'^' + folder_pat + r'/$', 'showMessageListView', 
        name='message_list'),
        
    url(r'^' + folder_pat + r'/(?P<uid>[\d]+)/$', 'showMessage',
        name='mailapp-message'),
        
    url(r'^' + folder_pat + r'/(?P<uid>[\d]+)/(?P<part_number>\d+(?:\.\d+)*)/$', 
        'get_msg_part', name='mailapp_message_part'),
        
    url(r'^' + folder_pat + r'/(?P<uid>[\d]+)/HEADER/$', 
        'message_header', name='mailapp_message_header'),
        
    url(r'^' + folder_pat + r'/(?P<uid>[\d]+)/STRUCTURE/$', 
        'message_structure', name='mailapp_message_structure'),
    )
    
# Compose messages:
urlpatterns += patterns('webpymail.mailapp.compose',
    url(r'^compose/$', 'new_message', name='mailapp_send_message'),
    url(r'^' + folder_pat + r'/(?P<uid>[\d]+)/REPLY/$', 
        'reply_message', name='mailapp_reply_message'),
    url(r'^' + folder_pat + r'/(?P<uid>[\d]+)/REPLYALL/$', 
        'reply_all_message', name='mailapp_reply_all_message'),
    url(r'^' + folder_pat + r'/(?P<uid>[\d]+)/FORWARD_INLINE/$', 
        'forward_message_inline', name='mailapp_forward_inline_message'),
    url(r'^' + folder_pat + r'/(?P<uid>[\d]+)/FORWARD/$', 
        'forward_message', name='mailapp_forward_message'),
    )  

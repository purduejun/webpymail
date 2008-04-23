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
# $LastChangedDate: 2008-04-18 13:11:56 +0100 (Fri, 18 Apr 2008) $
# $LastChangedRevision: 322 $
# $LastChangedBy: helder $
# 

"""Authentication Forms"""

# Global imports:
from django import newforms as forms
from django.utils.translation import gettext_lazy as _

# Local Imports:
from mailapp.models import ImapServer

class LoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        imap_server_list = [ (Xi.id,Xi.name) 
                             for Xi in ImapServer.objects.all() ]
    
        self.fields['host'].choices = imap_server_list
        
    host = forms.ChoiceField(
        label = _('Imap Server'), 
        required=False,)
    username = forms.CharField(
        label = _('Username'), 
        required=False,
        max_length=30,)
    password = forms.CharField(
        label = _('Password'), 
        required=False,
        widget=forms.PasswordInput,
        max_length=40)
    next = forms.CharField(
        required=False,
        widget=forms.HiddenInput,
        max_length=256)
        
        
    


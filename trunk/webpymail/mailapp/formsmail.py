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

'''Forms used on the mailapp application
'''

# Imports

from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms.widgets import Input
from django.conf import settings

import re

from multifile import *

# Mail form exceptions

class MAILFORMERROR ( Exception ):
    pass

# Custom Fields

# Regular expressions:

single_mail_address = r'([_a-zA-Z0-9-]+(?:\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+' +\
                      r'(?:\.[a-zA-Z0-9-]+)*\.(?:(?:[0-9]{1,3})|' + \
                      r'(?:[a-zA-Z]{2,3})|(?:aero|coop|info|museum|name)))'

mail_address = r'(?:[\'"](.*?)[\'"] +)?<?' + single_mail_address + r'>?'

email_list_re = re.compile(mail_address)

teste_emails_re = re.compile(r'^ *(' + mail_address + r'[ ,;]*)+$')

class MultiEmailField(forms.Field):
    def clean(self, value):
        '''
        Clean up the address list provided by the user.

        The address list should have the mail addresses sepparated by commas,
        spaces or ';'.

        Each address may be represented by:

            DQUOTE | QUOTE + Name + DQUOTE | QUOTE <mail_address>
        or  <mail_address>
        or  mail_address

        Examples: "Test Address" <test@example.com>
                  'Test Address' <test@example.com>
                  <test@example.com>
                  test@example.com

        The return addresses will have the format:
            [('Name','address'), ... ]
        '''
        # Make sure that:
        #   i) The addresses are valid
        #  ii) There is at least one address
        if not teste_emails_re.match(value):
            if not self.required and not value:
                return ''
            elif not self.required and value:
                raise forms.ValidationError(_('Invalid mail address.'))
            raise forms.ValidationError(_('Enter at least one valid email address.'))

        # Get all the addresses as a list
        emails = email_list_re.findall(value)

        if len(emails) > settings.MAXADDRESSES:
            raise forms.ValidationError('%s %s' % \
                (_("Exceeded the maximum number of addresses by:"),
                len(emails)- settings.MAXADDRESSES))

        return emails

class MultyChecksum(forms.Field):
    '''Field used to hold a list checksums of the uploaded files
    '''
    widget = forms.HiddenInput()
    required = False
    def clean(self, value):
        # FIXME: Lacking validation here
        return value.split(',')



# Forms

class ComposeMailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('user_profile')
        super(ComposeMailForm, self).__init__(*args, **kwargs)

        # Populate the identity choices
        from_list = [ ( profile.default_identity,
                        profile.default_identity ) ]
        for identity in profile.useridentity_set.all():
            if identity != profile.default_identity:
                from_list += [ (identity, identity ) ]
        self.fields['from_addr'].choices = from_list

    from_addr    = forms.ChoiceField(
        label = _('From'),
        help_text = "<div class=\"helptext\">%s</div>" % \
            _('Your email address'),
        required=True
        )

    to_addr      = MultiEmailField(
        label = _('To'),
        help_text = "<div class=\"helptext\">%s</div>" % \
            _('To addresses, separated by commas'),
        widget=forms.TextInput( attrs={'size':settings.SINGLELINELEN }),
        required=True
        )

    cc_addr      = MultiEmailField(
        label = _('Cc'),
        help_text= "<div class=\"helptext\">%s</div>" % \
        _('Carbon Copy addresses, separated by commas'),
        widget=forms.TextInput( attrs={'size':settings.SINGLELINELEN }),
        required=False
        )

    bcc_addr     = MultiEmailField(
        label = _('Bcc'),
        help_text= "<div class=\"helptext\">%s</div>" % \
        _('Blind Carbon Copy addresses, separated by commas'),
        widget=forms.TextInput( attrs={'size':settings.SINGLELINELEN }),
        required=False
        )

    filter       = forms.ChoiceField(
        choices = ((1,_('Plain')),(2,_('reST'))),
        label = _('Filter'), )

    subject      = forms.CharField(
        max_length=100,
        label = _('Subject'),
        widget=forms.TextInput( attrs={'size':settings.SINGLELINELEN }),
        required=False)

    message_text = forms.CharField(
        label = _('Message Text'),
        widget=forms.Textarea( attrs={'rows':settings.TEXTAREAROWS,
                                      'cols':settings.TEXTAREACOLS}),
        required=False)

    attachment = MultiFileField(
        label = _('Attachment'),
        required=False,
        count = 1 )

    saved_files = MultyChecksum( required = False, widget = forms.HiddenInput())

class MessageActionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        message_list = kwargs.pop('message_list')
        super(MessageActionForm, self).__init__(*args, **kwargs)

        # Populate the identity choices
        self.fields['messages'].choices = message_list

    messages = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)

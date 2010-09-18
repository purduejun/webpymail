# -*- coding: utf-8 -*-

# sabapp - Simple Address Book Application
# Copyright (C) 2008 Helder Guerreiro

## This file is part of sabapp.
##
## sabapp is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## sabapp is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with sabapp.  If not, see <http://www.gnu.org/licenses/>.

#
# Helder Guerreiro <helder@paxjulia.com>
#
# $Id$
#

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

# Models:

ADDRESSBOOKTYPE = (
    (1, _('User address book')),
    (2, _('Server address book')),
    (3, _('Site address book')),
    )

class Address(models.Model):
    user = models.ForeignKey(User, null=True)
    imap_server = models.CharField(_('IMAP server'), max_length=128)

    nickname = models.CharField(max_length=64)
    first_name = models.CharField(_('first name'), max_length=30, blank = True)
    last_name = models.CharField(_('last name'), max_length=64, blank = True)
    email = models.EmailField(_('e-mail address'))
    additional_info = models.CharField(_('aditional information'),
        max_length=128, blank = True)

    ab_type = models.IntegerField(choices=ADDRESSBOOKTYPE)

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

        db_table = 'address_book'

        unique_together = (('user', 'imap_server', 'nickname',
            'ab_type'),)

    def __str__(self):
        return '"%s %s" <%s>' % (self.first_name, self.last_name, self.email)
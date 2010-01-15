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

# Helder Guerreiro <helder@paxjulia.com>
#
# $Id$
#

# Imports

from django.db import models
from django.utils.translation import gettext_lazy as _

# Table
class AuthImapServer(models.Model):
    name  = models.CharField(verbose_name=_('Server name'),
        max_length=128)
    host  = models.CharField(verbose_name=_('Host name'),
        max_length=128)
    port  = models.PositiveIntegerField(verbose_name=_('Port number'),
        default=143)
    is_ssl = models.BooleanField(verbose_name=_('Is ssl'),
        default=False)

    def __unicode__(self):
        return self.name

    class Admin:
        list_display = ('name', 'is_ssl', )

    class Meta:
        verbose_name = _('Imap Server')
        verbose_name_plural = _('Imap Servers')

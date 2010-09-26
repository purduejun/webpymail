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

"""Authentication views to use with the IMAP auth backend
"""

# Global imports:
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, HttpResponse
from django.template import RequestContext
from django.utils.translation import gettext_lazy as _

# Local imports:
from forms import LoginForm
from utils.config import server_config

def loginView(request):
    """Login the user on the system
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            next = form.cleaned_data['next']
            try:
                server = form.cleaned_data['host']
                config = server_config()
                host = config.get( server, 'host' )
                port = config.getint( server, 'port' )
                ssl  = config.getboolean( server, 'ssl' )
            except:
                return render_to_response('wpmauth/login.html',
                    { 'form': form,
                      'error_message': _('Invalid server. '\
                          'Please try again.') },
                    context_instance=RequestContext(request))
            try:
                user = authenticate(username=username[:30],
                    password=password, host=host, port=port, ssl=ssl)
            except ValueError:
                return render_to_response('wpmauth/login.html',
                    { 'form': form,
                      'error_message': _('Invalid login. '\
                          'Please try again.') },
                    context_instance=RequestContext(request))
            if user is not None:
                if user.is_active:
                    login(request, user)

                    # Not an imap user:
                    if (request.session['_auth_user_backend'] ==
                     'django.contrib.auth.backends.ModelBackend'):
                        return render_to_response('wpmauth/login.html',
                        { 'form': form,
                          'error_message': _('This is not an IMAP '
                                 'valid account. Please try again.') },
                        context_instance=RequestContext(request))

                    request.session['username'] = username
                    request.session['password'] = password
                    request.session['host'] = host
                    request.session['port'] = port
                    request.session['ssl'] = ssl
                    return HttpResponseRedirect(next)
                # Disabled account:
                else:
                    return render_to_response('wpmauth/login.html',
                        { 'form': form,
                          'error_message': _('Sorry, disabled ' \
                          'account.') },
                        context_instance=RequestContext(request))
            # Invalid user:
            else:
                return render_to_response('wpmauth/login.html',
                    { 'form': form,
                      'error_message': _('Invalid login. Please ' \
                          'try again.') },
                    context_instance=RequestContext(request))
        # Invalid form:
        else:
            return render_to_response('wpmauth/login.html',
                { 'form': form },
                context_instance=RequestContext(request))
    # Display the empty form:
    else:
        try:
            next = request['next']
            if next == '': next = settings.LOGIN_SUCCESS
        except:
            next = settings.LOGIN_SUCCESS
        data = { 'next': next }
        form = LoginForm(data)
        return render_to_response('wpmauth/login.html',{ 'form': form },
            context_instance=RequestContext(request))

def logoutView(request):
    request.session.modified = True
    logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect(settings.LOGOUT_SUCCESS)


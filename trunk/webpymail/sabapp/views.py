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

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render_to_response, redirect

from forms import AddressForm
from models import Address

# Views:

@login_required
def delete_address(request, address_id ):
    try:
        address = Address.objects.get( id = int(address_id),
            user = request.user, ab_type = 1 )
    except ObjectDoesNotExist:
        raise Http404

    address.delete()

    return redirect('browse_addresses')

@login_required
def manage_address(request, address_id = None):
    '''Add an address to the user's address book'''
    context = {}

    if address_id:
        try:
            address = Address.objects.get( id = int(address_id),
                user = request.user, ab_type = 1 )
        except ObjectDoesNotExist:
            raise Http404

    if request.method == 'POST':
        if  request.POST.has_key('cancel'):
            return redirect('browse_addresses')
        if address_id:
            form = AddressForm(request.POST, instance = address)
        else:
            form = AddressForm(request.POST)
        if form.is_valid():
            # Save the new address
            address = form.save(commit=False)
            address.user = request.user
            address.imap_server = request.session['host']
            address.ab_type = 1
            address.save()
            return redirect('browse_addresses')
        else:
            # Show errors:
            context['form'] = form
    else:
        # Empty form
        if address_id:
            context['form'] = AddressForm(instance = address)
        else:
            context['form'] = AddressForm()

    return render_to_response('manage_address.html', context )

@login_required
def browse_addresses(request):
    host = request.session['host']

    address_list = Address.objects.filter(
        Q( user__exact = request.user, imap_server__exact = host, ab_type__exact = 1 ) |
        Q( imap_server__exact = host, ab_type__exact = 2 ) |
        Q( ab_type__exact = 3 ) ).order_by('first_name', 'last_name')

    return render_to_response('browse_addresses.html',
        { 'address_list': address_list } )
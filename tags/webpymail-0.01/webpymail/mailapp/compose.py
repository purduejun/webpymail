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
# $LastChangedDate: 2008-04-12 00:42:15 +0100 (Sat, 12 Apr 2008) $
# $LastChangedRevision: 307 $
# $LastChangedBy: helder $
# 

"""Compose form
"""

# Import

# Sys
import time
import tempfile
import os
import re

# Mail
from email import encoders
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.message import MIMEMessage
from email import message_from_file

import smtplib
from smtplib import SMTPRecipientsRefused, SMTPException

# Django
from django.conf import settings 
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.utils.html import escape
from django.utils.translation import ugettext as _

# Local Imports
from models import Attachments
from formsmail import ComposeMailForm
from utils import serverLogin, mail_addr_str, mail_addr_name_str, \
                  quote_wrap_lines, join_address_list, show_addrs
                  
# RE

delete_re = re.compile(r'^delete_(\d+)$')
                  
def compose_rfc822( from_addr, to_addr, cc_addr, bcc_addr, 
                subject, message_text, attachment_list = [] ):
    '''
    Returns a rfc822 compliant message
    '''
    
    # Create the message text:
    msg_text = MIMEText(message_text, _charset='utf-8')
    
    # Include the attachments:
    if attachment_list.file_list:
        msg = MIMEMultipart('MIXED')
        msg.attach(msg_text)
        for attachment in attachment_list.file_list:
            filename = attachment.temp_file
            if attachment.media() == 'TEXT':
                fp = open(filename)
                # Note: we should handle calculating the charset
                attach = MIMEText(fp.read(), _subtype=attachment.media_subtype(),
                    _charset='utf-8')
                fp.close()
            elif attachment.media() == 'IMAGE':
                fp = open(filename, 'rb')
                attach = MIMEImage(fp.read(), _subtype=attachment.media_subtype())
                fp.close()
            elif attachment.media() == 'AUDIO':
                fp = open(filename, 'rb')
                attach = MIMEAudio(fp.read(), _subtype=attachment.media_subtype())
                fp.close()
            elif (attachment.media() == 'MESSAGE' and 
                    attachment.media_subtype() == 'RFC822'):
                fp = open(filename, 'rb')
                attach =  MIMEMessage( message_from_file(fp) , 'RFC822' )
                fp.close()
            else:
                fp = open(filename, 'rb')
                attach = MIMEBase(attachment.media(), attachment.media_subtype())
                attach.set_payload(fp.read())
                fp.close()
                
                # Encode the payload using Base64
                encoders.encode_base64(attach)
                
            # Set the filename parameter
            attach.set_param('name',attachment.filename)
            attach.add_header('Content-Disposition', 'attachment', 
                filename=attachment.filename)
                
            msg.attach(attach)
    else:
        msg = msg_text
    
    if subject:
        msg['Subject'] = subject
    if from_addr:
        msg['From'] = from_addr
    if to_addr:
        msg['To'] = to_addr
    if cc_addr:
        msg['Cc'] = cc_addr
    if bcc_addr:
        msg['Bcc'] = bcc_addr
        
    msg['Date'] = (time.strftime('%a, %d %b %Y %H:%M:%S ', time.localtime()) + 
                    '%+05d' % time.timezone)
    msg['X-Mailer'] = 'WebPyMail %s' % settings.WEBPYMAIL_VERSION
    
    return msg
    
def send_mail( message,  smtp_host = settings.SMTPHOST, 
        smtp_port = settings.SMTPPORT, user = settings.SMTPUSER, 
        passwd = settings.SMTPPASS ):
    '''
    Sends a message to a smtp server
    '''
    s = smtplib.SMTP(smtp_host, smtp_port)

    if user:
        s.login( user, passwd)
    
    to_addr_list = []
    
    if message['To']:
        to_addr_list.append(message['To'])
    if message['Cc']:
        to_addr_list.append(message['Cc'])
    if message['Bcc']:
        to_addr_list.append(message['Bcc'])
        
    to_addr_list = ','.join(to_addr_list).split(',')

    s.sendmail(message['From'], to_addr_list, message.as_string())
    s.close()
    
def imap_store( request, folder, message ):
    '''
    Stores a message on an IMAP folder.
    '''
    M = serverLogin( request )
    folder = M.folders[folder]
    folder.append(message.as_string())
    
class UploadFiles:
    def __init__(self, user, old_files = None, new_files = None):
        self.file_list = []
        self.user = user
        if new_files:
            # We have new uploaded files
            self.add_new_files( new_files )
        
        if old_files:
            # We have previously uploaded files
            self.add_old_files( old_files )
        
    def delete_id(self, id):
        for fl in self.file_list:
            if fl.id == id:
                # Remove file from the list:
                self.file_list.remove(fl)
                # Remove file from the file system
                os.remove(fl.temp_file)
                # Remove the file from the attachments table
                fl.delete()
            
    def delete(self): 
        for fl in self.file_list:
            # Remove file from the file system
            os.remove(fl.temp_file)
            # Remove the file from the attachments table
            fl.delete()
            
        self.file_list = []
            
    def id_list(self):
        return [ Xi.id for Xi in self.file_list ]
      
    def add_old_files(self, file_list ):
        '''
        @param file_list: a list of Attachments table ids.
        '''
        obj_lst = Attachments.objects.filter(user__exact=self.user).in_bulk(file_list)
        self.file_list += [ Xi for Xi in obj_lst.itervalues() ]
        
    def add_new_files(self, file_list ):
        '''
        @param file_list: a file list as returned on request.FILES
        '''
        for a_file in file_list:
            # Create a temporary file
            fl = tempfile.mkstemp(suffix='.tmp', prefix='webpymail_', 
                dir=settings.TEMPDIR)
                
            # Save the attachments to the temp file
            os.write( fl[0], a_file['content'] )
            os.close(fl[0])
            
            # Add a entry to the Attachments table:
            attachment = Attachments(
                user = self.user,
                temp_file = fl[1],
                filename = a_file['filename'],
                mime_type = a_file['content-type'],
                sent = False )
            attachment.save()
            self.file_list.append(attachment)
        
def send_message(request, text='', to_addr='', cc_addr='', subject='', 
    attachments=''):
    '''
    '''
    if request.method == 'POST':
        new_data = request.POST.copy()
        other_action = False
        
        old_files = []
        if new_data['saved_files']:
            old_files = new_data['saved_files'].split(',')
            
        uploaded_files = UploadFiles( request.user,
            old_files = old_files, 
            new_files = request.FILES.getlist('attachment[]'))
            
        # Check if there is a request to delete files
        for key in new_data:
            match = delete_re.match(key)
            if match:
                id = int(match.groups()[0])
                uploaded_files.delete_id(id)
                other_action = True
                
        # Check if the cancel button was pressed
        if  new_data.has_key('cancel'):
            # Delete the files
            uploaded_files.delete()
            # return
            return HttpResponseRedirect('/')
            
        # create an hidden field with the file list.
        # In case the form does not validate, the user doesn't have 
        # to upload it again
        new_data['saved_files'] = ','.join([ '%d' % Xi 
            for Xi in uploaded_files.id_list()])
            
        user_profile = request.user.get_profile()    
        
        form = ComposeMailForm(new_data, user_profile = user_profile)
        
        if new_data.has_key('upload'):
            other_action = True

        if form.is_valid() and not other_action:
            # get the data:
            form_data = form.cleaned_data

            subject = form_data['subject']
            from_addr  = form_data['from_addr']
            
            to_addr    = join_address_list( form_data['to_addr'] )
            cc_addr    = join_address_list( form_data['cc_addr'] )
            bcc_addr   = join_address_list( form_data['bcc_addr'] )
            
            message_text = form_data['message_text']
            
            message = compose_rfc822( from_addr, to_addr, cc_addr, bcc_addr, 
                subject, message_text, uploaded_files )
            
            try:  
                send_mail( message )
            except SMTPRecipientsRefused, detail:
                error_message = ''.join( 
                    ['<p>%s' % escape(detail.recipients[Xi][1]) 
                     for Xi in detail.recipients ] )                
                return render_to_response('send_message.html', {'form':form, 
                    'server_error': error_message,
                    'uploaded_files': uploaded_files})
            except SMTPException, detail:
                return render_to_response('send_message.html', {'form':form, 
                    'server_error': detail.smtp_error,
                    'uploaded_files': uploaded_files})
               
            # Store the message on the sent folder
            import base64
            imap_store( request, 
                base64.urlsafe_b64encode(user_profile.sent_folder), message )
            
            # Delete the temporary files
            uploaded_files.delete()
            
            return HttpResponseRedirect('/')
        else:
            return render_to_response('send_message.html', {'form':form,
                'uploaded_files': uploaded_files })
            
    else:
        initial= { 'filter': 1, 
                   'message_text': text,
                   'to_addr': to_addr,
                   'cc_addr': cc_addr,
                   'subject': subject,
                   'saved_files': attachments }
                   
        if attachments:
            uploaded_files = UploadFiles( request.user,
            old_files = attachments.split(',') )
        else:
            uploaded_files = []
        
        form = ComposeMailForm(initial=initial, 
            user_profile = request.user.get_profile())
        return render_to_response('send_message.html', {'form':form,
            'uploaded_files': uploaded_files })

@login_required 
def new_message( request ):
    return send_message(request)
 
@login_required   
def reply_message(request, folder, uid):
    '''Reply to a message'''
    # Get the message
    M = serverLogin( request )
    folder = M.folders[folder].select()
    message = folder.messages[uid]
    
    # Extract the relevant headers
    to_addr = mail_addr_str(message.envelope['env_from'][0])
    subject = _('Re: ') + unicode(message.envelope['env_subject'],'utf-8')
    
    # Extract the message text
    text = ''
    for part in message.bodystructure.serial_message():
        if part.is_text() and part.test_plain():
            text += message.part( part )
            
    # Quote the message
    text = quote_wrap_lines(text)
    text = (mail_addr_name_str(message.envelope['env_from'][0][1]) +
        _(' wrote:\n') + text)
    
    # Invoque the compose message form
    return send_message( request, text=text,  to_addr=to_addr, subject=subject)
    
@login_required   
def reply_all_message(request, folder, uid):
    '''Reply to a message'''
    # Get the message
    M = serverLogin( request )
    folder = M.folders[folder].select()
    message = folder.messages[uid]
    
    # Extract the relevant headers
    to_addr = mail_addr_str(message.envelope['env_from'][0])
    
    cc_addr =  join_address_list(message.envelope['env_to']+  
        message.envelope['env_cc'])
    
    subject = _('Re: ') + message.envelope['env_subject']
    
    # Extract the message text
    text = ''
    for part in message.bodystructure.serial_message():
        if part.is_text() and part.test_plain():
            text += message.part( part )
            
    # Quote the message
    text = quote_wrap_lines(text)
    text = (mail_addr_name_str(message.envelope['env_from'][0][1]) +
        _(' wrote:\n') + text)
    
    # Invoque the compose message form
    return send_message( request, text=text,  to_addr=to_addr, cc_addr=cc_addr,
                         subject=subject)
    
@login_required   
def forward_message(request, folder, uid):
    '''Reply to a message'''
    # Get the message
    M = serverLogin( request )
    folder = M.folders[folder].select()
    message = folder.messages[uid]

    # Create a temporary file
    fl = tempfile.mkstemp(suffix='.tmp', prefix='webpymail_', 
        dir=settings.TEMPDIR)
        
    # Save message source to a file
    os.write( fl[0], message.source() )
    os.close(fl[0])
    
    # Add a entry to the Attachments table:
    attachment = Attachments(
        user = request.user,
        temp_file = fl[1],
        filename = 'attached_message',
        mime_type = 'MESSAGE/RFC822',
        sent = False )
    attachment.save()

    # Gather some message info
    subject = _('Fwd: ') + message.envelope['env_subject']
    
    return send_message( request, subject=subject, 
        attachments='%d' % attachment.id)

    
@login_required   
def forward_message_inline(request, folder, uid):
    '''Reply to a message'''
    def message_header( message ):
        text = ''
        text += show_addrs( _('From'), message.envelope['env_from'],
        _('Unknown') )
        text += show_addrs( _('To'), message.envelope['env_to'], _('-') )
        text += show_addrs( _('Cc'), message.envelope['env_cc'], _('-') )
        text += _('Date: ') + message.envelope['env_date'].strftime('%Y-%m-%d %H:%M') + '\n' 
        text += _('Subject: ') + message.envelope['env_subject']+ '\n\n'
        
        return text
        
    # Get the message
    M = serverLogin( request )
    folder = M.folders[folder].select()
    message = folder.messages[uid]
    
    # Extract the message text
    text = ''
    text += '\n\n' + _('Forwarded Message').center(40,'-') + '\n'
    text += message_header( message )
    
    for part in message.bodystructure.serial_message():
        if part.is_text() and part.test_plain():
            text += message.part( part )
            
        if part.is_encapsulated():
            if part.is_start():
                text += '\n\n' + _('Encapsuplated Message').center(40,'-') + '\n'
                text += message_header( part )
            else:
                text += '\n' + _('End Encapsuplated Message').center(40,'-') 
    text += _('End Forwarded Message').center(40,'-') + '\n'
    
    # Extract the message attachments
    attach_list = []
    for part in message.bodystructure.serial_message():
        if part.is_attachment():
            # Create a temporary file
            fl = tempfile.mkstemp(suffix='.tmp', prefix='webpymail_', 
                dir=settings.TEMPDIR)
                
            # Save message source to a file
            os.write( fl[0], message.part(part) )
            os.close(fl[0])
            
            if part.filename():
                filename = part.filename()
            else:
                filename = _('Unknown')            
            
            # Add a entry to the Attachments table:
            attachment = Attachments(
                user = request.user,
                temp_file = fl[1],
                filename = filename,
                mime_type = '%s/%s' % (part.media, part.media_subtype),
                sent = False )
            attachment.save()
            attach_list.append(attachment.id)
     
    # Gather some message info
    subject = _('Fwd: ') + message.envelope['env_subject']
    
    return send_message( request, subject=subject, text = text, 
        attachments=','.join([ '%d' % Xi for Xi in attach_list ]) )
    

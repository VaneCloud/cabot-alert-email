# -*- coding: utf-8 -*-

from os import environ as env
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.template.loader import get_template
from cabot.cabotapp.alert import AlertPlugin
from cabot.cabotapp.models import StatusCheckResult

import requests
import logging


class EmailAlert(AlertPlugin):
    name = "Email"
    author = "Jonathan Balls"

    def send_alert(self, service, users, duty_officers):
        emails = [u.email for u in users if u.email]
        if not emails:
            return
        c = Context({
            'service': service,
            'host': settings.WWW_HTTP_HOST,
            'scheme': settings.WWW_SCHEME,
	    'StatusCheckResult': StatusCheckResult
        })
        if service.overall_status != service.PASSING_STATUS:
            if service.overall_status == service.CRITICAL_STATUS:
                emails += [u.email for u in users if u.email]
            subject = '服务 {} - {}'.format(service.name, service.overall_status)
        else:
            subject = '服务 {} 恢复正常'.format(service.name,)
        html_content= get_template('./alert.html').render(c)
	from_email='Cabot <%s>' % env.get('CABOT_FROM_EMAIL')
	msg = EmailMessage(subject, html_content, from_email, emails)
        msg.content_subtype = 'html'
	msg.send()


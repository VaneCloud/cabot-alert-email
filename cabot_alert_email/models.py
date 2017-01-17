# -*- coding: utf-8 -*-

from os import environ as env

from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template import Context, Template
from cabot.cabotapp.alert import AlertPlugin

import requests
import logging

email_template = """服务 {{ service.name }} {% if service.overall_status == service.PASSING_STATUS %} 恢复正常 {% else %} 问题很大 {% endif %}
{% if service.overall_status != service.PASSING_STATUS %}
{% for check in service.all_failing_checks %}
{{ check.name }} - 类别: {{ check.check_category }} - 级别: {{ check.get_importance_display }}{% endfor %}
{% endif %}
"""


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
            'scheme': settings.WWW_SCHEME
        })
        if service.overall_status != service.PASSING_STATUS:
            if service.overall_status == service.CRITICAL_STATUS:
                emails += [u.email for u in users if u.email]
            subject = '服务 {} - {}'.format(service.name, service.overall_status)
        else:
            subject = '服务 {} 恢复正常'.format(service.name,)
        t = Template(email_template)
        send_mail(
            subject=subject,
            message=t.render(c),
            from_email='Cabot <%s>' % env.get('CABOT_FROM_EMAIL'),
            recipient_list=emails,
        )

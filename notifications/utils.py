import json, os
from django.core.mail import EmailMessage
from django.template import Template, Context
from django.conf import settings
from .models import NotificationLog

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates.json")

def load_templates():
    with open(TEMPLATE_PATH, "r") as f:
        return json.load(f)

def render_template(template_str, context_dict):
    return Template(template_str).render(Context(context_dict))

def send_notification(user, template_key, context):
    templates = load_templates()
    tpl = templates.get(template_key)
    if not tpl:
        raise ValueError(f"Template '{template_key}' not found.")

    subject = render_template(tpl['subject'], context)
    body = render_template(tpl['body'], context)

    # Log entry first
    log = NotificationLog.objects.create(
        user=user, event_type=template_key, channel='email',
        subject=subject, message=body, status='pending'
    )

    # Send email
    try:
        email = EmailMessage(subject=subject, body=body, to=[user.email])
        email.send(fail_silently=False)
        log.status = 'sent'
        log.response = 'Email sent successfully'
        log.save()
    except Exception as e:
        log.status = 'failed'
        log.response = str(e)
        log.save()

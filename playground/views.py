from django.shortcuts import render

from django.core.mail import EmailMessage, BadHeaderError
from templated_mail.mail import BaseEmailMessage


def say_hello(request):
    try:
        message = BaseEmailMessage(
            template_name='emails/hello.html',
            context={'name': 'Leo'}
        )
        message.send('josh@deefarm.com')
    except BadHeaderError:
        pass
    return render(request)

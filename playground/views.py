from django.shortcuts import render

from django.core.mail import send_mail, mail_admins, BadHeaderError


def say_hello(request):
    try:
        send_mail('subject', 'message', 'info@dfoods.com', 'bob@gmail.com')
        mail_admins('subject', 'message', html_message='message')
    except BadHeaderError:
        pass
    return render(request)
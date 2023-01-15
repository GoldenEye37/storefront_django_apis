from django.shortcuts import render

from django.core.mail import EmailMessage, BadHeaderError


def say_hello(request):
    try:
        message = EmailMessage('subject', 'message', 'info@dfoods.com', ['bob@gmail.com'])
        message.attach_file('playground/static/images/meals.jpg')
        message.send()
    except BadHeaderError:
        pass
    return render(request)

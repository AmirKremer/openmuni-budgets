"""Custom context processors for Omuni"""
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, \
    PasswordChangeForm
from django.contrib.sites.models import Site
from registration.forms import RegistrationFormUniqueEmail


def get_site(request):
    """Returns a Site object for the global request context"""
    # If we will later map multiple hosts to the project
    #host = request.get_host()
    #site = Site.objects.get(domain=host)

    # But, for now
    site = Site.objects.get(pk=1)

    return {'site': site}


def auth_forms(request):

    auth_forms = {}

    login_form = AuthenticationForm
    registration_form = RegistrationFormUniqueEmail
    password_reset_form = PasswordResetForm
    password_change_form = PasswordChangeForm

    auth_forms['login_form'] = login_form
    auth_forms['registration_form'] = registration_form
    auth_forms['password_reset_form'] = password_reset_form

    if request.user.is_authenticated:
        auth_forms['password_change_form'] = password_change_form

    return auth_forms

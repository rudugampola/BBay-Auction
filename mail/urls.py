from django.urls import path

from . import views

app_name = "mail"

urlpatterns = [
    path("", views.index, name="mail-index"),

    # API Routes
    path("mail/emails", views.compose, name="compose"),
    path("mail/emails/<int:email_id>", views.email, name="email"),
    path("mail/emails/<str:mailbox>", views.mailbox, name="mailbox"),
]

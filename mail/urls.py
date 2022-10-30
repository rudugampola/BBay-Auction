from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="mail-index"),
    # path("login", views.login_view, name="login"),
    # path("logout", views.logout_view, name="logout"),
    # path("register", views.register, name="register"),

    # API Routes
    path("mail/emails", views.compose, name="compose"),
    path("mail/emails/<int:email_id>", views.email, name="email"),
    path("mail/emails/<str:mailbox>", views.mailbox, name="mailbox"),
]

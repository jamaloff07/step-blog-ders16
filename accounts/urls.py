from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    # [DƏRS 12] giriş və çıxış — view-u özümüz YAZMIRIQ, Django-nun hazır class-larını işlədirik
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),          # yalnız POST qəbul edir

    # [DƏRS 12] qeydiyyat — bunun hazır view-u yoxdur, özümüz yazırıq
    path("register/", views.register, name="register"),

    # [EV 12] bonus — profil · password: [REFERANS 12]
    path("profile/", views.profile, name="profile"),                          # tapşırıq 2
    path(                                                                     # tapşırıq 3
        "password/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password_change.html",
            success_url="/accounts/profile/",
        ),
        name="password_change",
    ),
]

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import RegisterForm

# Nişanlar:  [DƏRS 12] müəllim yazır · [EV 12] ev tapşırığı


# [DƏRS 12] dərsdə hazır UserCreationForm işlənir:  from django.contrib.auth.forms import UserCreationForm
# [REFERANS 12] — onun yerinə email-li RegisterForm
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()                                    # User yaranır, parol HASH olunub yazılır
            login(request, user)                                  # [REFERANS 12] — qeydiyyatdan sonra avtomatik giriş
            messages.success(request, f"Xoş gəldin, {user.username}!")
            return redirect("blog:post_list")                     # dərsdə: redirect("accounts:login")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required                                                   # [EV 12] bonus — profil
def profile(request):
    context = {
        "post_count": request.user.posts.count(),                 # related_name="posts"
        "comment_count": request.user.comments.count(),
    }
    return render(request, "accounts/profile.html", context)

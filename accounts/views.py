from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CustomUserCreationForm, CustomAuthenticationForm



def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "ユーザー登録が完了しました。ログインしてください。")
            return redirect("accounts:login")
    
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/signup.html",
                {"form": form})


def login_view(request):  # loginだとDjangoのlogin関数と衝突する可能性がある、login_viewと書くのが一般的
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, "ログインしました。")
            return redirect("mymath:index",)
    
    else:
        form = CustomAuthenticationForm()
    return render(request, "accounts/login.html",{"form": form})


@login_required
def logout_view(request): # login_view と同様にlogoutも衝突を避ける
    auth_logout(request)
    messages.success(request, "ログアウトしました。")
    return redirect("mymath:index")

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .serializers import ChangePasswordSerializer
from django.contrib import messages
from account.forms import PasswordChangeForm
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

# Import User model
from django.contrib.auth import get_user_model
User = get_user_model()

def registration_view(request):
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_pasword = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=raw_pasword)
            login(request, account)
            return redirect('home')
        else:
            context['registration_form'] = form
    else:
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'account/register.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

def login_view(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        return redirect("home")

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect("home")
        context['login_form'] = form  
    else:
        form = AccountAuthenticationForm()
        context['login_form'] = form

    return render(request, 'account/login.html', context)

@login_required
def account_view(request):
    return render(request, 'account/account.html')

@login_required
def reset_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ваш пароль успішно змінено!")
            return redirect('home')  
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'account/reset_password.html', {'form': form})

# API endpoint для зміни паролю
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def reset_password_api(request, user_id):
    if request.user.id != int(user_id):
        return Response(
            {"error": "Ви не маєте дозволу змінювати пароль іншого користувача"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = ChangePasswordSerializer(data=request.data)
    
    if serializer.is_valid():
        user = request.user
        old_password = serializer.validated_data.get('old_password')
        new_password = serializer.validated_data.get('new_password')

        if not user.check_password(old_password):
            return Response({"error": "Неправильний пароль"}, status=status.HTTP_400_BAD_REQUEST)
        
        if old_password == new_password:
            return Response({"error": "Введіть новий пароль"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response({"error": e.messages[0]}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        return Response({"success": "Ваш пароль успішно змінено!"}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
def account_change_view(request):
    if request.method == 'POST':
        form = AccountUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваші дані успішно оновлено!')
            return redirect('account')
    else:
        form = AccountUpdateForm(instance=request.user)
    
    context = {
        'form': form
    }
    return render(request, 'account/account_change.html', context)
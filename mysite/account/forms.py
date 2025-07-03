from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from account.models import Account
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=60,
    )
    username = forms.CharField(
        max_length=30,
    )

    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Підтвердіть пароль', widget=forms.PasswordInput)

    class Meta(UserCreationForm.Meta):
        model = Account
        fields = ('email', 'username')  

class AccountAuthenticationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ('email', 'password') 

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Неправильна адреса електронної пошти або пароль.")

class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('email', 'username') 

    def clean_email(self):
        email = self.cleaned_data['email']
        if Account.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('Ця електронна адреса вже пов’язана з обліковим записом. Якщо цей обліковий запис належить вам, ви можете скинути пароль')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if Account.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError('Ім\'я користувача вже використовується')
        return username


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        label='Поточний пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введіть поточний пароль'}),
        required=True
    )
    new_password = forms.CharField(
        label='Новий пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введіть новий пароль'}),
        required=True
    )
    confirm_password = forms.CharField(
        label='Підтвердження паролю',
        widget=forms.PasswordInput(attrs={'placeholder': 'Підтвердіть новий пароль'}),
        required=True
    )

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not check_password(current_password, self.user.password):
            raise forms.ValidationError("Неправильний пароль")
        return current_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        current_password = self.cleaned_data.get('current_password')
        
        # Перевірка чи новий пароль відрізняється від старого
        if current_password and check_password(new_password, self.user.password):
            raise forms.ValidationError("Введіть новий пароль")
        
        # Перевірка відповідності стандартам безпеки
        try:
            validate_password(new_password, self.user)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
            
        return new_password

    def clean_confirm_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Паролі не співпадають")
            
        return confirm_password

    def save(self):
        new_password = self.cleaned_data.get('new_password')
        self.user.set_password(new_password)
        self.user.save()
        return self.user  


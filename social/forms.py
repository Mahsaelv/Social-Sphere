from django import forms
from django.contrib.auth.password_validation import validate_password

from .models import User, Post, Comment
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=250,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control"
        })
    )
    password = forms.CharField(
        max_length=250,
        required=True,
        widget=forms.PasswordInput(attrs={
            "class": "form-control"
        })
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['old_password'].widget.attrs.update({
            'autocomplete': 'off',
            'autofocus': True,
            'placeholder': 'Current Password',
        })
        self.fields['new_password1'].widget.attrs.update({
            'autocomplete': 'new-password',
            'placeholder': 'New Password',
        })
        self.fields['new_password2'].widget.attrs.update({
            'autocomplete': 'new-password',
            'placeholder': 'Confirm New Password',
        })


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords do not match')

        validate_password(cd['password'], self.instance)

        return cd['password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'date_of_birth', 'bio', 'photo', 'job']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'job': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'نام کاربری',
            'first_name': 'نام',
            'email': 'ایمیل',
            'date_of_birth': 'تاریخ تولد',
            'bio': 'بایو',
            'job': 'شغل',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.exclude(id=self.instance.id).filter(username=username).exists():
            raise ValidationError("username already exists!")
        return username.strip()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(id=self.instance.id).filter(email=email).exists():
            raise ValidationError("email already exists!")
        return email.lower().strip()

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob and dob > timezone.now().date():
            raise ValidationError("Date of birth can't be in future!")
        return dob


class CreatePostForm(forms.ModelForm):
    image1 = forms.ImageField(label="تصویر اول", widget=forms.FileInput(attrs={'class': 'form-control'}))
    image2 = forms.ImageField(label="تصویر دوم", widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Post
        fields = ['description', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': "3"
            }),
        }
        labels = {
            'tags': 'تگ ها',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.TextInput(attrs={
                'class': 'form-control input-sm'
            }),
        }


class EditPostForm(forms.ModelForm):
    image1 = forms.ImageField(
        required=False,
        label="Image 1",
        widget=forms.ClearableFileInput(attrs={
            'accept': 'image/*',
            'class': 'block w-full text-sm text-zinc-100 file:bg-zinc-700 file:text-zinc-100 file:px-4 file:py-2 file:rounded-lg'
        })
    )
    image2 = forms.ImageField(
        required=False,
        label="Image 2",
        widget=forms.ClearableFileInput(attrs={
            'accept': 'image/*',
            'class': 'block w-full text-sm text-zinc-100 file:bg-zinc-700 file:text-zinc-100 file:px-4 file:py-2 file:rounded-lg'
        })
    )

    class Meta:
        model = Post
        fields = ['description', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full bg-zinc-700 text-zinc-100 p-3 rounded-lg focus:ring-purple-400'
            }),
        }

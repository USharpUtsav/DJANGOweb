from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Post, Comment

class RegistrationForm(forms.ModelForm):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    address = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}))
    favorite_food = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Favorite Food'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}), label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}), label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'address', 'favorite_food']

    # Ensure passwords match
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise ValidationError("Passwords do not match")

    # Save method to handle custom fields
    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.first_name = self.cleaned_data['favorite_food']  # Store favorite food in first_name
        user.last_name = self.cleaned_data['address']         # Store address in last_name
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


class ResetPasswordForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        }),
        label='Username'
    )
    favorite_food = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Favorite Food'
        }),
        label='Favorite Food'
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        favorite_food = cleaned_data.get("favorite_food")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError("No user found with this username")

        # Verify favorite food matches the first_name field
        if user.first_name != favorite_food:
            raise ValidationError("Favorite food does not match")

        return cleaned_data

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']  # Use 'content' instead of 'text'
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Add a comment',
                'required': True
            })
        }

from django import forms

class NewPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password'
        }),
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        }),
        label="Confirm Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

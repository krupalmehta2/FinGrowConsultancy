from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import ContactInquiry, CustomerProfile


class RegistrationForm(forms.Form):
    input_attrs = {"class": "fg-auth-input"}
    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={**input_attrs, "autocomplete": "name", "required": True}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={**input_attrs, "autocomplete": "email", "required": True}))
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={**input_attrs, "autocomplete": "new-password", "required": True}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={**input_attrs, "autocomplete": "new-password", "required": True}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") and cleaned.get("confirm_password") and cleaned["password"] != cleaned["confirm_password"]:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("That email address is already registered.")
        return email

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def save(self):
        user = User.objects.create_user(username=self.cleaned_data["email"], email=self.cleaned_data["email"], password=self.cleaned_data["password"])
        CustomerProfile.objects.create(user=user, full_name=self.cleaned_data["full_name"])
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "fg-auth-input", "autocomplete": "email", "required": True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "fg-auth-input", "autocomplete": "current-password", "required": True}))

    def clean(self):
        cleaned = super().clean()
        user = User.objects.filter(email__iexact=cleaned.get("email", "")).first()
        if not user or not user.check_password(cleaned.get("password", "")) or not user.is_active:
            raise forms.ValidationError("Enter a valid email address and password.")
        cleaned["user"] = user
        return cleaned

    def get_user(self):
        return self.cleaned_data["user"]


class ContactInquiryForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactInquiry
        fields = ["name", "phone", "email", "subject", "message", "page_type", "page_title", "current_url"]

    def clean_website(self):
        value = self.cleaned_data.get("website")
        if value:
            raise forms.ValidationError("Invalid submission.")
        return value

    def clean_message(self):
        return self.cleaned_data.get("message", "").strip()
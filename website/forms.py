from django import forms

from .models import ContactInquiry


class ContactInquiryForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)
    class Meta:
        model = ContactInquiry
        fields = [
            "name",
            "phone",
            "email",
            "subject",
            "message",
            "page_type",
            "page_title",
            "current_url",
        ]

    def clean_website(self):
        value = self.cleaned_data.get("website")
        if value:
            raise forms.ValidationError("Invalid submission.")
        return value

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 10:
            raise forms.ValidationError("Please provide at least 10 characters.")
        return message

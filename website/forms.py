from django import forms

from .models import ContactInquiry


class ContactInquiryForm(forms.ModelForm):
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

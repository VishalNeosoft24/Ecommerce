from django import forms
from .models import Banner, EmailTemplate


class EmailTemplateForm(forms.ModelForm):

    class Meta:
        model = EmailTemplate
        exclude = ["created_by", "updated_by", "deleted_at"]
        fields = "__all__"
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Email Template Name"}
            ),
            "subject": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Email Subject"}
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Email Body",
                }
            ),
        }


class BannerForm(forms.ModelForm):

    class Meta:
        model = Banner
        exclude = ["created_by", "updated_by", "deleted_at", "status"]
        fields = "__all__"
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Banner Title"}
            ),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "url": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Url"}
            ),
        }

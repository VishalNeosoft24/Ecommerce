from django import forms

from order_management.models import UserOrder
from .models import Banner, EmailTemplate
from django.contrib.flatpages.models import FlatPage
from django.core.exceptions import ValidationError
from django.contrib.sites.models import Site


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
                    "id": "summernote",
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


class FlatPageForm(forms.ModelForm):
    class Meta:
        model = FlatPage
        fields = [
            "url",
            "title",
            "content",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Banner Title"}
            ),
            "url": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Url"}
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "id": "summernote",
                    "placeholder": "Content",
                }
            ),
        }

    def clean_url(self):
        url = self.cleaned_data.get("url")
        if not url.startswith("/"):
            raise ValidationError("URL must start with a forward slash ('/').")
        return url

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if len(title) < 5:
            raise ValidationError("Title must be at least 5 characters long.")
        return title

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        url = cleaned_data.get("url")

        # Example of cross-field validation
        if title and "example" in title.lower():
            raise ValidationError("The title cannot contain the word 'example'.")

        # Ensure unique URL for each site
        site = Site.objects.get_current()
        if self.instance.pk:
            # If editing an existing instance, exclude it from the uniqueness check
            if (
                FlatPage.objects.filter(url=url, sites=site)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise ValidationError(
                    f"A flat page with the URL '{url}' already exists on this site."
                )
        else:
            # If creating a new instance, check for uniqueness
            if FlatPage.objects.filter(url=url, sites=site).exists():
                raise ValidationError(
                    f"A flat page with the URL '{url}' already exists on this site."
                )

        return cleaned_data


class UserOrderForm(forms.ModelForm):
    class Meta:
        model = UserOrder
        fields = ["status"]  # Include all fields
        widgets = {
            "status": forms.Select(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        instance = super(UserOrderForm, self).save(commit=False)
        if "status" in self.changed_data:  # Only update 'status' if it has changed
            instance.status = self.cleaned_data.get("status")
        if commit:
            instance.save()
        return instance

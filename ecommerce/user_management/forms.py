from django import forms
from .models import User
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _
from admin_panel.models import Address, ContactUs, NewsLetter


class UpdateUserForm(forms.ModelForm):
    """Update user profile"""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs.update({"class": "form-control"})
        self.fields["last_name"].widget.attrs.update({"class": "form-control"})
        self.fields["email"].widget.attrs.update({"class": "form-control"})
        self.fields["phone_number"].widget.attrs.update({"class": "form-control"})

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not first_name:
            raise ValidationError(_("First Name is required."))
        if not first_name.isalpha():
            raise ValidationError(
                _("First Name must contain only alphabetic characters.")
            )
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not last_name:
            raise ValidationError(_("Last Name is required."))
        if not last_name.isalpha():
            raise ValidationError(
                _("Last Name must contain only alphabetic characters.")
            )
        return last_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if not phone_number:
            raise ValidationError(_("Phone number is required."))
        if not phone_number.isdigit():
            raise ValidationError(_("Phone number must be numeric."))
        if not len(phone_number) == 10:
            raise ValidationError(_("Phone number must be 10 digits long."))
        return phone_number

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise ValidationError(_("Email is required."))
        validator = EmailValidator()
        try:
            validator(email)
        except ValidationError:
            raise ValidationError(_("Enter a valid email address."))
        return email


class AddressForm(forms.ModelForm):
    """Create and Update user address"""

    class Meta:
        model = Address
        fields = [
            "type",
            "country",
            "state",
            "city",
            "pincode",
            "street_address",
            "apartment_number",
            "phone_number",
            "default",
        ]
        widgets = {
            "type": forms.Select(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "pincode": forms.TextInput(attrs={"class": "form-control"}),
            "street_address": forms.TextInput(attrs={"class": "form-control"}),
            "apartment_number": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "default": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_country(self):
        """Validate country format and check if it is not empty."""
        country = self.cleaned_data.get("country")

        if not country:
            raise ValidationError(_("Country is required."))

        if not country.isalpha():
            raise ValidationError(
                _(
                    "Country must contain only letters. Please enter a valid country name."
                )
            )

        return country

    def clean_state(self):
        """Validate state format."""
        state = self.cleaned_data.get("state")
        if not state.isalpha():
            raise ValidationError(
                _("State must contain only letters. Please enter a valid state name.")
            )
        return state

    def clean_city(self):
        """Validate city format."""
        city = self.cleaned_data.get("city")
        if not city.isalpha():
            raise ValidationError(
                _("City must contain only letters. Please enter a valid city name.")
            )
        return city

    def clean_pincode(self):
        """Validate pincode format"""
        pincode = self.cleaned_data.get("pincode")
        if len(pincode) != 6 or not pincode.isdigit():
            raise ValidationError(_("Pincode must be exactly 6 digits."))
        return pincode

    def clean_phone_number(self):
        """Validate phone number format"""
        phone_number = self.cleaned_data.get("phone_number")
        if len(phone_number) != 10 or not phone_number.isdigit():
            raise ValidationError(_("Phone number must be exactly 10 digits."))
        return phone_number

    def clean(self):
        """Form-wide validation"""
        cleaned_data = super().clean()

        street_address = cleaned_data.get("street_address")
        apartment_number = cleaned_data.get("apartment_number")

        if not street_address and not apartment_number:
            raise ValidationError(
                _("Either street address or apartment number must be provided.")
            )

        # Add more form-wide validations as needed
        return cleaned_data


class ContactUsForm(forms.ModelForm):
    """Contact Us Form"""

    class Meta:
        model = ContactUs
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "message",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "First Name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Last Name"}
            ),
            "email": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Email"}
            ),
            "phone_number": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Phone Number"}
            ),
            "message": forms.Textarea(
                attrs={
                    "id": "message",
                    "class": "form-control",
                    "placeholder": "Your Message Here",
                }
            ),
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not first_name:
            raise ValidationError(_("First Name is required."))
        if not first_name.isalpha():
            raise ValidationError(
                _("First Name must contain only alphabetic characters.")
            )
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not last_name:
            raise ValidationError(_("Last Name is required."))
        if not last_name.isalpha():
            raise ValidationError(
                _("Last Name must contain only alphabetic characters.")
            )
        return last_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if not phone_number:
            raise ValidationError(_("Phone number is required."))
        if not phone_number.isdigit():
            raise ValidationError(_("Phone number must be numeric."))
        if not len(phone_number) == 10:
            raise ValidationError(_("Phone number must be 10 digits long."))
        return phone_number

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise ValidationError(_("Email is required."))
        validator = EmailValidator()
        try:
            validator(email)
        except ValidationError:
            raise ValidationError(_("Enter a valid email address."))
        return email


class NewsLetterForm(forms.ModelForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={"placeholder": "Your email address"}),
        error_messages={"required": "Please enter your email address"},
    )

    class Meta:
        model = NewsLetter
        fields = ["email"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if NewsLetter.objects.filter(email=email).exists():
            raise forms.ValidationError("You are already subscribed.")
        return email

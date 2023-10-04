from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text="Required. Enter a valid email address.")
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES, widget=forms.RadioSelect, required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'user_type', 'password1', 'password2')  # Fixed the fields tuple

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = "Your password can't be too similar to your other personal information."
        self.fields['password1'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['password2'].help_text = "Enter the same password as before, for verification."
        self.fields['password2'].widget.attrs['autocomplete'] = 'new-password'

class CustomUserAdminForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = '__all__'
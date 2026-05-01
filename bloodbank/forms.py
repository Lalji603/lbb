from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import User, BloodRequest, BloodStock, Donation

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    blood_group = forms.ChoiceField(choices=User.BLOOD_GROUP_CHOICES, required=False)
    phone = forms.CharField(max_length=15, required=True, help_text="Enter exactly 10 digits")
    address = forms.CharField(widget=forms.Textarea, required=True, help_text="Enter your full address")
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True, help_text="You must be at least 18 years old")

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'blood_group', 
                 'phone', 'address', 'date_of_birth', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if not email:
            raise forms.ValidationError("Email field is required.")
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        
        # Remove any non-digit characters
        phone_digits = ''.join(filter(str.isdigit, phone))
        
        # Check if exactly 10 digits
        if len(phone_digits) != 10:
            raise forms.ValidationError("Phone number must contain exactly 10 digits.")
        
        # Return only the digits
        return phone_digits

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        
        if date_of_birth:
            # Calculate age more accurately
            today = timezone.now().date()
            age = today.year - date_of_birth.year
            
            # Check if birthday has passed this year
            if (date_of_birth.month, date_of_birth.day) > (today.month, today.day):
                age -= 1
            
            # Check if user is at least 18 years old
            if age < 18:
                raise forms.ValidationError("You must be at least 18 years old to register.")
        
        return date_of_birth
    
    def clean_address(self):
        address = self.cleaned_data.get('address')
        
        # Check if address is provided but empty
        if address and not address.strip():
            raise forms.ValidationError("Address cannot be empty if provided.")
        
        return address.strip() if address else ''

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.address = self.cleaned_data.get('address', '')
        if commit:
            user.save()
        return user

class DonorBloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = ['blood_group', 'units_required', 'urgency', 'hospital_name', 
                 'hospital_address', 'doctor_name', 'reason', 'required_date']
        widgets = {
            'required_date': forms.DateInput(attrs={'type': 'date', 'min': ''}),
            'hospital_address': forms.Textarea(attrs={'rows': 3}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['required_date'].required = True
        self.fields['required_date'].widget.attrs['min'] = timezone.now().date().strftime('%Y-%m-%d')
        self.fields['required_date'].help_text = "Select a date from today onwards"
        # Store user for later use in field validation
        self.user = kwargs.get('user', None)

    def clean_required_date(self):
        required_date = self.cleaned_data.get('required_date')
        
        if required_date:
            today = timezone.now().date()
            if required_date < today:
                raise forms.ValidationError("Required date cannot be in the past. Please select today or a future date.")
        
        return required_date

class BloodStockForm(forms.ModelForm):
    class Meta:
        model = BloodStock
        fields = ['blood_group', 'units']

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['donation_date', 'units_donated', 'notes']
        widgets = {
            'donation_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class ProfileForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=10, 
        required=True, 
        help_text="Enter exactly 10 digits",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': '[0-9]{10}',
            'maxlength': '10',
            'placeholder': 'Enter 10 digit phone number'
        })
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3
        }), 
        required=True
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }), 
        required=True, 
        help_text="You must be at least 18 years old"
    )
    blood_group = forms.ChoiceField(
        choices=User.BLOOD_GROUP_CHOICES, 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'address', 'date_of_birth', 'blood_group']
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        
        # Remove any non-digit characters
        phone_digits = ''.join(filter(str.isdigit, phone))
        
        # Check if exactly 10 digits
        if len(phone_digits) != 10:
            raise forms.ValidationError("Phone number must contain exactly 10 digits.")
        
        # Return only the digits
        return phone_digits

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        
        if date_of_birth:
            # Calculate age more accurately
            today = timezone.now().date()
            age = today.year - date_of_birth.year
            
            # Check if birthday has passed this year
            if (date_of_birth.month, date_of_birth.day) > (today.month, today.day):
                age -= 1
            
            # Check if user is at least 18 years old
            if age < 18:
                raise forms.ValidationError("You must be at least 18 years old to register.")
        
        return date_of_birth

# Use DonorBloodRequestForm for all users to avoid patient field issues
BloodRequestForm = DonorBloodRequestForm

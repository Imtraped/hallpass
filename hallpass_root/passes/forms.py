from django import forms
from django.forms import ModelForm
from .models import Student, HallPass, Destination, Category, Profile
from django.forms.widgets import TextInput
from django.core.exceptions import ValidationError
from django_toggle_switch_widget.widgets import DjangoToggleSwitchWidget


class LogForm(forms.Form):
    log_id = forms.CharField() # This is all we need to get cleaned_data from the form

class LocationForm(forms.Form):
    log_id = forms.CharField() # This is all we need to get cleaned_data from the form
    destination_id = forms.CharField() # This is all we need to get cleaned_data from the form


    
class ArrivalForm(forms.Form):
    student_id = forms.CharField(max_length=6)
    destination_id = forms.CharField() # This is all we need to get cleaned_data from the form
    
    # This function contains the custom validation 
    # for the student_if field
    def clean_student_id(self):
        input_id = self.cleaned_data["student_id"]
        id_length = len(input_id)
        validate = []

        if id_length != 6:
            validate.append("IDs must be 6 numbers")
            
        if not input_id.isnumeric():
            validate.append("IDs cannot contain letters")

        if not Student.objects.filter(student_id=input_id).exists():
            validate.append("This ID is not in our system.")

        # We can let kids go to the 
        # bathroom if they are from another school 
        # if student_query[0].building != self.request.user.profile.building:
        #     validate += "Student must belong to current building"
            
        if (len(validate) > 0):
            raise ValidationError(validate)

        return input_id
    
class ProfileForm(forms.ModelForm):
    destinations_choices = None
    destinations = forms.ModelMultipleChoiceField(
        label='Destinations', 
        queryset=destinations_choices, 
        required=False, 
        widget=forms.CheckboxSelectMultiple()
    )
    destinations.widget.template_name = 'widgets/destination_choices.html'

    class Meta:
        model = Profile
        fields = ('building','destinations','queue')
        widgets = {
            'building': forms.Select(attrs={'onchange':'this.form.submit()'}),
            'queue': forms.CheckboxInput(attrs={"class": "form-check-input", "id": "flexSwitchCheckChecked"})
             # This isn't best practice. We should use JS for this.
        }

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        # Order_by sorts the choices by alpha.
        self.destinations_choices = Destination.objects.filter(building = self.instance.building).order_by('room', 'category')
        self.fields['destinations'].queryset = self.destinations_choices
        self.fields['building'].label="Buildings"


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
            'text_color': TextInput(attrs={'type': 'color'}),
        }

class ContactForm(forms.Form):
    name = forms.CharField(max_length=128)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea())

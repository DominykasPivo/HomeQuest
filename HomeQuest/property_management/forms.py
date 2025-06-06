from django import forms
from .models import Property, Comment
from django.utils.translation import gettext_lazy as _

class PropertyForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        label="Property Image",
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )

    class Meta:
        model = Property
        fields = [
            'location', 'map_location', 'price', 'size', 'room_num',
            'property_type', 'listing_type', 'duration'
        ]
        labels = {
            'location': _('Location'),
            'map_location': _('Map Location'),
            'price': _('Price'),
            'size': _('Size'),
            'room_num': _('Number of Rooms'),
            'property_type': _('Property Type'),
            'listing_type': _('Listing Type'),
            'duration': _('Duration'),
        }
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Make all fields required except duration
            for name, field in self.fields.items():
                if name not in ['duration']:
                    field.required = True
                else:
                    field.required = False

        def clean(self):
            cleaned_data = super().clean()
            listing_type = cleaned_data.get('listing_type')
            duration = cleaned_data.get('duration')
            if listing_type == 'for_rent' and not duration:
                self.add_error('duration', 'Duration is required for rental properties.')
            return cleaned_data
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add your comment...'}),
        }
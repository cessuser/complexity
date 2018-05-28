# from otree import __version__
# if int(__version__.split('.')[0])<=1:
#     import floppyforms.__future__ as forms
# else:
from django import forms
from .models import Player, Constants,Risk

from django.forms import inlineformset_factory, BaseFormSet, BaseInlineFormSet
import django.forms as djforms




#
class RiskForm(forms.ModelForm):
    CHOICES = ((False, '',), (True, '',))
    answer = djforms.ChoiceField(widget=forms.RadioSelect(attrs={'required':''}), choices=CHOICES, required=True)


RiskFormSet = inlineformset_factory(Player, Risk,
                                  fields=['answer'],
                                  can_delete=False,
                                  extra=0,
                                    form=RiskForm,
                                  )

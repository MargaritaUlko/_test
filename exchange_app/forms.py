# exchange_app/forms.py
from django import forms
from .models import Ad, ExchangeProposal

class AdFilterForm(forms.Form):
    category = forms.ChoiceField(
        choices=Ad.CATEGORY_CHOICES,
        required=False,
        label='Категория'
    )
    condition = forms.ChoiceField(
        choices=Ad.CONDITION_CHOICES,
        required=False,
        label='Состояние'
    )
    search = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={'placeholder': 'Название или описание'})
    )


class AdCreateForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'image_url', 'category', 'condition']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://example.com/image.jpg'}),
            'category': forms.Select(choices=Ad.CATEGORY_CHOICES),
            'condition': forms.Select(choices=Ad.CONDITION_CHOICES),
        }
        labels = {
            'image_url': 'Ссылка на изображение'
        }

class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'ad_receiver', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:

            self.fields['ad_sender'].queryset = Ad.objects.filter(user=user)
            self.fields['ad_receiver'].queryset = Ad.objects.exclude(user=user)

    def clean(self):
        cleaned_data = super().clean()
        ad_sender = cleaned_data.get('ad_sender')
        ad_receiver = cleaned_data.get('ad_receiver')

        if ad_sender and ad_receiver:
            if ad_sender.user == ad_receiver.user:
                raise forms.ValidationError("Нельзя создавать предложение между своими объявлениями")
            
            if ExchangeProposal.objects.filter(
                ad_sender=ad_sender, 
                ad_receiver=ad_receiver
            ).exists():
                raise forms.ValidationError("Предложение уже существует")
            
        return cleaned_data

class ProposalFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('', 'Все'), 
        *ExchangeProposal.STATUS_CHOICES
    ]
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    direction = forms.ChoiceField(
        choices=[('sent', 'Отправленные'), ('received', 'Полученные')],
        required=False
    )




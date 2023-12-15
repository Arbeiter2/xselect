from django import forms
from .models import Creator, Site, SiteAccount, CreatorSiteAccount, SiteAccountCharge, CreatorPhoto

class SearchForm(forms.Form):
    gender = forms.ChoiceField()
    country = forms.CharField()
    tags = forms.CharField(widget=forms.Textarea)

class CreatorForm(forms.ModelForm):
    class Meta:
        model = Creator
        fields = ['name', 'photo', 'description', 'email', 'biodata', 'user']


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['url', 'name']


class SiteAccountForm(forms.ModelForm):
    class Meta:
        model = SiteAccount
        fields = ['account', 'data']


class CreatorSiteAccountForm(forms.ModelForm):
    class Meta:
        model = CreatorSiteAccount
        fields = ['creator', 'site_account', 'photo']


class SiteAccountChargeForm(forms.ModelForm):
    class Meta:
        model = SiteAccountCharge
        fields = ['description', 'currency', 'frequency']


class CreatorPhotoForm(forms.ModelForm):
    class Meta:
        model = CreatorPhoto
        fields = ['url', 'deleted']



from django.contrib import admin
from django import forms
from .models import Creator, Site, SiteAccount, CreatorSiteAccount, SiteAccountCharge, CreatorPhoto #, ContentTag 

class CreatorAdminForm(forms.ModelForm):

    class Meta:
        model = Creator
        fields = '__all__'


class CreatorAdmin(admin.ModelAdmin):
    form = CreatorAdminForm
    list_display = ['name', 'slug', 'created', 'last_updated', 'photo', 'description', 'email', 'biodata']
    readonly_fields = ['name', 'slug', 'created', 'last_updated', 'photo', 'description', 'email', 'biodata']

admin.site.register(Creator, CreatorAdmin)


class SiteAdminForm(forms.ModelForm):

    class Meta:
        model = Site
        fields = '__all__'


class SiteAdmin(admin.ModelAdmin):
    form = SiteAdminForm
    list_display = ['url', 'name', 'slug', 'created', 'last_updated']
    readonly_fields = ['url', 'name', 'slug', 'created', 'last_updated']

admin.site.register(Site, SiteAdmin)


class SiteAccountAdminForm(forms.ModelForm):

    class Meta:
        model = SiteAccount
        fields = '__all__'


class SiteAccountAdmin(admin.ModelAdmin):
    form = SiteAccountAdminForm
    list_display = ['account', 'created', 'last_updated', 'data']
    readonly_fields = ['account', 'created', 'last_updated', 'data']

admin.site.register(SiteAccount, SiteAccountAdmin)

class SiteAccountChargeAdminForm(forms.ModelForm):

    class Meta:
        model = SiteAccountCharge
        fields = '__all__'


class SiteAccountChargeAdmin(admin.ModelAdmin):
    form = SiteAccountChargeAdminForm
    list_display = ['created', 'last_updated', 'description', 'currency', 'frequency']
    readonly_fields = ['created', 'last_updated', 'description', 'currency', 'frequency']

admin.site.register(SiteAccountCharge, SiteAccountChargeAdmin)


class CreatorPhotoAdminForm(forms.ModelForm):

    class Meta:
        model = CreatorPhoto
        fields = '__all__'


class CreatorPhotoAdmin(admin.ModelAdmin):
    form = CreatorPhotoAdminForm
    list_display = ['slug', 'created', 'last_updated', 'url', 'deleted']
    readonly_fields = ['slug', 'created', 'last_updated', 'url', 'deleted']

admin.site.register(CreatorPhoto, CreatorPhotoAdmin)


# class ContentTagAdmin(admin.ModelAdmin):
#     list_display = ("display_name",)
#     prepopulated_fields = {"slug": ("display_name",)}  # new

# admin.site.register(ContentTag, ContentTagAdmin)
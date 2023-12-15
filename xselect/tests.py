import unittest
from django.urls import reverse
from django.test import Client
from .models import Creator, Site, SiteAccount, CreatorSiteAccount, SiteAccountCharge, CreatorPhoto
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType


def create_django_contrib_auth_models_user(**kwargs):
    defaults = {}
    defaults["username"] = "username"
    defaults["email"] = "username@tempurl.com"
    defaults.update(**kwargs)
    return User.objects.create(**defaults)


def create_django_contrib_auth_models_group(**kwargs):
    defaults = {}
    defaults["name"] = "group"
    defaults.update(**kwargs)
    return Group.objects.create(**defaults)


def create_django_contrib_contenttypes_models_contenttype(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ContentType.objects.create(**defaults)


def create_creator(**kwargs):
    defaults = {}
    defaults["name"] = "name"
    defaults["slug"] = "slug"
    defaults["photo"] = "photo"
    defaults["description"] = "description"
    defaults["email"] = "email"
    defaults["biodata"] = "biodata"
    defaults.update(**kwargs)
    if "user" not in defaults:
        defaults["user"] = create_user()
    return Creator.objects.create(**defaults)


def create_site(**kwargs):
    defaults = {}
    defaults["url"] = "url"
    defaults["name"] = "name"
    defaults["slug"] = "slug"
    defaults.update(**kwargs)
    return Site.objects.create(**defaults)


def create_siteaccount(**kwargs):
    defaults = {}
    defaults["account"] = "account"
    defaults["data"] = "data"
    defaults.update(**kwargs)
    return SiteAccount.objects.create(**defaults)


def create_creatorsite(**kwargs):
    defaults = {}
    defaults["account"] = "account"
    defaults["is_active"] = "is_active"
    defaults["photo"] = "photo"
    defaults["description"] = "description"
    defaults.update(**kwargs)
    return CreatorSiteAccount.objects.create(**defaults)


def create_siteaccountcharge(**kwargs):
    defaults = {}
    defaults["description"] = "description"
    defaults["currency"] = "currency"
    defaults["frequency"] = "frequency"
    defaults.update(**kwargs)
    return SiteAccountCharge.objects.create(**defaults)


def create_creatorphoto(**kwargs):
    defaults = {}
    defaults["slug"] = "slug"
    defaults["url"] = "url"
    defaults["deleted"] = "deleted"
    defaults.update(**kwargs)
    return CreatorPhoto.objects.create(**defaults)


class CreatorViewTest(unittest.TestCase):
    '''
    Tests for Creator
    '''
    def setUp(self):
        self.client = Client()

    def test_list_creator(self):
        url = reverse('creator_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_creator(self):
        url = reverse('creator_create')
        data = {
            "name": "name",
            "slug": "slug",
            "photo": "photo",
            "description": "description",
            "email": "email",
            "biodata": "biodata",
            "user": create_user().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_creator(self):
        creator = create_creator()
        url = reverse('creator_detail', args=[creator.slug,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_creator(self):
        creator = create_creator()
        data = {
            "name": "name",
            "slug": "slug",
            "photo": "photo",
            "description": "description",
            "email": "email",
            "biodata": "biodata",
            "user": create_user().pk,
        }
        url = reverse('creator_update', args=[creator.slug,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class SiteViewTest(unittest.TestCase):
    '''
    Tests for Site
    '''
    def setUp(self):
        self.client = Client()

    def test_list_site(self):
        url = reverse('site_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_site(self):
        url = reverse('site_create')
        data = {
            "url": "url",
            "name": "name",
            "slug": "slug",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_site(self):
        site = create_site()
        url = reverse('site_detail', args=[site.slug,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_site(self):
        site = create_site()
        data = {
            "url": "url",
            "name": "name",
            "slug": "slug",
        }
        url = reverse('site_update', args=[site.slug,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class SiteAccountViewTest(unittest.TestCase):
    '''
    Tests for SiteAccount
    '''
    def setUp(self):
        self.client = Client()

    def test_list_siteaccount(self):
        url = reverse('siteaccount_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_siteaccount(self):
        url = reverse('siteaccount_create')
        data = {
            "account": "account",
            "data": "data",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_siteaccount(self):
        siteaccount = create_siteaccount()
        url = reverse('siteaccount_detail', args=[siteaccount.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_siteaccount(self):
        siteaccount = create_siteaccount()
        data = {
            "account": "account",
            "data": "data",
        }
        url = reverse('siteaccount_update', args=[siteaccount.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class CreatorSiteAccountViewTest(unittest.TestCase):
    '''
    Tests for CreatorSiteAccount
    '''
    def setUp(self):
        self.client = Client()

    def test_list_creatorsite(self):
        url = reverse('creatorsite_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_creatorsite(self):
        url = reverse('creatorsite_create')
        data = {
            "account": "account",
            "is_active": "is_active",
            "photo": "photo",
            "description": "description",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_creatorsite(self):
        creatorsite = create_creatorsite()
        url = reverse('creatorsite_detail', args=[creatorsite.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_creatorsite(self):
        creatorsite = create_creatorsite()
        data = {
            "account": "account",
            "is_active": "is_active",
            "photo": "photo",
            "description": "description",
        }
        url = reverse('creatorsite_update', args=[creatorsite.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class SiteAccountChargeViewTest(unittest.TestCase):
    '''
    Tests for SiteAccountCharge
    '''
    def setUp(self):
        self.client = Client()

    def test_list_siteaccountcharge(self):
        url = reverse('siteaccountcharge_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_siteaccountcharge(self):
        url = reverse('siteaccountcharge_create')
        data = {
            "description": "description",
            "currency": "currency",
            "frequency": "frequency",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_siteaccountcharge(self):
        siteaccountcharge = create_siteaccountcharge()
        url = reverse('siteaccountcharge_detail', args=[siteaccountcharge.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_siteaccountcharge(self):
        siteaccountcharge = create_siteaccountcharge()
        data = {
            "description": "description",
            "currency": "currency",
            "frequency": "frequency",
        }
        url = reverse('siteaccountcharge_update', args=[siteaccountcharge.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class CreatorPhotoViewTest(unittest.TestCase):
    '''
    Tests for CreatorPhoto
    '''
    def setUp(self):
        self.client = Client()

    def test_list_creatorphoto(self):
        url = reverse('creatorphoto_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_creatorphoto(self):
        url = reverse('creatorphoto_create')
        data = {
            "slug": "slug",
            "url": "url",
            "deleted": "deleted",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_creatorphoto(self):
        creatorphoto = create_creatorphoto()
        url = reverse('creatorphoto_detail', args=[creatorphoto.slug,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_creatorphoto(self):
        creatorphoto = create_creatorphoto()
        data = {
            "slug": "slug",
            "url": "url",
            "deleted": "deleted",
        }
        url = reverse('creatorphoto_update', args=[creatorphoto.slug,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)



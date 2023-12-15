"""
    _summary_
"""
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django_extensions.db import fields as extension_fields


class Creator(models.Model):
    """_summary_

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Fields
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    slug = extension_fields.AutoSlugField(populate_from='name', blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    photo = models.URLField()
    description = models.TextField(max_length=1000)
    email = models.EmailField()
    biodata = models.JSONField()


    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'{self.slug}'

    def get_absolute_url(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return reverse('creator_detail', args=(self.slug,))


    def get_update_url(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return reverse('creator_update', args=(self.slug,))


class Fan(models.Model):
    """_summary_

    Args:
        models (_type_): _description_
    """
    # Fields
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)



class Site(models.Model):
    """_summary_

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Fields
    url = models.URLField()
    name = models.CharField(max_length=255)
    slug = extension_fields.AutoSlugField(populate_from='name', blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)


    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.slug)

    def get_absolute_url(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return reverse('site_detail', args=(self.slug,))

    def get_update_url(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return reverse('site_update', args=(self.slug,))


class SiteAccount(models.Model):
    """_summary_

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Fields
    site = models.ForeignKey(
        'Site',
        on_delete=models.CASCADE, related_name="siteaccounts",
    )
    # Fields
    account = models.CharField(max_length=60)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    is_active = models.BooleanField(default=True)
    data = models.JSONField()
    fans = models.ManyToManyField(
        'SiteAccount',
        related_name='favourites'
    )

    def get_absolute_url(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return reverse('siteaccount_detail', args=(self.site.slug, self.account,))

    def get_update_url(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return reverse('siteaccount_update', args=(self.id,))

    def __str__(self):
        return f'{self.site}/{self.account}'

    def save(self, *args, **kwargs):
        self.account = self.account.lower()
        return super(SiteAccount, self).save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['site', 'account'],
                name='site_account_unique',
            ),
        ]
        ordering = ('account',)

class UserFavorite(models.Model):
    """_summary_

    Args:
        models (_type_): _description_
    """
    # Fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    site_account = models.ForeignKey(SiteAccount, on_delete=models.CASCADE,
                                     related_name="favorites")
    added = models.DateTimeField(auto_now_add=True, editable=False)
    notes = models.TextField(max_length=120)
    deleted = models.DateTimeField(default=None, editable=True)

    class Meta:
        unique_together = ['user', 'site_account']


class SiteAccountRank(models.Model):
    """_summary_

    Args:
        models (_type_): _description_
    """
    # Fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rankings")
    site_account = models.ForeignKey(SiteAccount, on_delete=models.CASCADE, related_name="rankings")
    rank = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    added = models.DateTimeField(auto_now_add=True, editable=False)
    deleted = models.DateTimeField(default=None, editable=True)

    class Meta:
        unique_together = ['user', 'site_account']


class CreatorSiteAccount(models.Model):
    """_summary_

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Fields
    creator = models.ForeignKey(
        'Creator',
        on_delete=models.CASCADE, related_name="creatorsites",
    )
    site_account = models.ForeignKey(
        'SiteAccount',
        on_delete=models.CASCADE, related_name="creatoraccounts",
    )
    # Fields
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    photo = models.URLField()


    class Meta:
        ordering = ('-created',)
        unique_together = ['creator', 'site_account']

    def __str__(self):
        return f'{self.pk}'

    def get_absolute_url(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return reverse('creatorsite_detail', args=(self.pk,))


    def get_update_url(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return reverse('creatorsite_update', args=(self.pk,))


class SiteAccountCharge(models.Model):
    """_summary_

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Fields
    site_account = models.ForeignKey(
        'SiteAccount',
        on_delete=models.CASCADE, related_name="siteaccountcharges",
    )
    FREQUENCY = (
        ("30D", "30 Days"),
        ("31D", "31 Days"),
        ("1M", "Month"),
        ("3M", "3 months"),
        ("6M", "6 months"),
        ("12M", "12 months"),
    )

    # Fields
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    description = models.TextField(max_length=100)
    amount = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    currency = models.CharField(max_length=3, default='USD')
    frequency = models.CharField(max_length=4, choices=FREQUENCY)
    expiry_date = models.DateTimeField(null=True, editable=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'{self.pk}'

    def get_absolute_url(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return reverse('creatorsitecharge_detail', args=(self.pk,))


    def get_update_url(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return reverse('creatorsitecharge_update', args=(self.pk,))


class CreatorPhoto(models.Model):
    """_summary_

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Fields
    creator = models.ForeignKey(
        'Creator',
        on_delete=models.CASCADE, related_name="creatorphotos",
    )

    # Fields
    slug = extension_fields.AutoSlugField(populate_from='name', blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    url = models.URLField()
    deleted = models.BooleanField(default=False)


    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'{self.slug}'

    def get_absolute_url(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return reverse('creatorphoto_detail', args=(self.slug,))

    def get_update_url(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return reverse('creatorphoto_update', args=(self.slug,))

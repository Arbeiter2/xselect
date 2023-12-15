import logging
from rest_framework import serializers

from . import models


logger = logging.getLogger('aws')


class CreatorSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Creator
        fields = (
            'pk',
            'slug', 
            'name', 
            'created', 
            'last_updated', 
            'photo', 
            'description', 
            'email', 
            'biodata', 
        )
        read_only_fields = ['pk', 'created', 'last_updated', ]


class SiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Site
        fields = (
            'slug', 
            'url', 
            'name', 
            'created', 
            'last_updated', 
        )


class SiteAccountSerializer(serializers.ModelSerializer):
    site = serializers.SlugRelatedField(slug_field='slug',
        queryset = models.Site.objects.all()
    )
    is_active = serializers.BooleanField(required=False, default=True)
    url = serializers.URLField(required=False, read_only=True, source='get_absolute_url')

    class Meta:
        model = models.SiteAccount
        fields = (
            'id', 
            'site',
            'account', 
            'is_active', 
            'created', 
            'last_updated', 
            'data',
            'url',
        )
        read_only_fields = ['id', 'created', 'last_updated', 'url']


    def validate(self, data):
        """
        Validate serializer data

        Arguments:
            data: incoming serializer data

        Returns:
            data on success,
            throws ValidationError otherwise
        """
        logger.info("SiteAccountSerializer::validate")
        mem = super(SiteAccountSerializer, self).validate(data)
        print(mem)
        self.instance = models.SiteAccount.objects.filter(
            site=mem['site'],
            account=mem['account'].lower()).first()
        print(self.instance)
        return data


    # def create(self, validated_data):
    #     """
    #     Create Timetable and children
    #     """
    #     instance = models.SiteAccount(**validated_data)
    #     instance.save()

    #     logger.info("instance = SiteAccount(%s)", validated_data)
    #     logger.info("instance.save()")
    #     return instance


    # def update(self, instance, validated_data):
    #     """
    #     Update existing Timetable
    #     """


    #     instance.save()

    #     return instance



class CreatorSiteAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CreatorSiteAccount
        fields = (
            'pk', 
            'creator',
            'site_account',
            'created', 
            'last_updated', 
            'photo', 
        )


class SiteAccountChargeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SiteAccountCharge
        fields = (
            'pk', 
            'created', 
            'last_updated', 
            'description', 
            'currency', 
            'frequency', 
        )


class CreatorPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CreatorPhoto
        fields = (
            'slug', 
            'created', 
            'last_updated', 
            'url', 
            'deleted', 
        )

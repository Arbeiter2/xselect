from . import models
from . import serializers
from rest_framework import viewsets, permissions


class CreatorViewSet(viewsets.ModelViewSet):
    """ViewSet for the Creator class"""

    queryset = models.Creator.objects.all()
    serializer_class = serializers.CreatorSerializer
    permission_classes = [permissions.IsAuthenticated]


class SiteViewSet(viewsets.ModelViewSet):
    """ViewSet for the Site class"""

    queryset = models.Site.objects.all()
    serializer_class = serializers.SiteSerializer
    permission_classes = [permissions.IsAuthenticated]


class SiteAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for the SiteAccount class"""

    queryset = models.SiteAccount.objects.all()
    serializer_class = serializers.SiteAccountSerializer
    permission_classes = [permissions.IsAuthenticated]


class CreatorSiteAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for the CreatorSiteAccount class"""

    queryset = models.CreatorSiteAccount.objects.all()
    serializer_class = serializers.CreatorSiteAccountSerializer
    permission_classes = [permissions.IsAuthenticated]


class SiteAccountChargeViewSet(viewsets.ModelViewSet):
    """ViewSet for the SiteAccountCharge class"""

    queryset = models.SiteAccountCharge.objects.all()
    serializer_class = serializers.SiteAccountChargeSerializer
    permission_classes = [permissions.IsAuthenticated]


class CreatorPhotoViewSet(viewsets.ModelViewSet):
    """ViewSet for the CreatorPhoto class"""

    queryset = models.CreatorPhoto.objects.all()
    serializer_class = serializers.CreatorPhotoSerializer
    permission_classes = [permissions.IsAuthenticated]


from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from rest_framework import routers
from django.contrib.auth import views as auth_views

from . import api
from . import views

router = routers.DefaultRouter()
router.register(r'creator', api.CreatorViewSet)
router.register(r'site', api.SiteViewSet)
router.register(r'siteaccount', api.SiteAccountViewSet)
router.register(r'creatorsite', api.CreatorSiteAccountViewSet)
router.register(r'siteaccountcharge', api.SiteAccountChargeViewSet)
router.register(r'creatorphoto', api.CreatorPhotoViewSet)

urlpatterns = [
     path('password_reset/', auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"), name="reset_password"),
]



urlpatterns += [
    # urls for Django Rest Framework API
    path('api/v1/', include(router.urls)),
]

urlpatterns += [
    re_path(r'xselect/taglist/?', views.TagView, name="tag_list"),
]

urlpatterns = [
    path('login/', views.MyLoginView.as_view(), name='login'),
]

urlpatterns += [
    path('', views.HomeView.as_view(), name="index")
]

urlpatterns += [
    path('search/', views.SearchView.as_view(), name="search")
]

# urlpatterns += (
#     # urls for Creator
#     path('xselect/creator/', views.CreatorListView.as_view(), name='creator_list'),
#     path('xselect/creator/create/', views.CreatorCreateView.as_view(), name='creator_create'),
#     path('xselect/creator/detail/<slug:slug>/', views.CreatorDetailView.as_view(), name='creator_detail'),
#     path('xselect/creator/update/<slug:slug>/', views.CreatorUpdateView.as_view(), name='creator_update'),
# )

urlpatterns += (
    # urls for Site
    re_path(r'xselect/sites/?$', views.SiteListView.as_view(), name='site_list'),
    re_path(r'xselect/sites/(?P<slug>[0-9a-zA-Z_\-.]+)/?$', views.SiteView.as_view(), name='site_detail'),
)

urlpatterns += (
    # urls for SiteAccount
    re_path(r'xselect/site_accounts/(?P<site__slug>\w+)/(?P<account>[0-9a-zA-Z_\-.]+)/?$', 
            views.SiteAccountView.as_view(), name='siteaccount_detail'),
    # re_path(r'xselect/site_accounts/(?P<site__slug>\w+)/?$', 
    #         views.SiteAccountListView.as_view(), name='siteaccount_list'),
    re_path(r'xselect/site_accounts/?$', views.SiteAccountListView.as_view(),
            name='siteaccount_list'),
    #re_path(r'xselect/site_accounts/(?P<id>\d+)/?$', views.SiteAccountView.as_view(),
    #        name='siteaccount_detail'),
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# urlpatterns += (
#     # urls for SiteAccount
#     path('xselect/siteaccount/', views.SiteAccountListView.as_view(), name='siteaccount_list'),
#     path('xselect/siteaccount/create/', views.SiteAccountCreateView.as_view(), name='siteaccount_create'),
#     path('xselect/siteaccount/detail/<int:pk>/', views.SiteAccountDetailView.as_view(), name='siteaccount_detail'),
#     path('xselect/siteaccount/update/<int:pk>/', views.SiteAccountUpdateView.as_view(), name='siteaccount_update'),
# )

# urlpatterns += (
#     # urls for CreatorSiteAccount
#     path('xselect/creatorsite/', views.CreatorSiteAccountListView.as_view(), name='creatorsite_list'),
#     path('xselect/creatorsite/create/', views.CreatorSiteAccountCreateView.as_view(), name='creatorsite_create'),
#     path('xselect/creatorsite/detail/<int:pk>/', views.CreatorSiteAccountDetailView.as_view(), name='creatorsite_detail'),
#     path('xselect/creatorsite/update/<int:pk>/', views.CreatorSiteAccountUpdateView.as_view(), name='creatorsite_update'),
# )

# urlpatterns += (
#     # urls for SiteAccountCharge
#     path('xselect/siteaccountcharge/', views.SiteAccountChargeListView.as_view(), name='siteaccountcharge_list'),
#     path('xselect/siteaccountcharge/create/', views.SiteAccountChargeCreateView.as_view(), name='siteaccountcharge_create'),
#     path('xselect/siteaccountcharge/detail/<int:pk>/', views.SiteAccountChargeDetailView.as_view(), name='siteaccountcharge_detail'),
#     path('xselect/siteaccountcharge/update/<int:pk>/', views.SiteAccountChargeUpdateView.as_view(), name='siteaccountcharge_update'),
# )

# urlpatterns += (
#     # urls for CreatorPhoto
#     path('xselect/creatorphoto/', views.CreatorPhotoListView.as_view(), name='creatorphoto_list'),
#     path('xselect/creatorphoto/create/', views.CreatorPhotoCreateView.as_view(), name='creatorphoto_create'),
#     path('xselect/creatorphoto/detail/<slug:slug>/', views.CreatorPhotoDetailView.as_view(), name='creatorphoto_detail'),
#     path('xselect/creatorphoto/update/<slug:slug>/', views.CreatorPhotoUpdateView.as_view(), name='creatorphoto_update'),
# )

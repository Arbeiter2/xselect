import os
import logging
import json
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from rest_framework import generics, status
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import PermissionDenied
from django_countries import countries
from tagging.models import Tag, TaggedItem
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth.views import LoginView


from .models import Creator, Site, SiteAccount, CreatorSiteAccount, SiteAccountCharge, CreatorPhoto
from .forms import CreatorForm, SearchForm, SiteForm, SiteAccountForm, CreatorSiteAccountForm, SiteAccountChargeForm, CreatorPhotoForm
from .serializers import SiteAccountSerializer, SiteSerializer
from .settings import STATIC_ROOT

logger = logging.getLogger('xselect')

class MyLoginView(LoginView):
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('tasks') 
    
    def form_invalid(self, form):
        messages.error(self.request,'Invalid username or password')
        return self.render_to_response(self.get_context_data(form=form))
    
    
def search(request):
    return render(request, 'search_results.html', locals())

def TagView(request):
    tag_list = []
    filename = f"{STATIC_ROOT}/tag-list"
    if "save" in request.GET or not os.path.exists(filename):
        tag_list = [tag.name for tag in Tag.objects.usage_for_model(SiteAccount, min_count=2)]
        country_names = [name.lower() for _, name in list(countries)]
        logger.info("country_name = %s", country_names)
        clean_list = sorted(set(tag_list) - set(country_names))
        with open(filename, "w") as fp:
            json.dump(clean_list, fp)
        logger.info("Successfully wrote %d entries to %s", len(clean_list), filename)
    else:
        logger.info("Opening saved file")
        with open(filename) as fp:
            tag_list = json.load(fp)
    return JsonResponse(tag_list, safe=False)


class HomeView(View):
    def get(self, request, *args, **kwargs):
        form = SearchForm()
        context = {'form': form, }
        return render(request, 'search.html', context)


class SearchView(View):
    def get(self, request, *args, **kwargs):
        raise PermissionDenied

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        logger.info("post: args=%s, kwargs=%s, body=%s, POST=%s", args, kwargs, request.body, request.POST)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse([], safe=False)
        if 'tags' not in data or not isinstance(data['tags'], list):
            return JsonResponse([], safe=False)
        results = [acct.data for acct in TaggedItem.objects.get_by_model(SiteAccount, Tag.objects.filter(name__in=data['tags']))]
        #logger.info("results = %s", [acct['account'] for acct in results])
        return JsonResponse(results, safe=False, json_dumps_params={'ensure_ascii': False})


class SiteView(generics.RetrieveUpdateAPIView):
    """
    SiteView
    """
    serializer_class = SiteSerializer
    queryset = Site.objects.all()
    lookup_field = 'slug'


class SiteListView(generics.ListCreateAPIView):
    """
    SiteListView
    """
    serializer_class = SiteSerializer
    queryset = Site.objects.all()


class SiteAccountView(generics.RetrieveUpdateDestroyAPIView):
    """
    SiteAccountView
    """
    serializer_class = SiteAccountSerializer
    queryset = SiteAccount.objects.all()
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        """
        get
        """
        logger.info('args = %s, kwargs = %s, self.kwargs = %s', args, kwargs, self.kwargs)
        print(f'args = {args}, kwargs = {kwargs}, self.kwargs = {self.kwargs}')
        if 'id' not in kwargs:
            ret_val = self.queryset.filter(**kwargs).first()
            if ret_val:
                self.kwargs['id'] = kwargs['id'] = str(ret_val.id)
        print(f'args = {args}, kwargs = {kwargs}, self.kwargs = {self.kwargs}')
        return super().get(request, *args, **kwargs)


    def get_queryset(self):
        logger.info("""kwargs = %s""", self.kwargs)
        if 'site__slug' in self.kwargs:
            site = get_object_or_404(Site, slug=self.kwargs['site__slug'])
            return SiteAccount.objects.filter(site=site)
        return SiteAccount.objects.all()


class SiteAccountListView(generics.ListCreateAPIView):
    """
    SiteAccountListView
    """
    serializer_class = SiteAccountSerializer
    queryset = SiteAccount.objects.all()

    filter_map = {
        'site': "site__slug",
    }

    def get_queryset(self):
        """
        filter
        """
        logger.info("""request.GET = %s""", self.request.GET)
        param = {"is_active": True}

        for filter_key, param_str in SiteAccountListView.filter_map.items():
            value = self.request.GET.get(filter_key, None)
            if value:
                param[param_str] = value
        logger.info("TimetableListView::get_queryset - %s", param)
        return SiteAccount.objects.filter(**param)


    def __get_raw(self, queryset):
        out = {}
        for acct in queryset.all():
             out[acct.account] = acct.data
        return out

    def get(self, request, *args, **kwargs):
        """
        get
        """
        logger.info("""args = %s""", args)
        logger.info("""kwargs = %s""", kwargs)
        logger.info("""request.GET = %s""", request.GET)
        queryset = self.get_queryset()
        if "raw" in request.GET:
            return JsonResponse(self.__get_raw(queryset))
        srlzr = SiteAccountSerializer(queryset, read_only=True, many=True)
        return JsonResponse(srlzr.data, json_dumps_params={'ensure_ascii': False})


    def post(self, request, *args, **kwargs):
        """
        Add timetable to specific game
        """
        logger.info("""args = %s""", args)
        logger.info("""kwargs = %s""", kwargs)
        logger.info("""request.body = %s""", request.body)
        logger.info("""request.POST = %s""", request.POST)
        logger.info("""request.data = %s""", request.data)
        logger.info(request.body)
        srlzr = SiteAccountSerializer(data=json.loads(request.body), many=True)
        logger.info("Serializer created")
        is_valid = srlzr.is_valid(raise_exception=False)
        logger.info(srlzr.errors)
        logger.info('instance = %s', srlzr.instance)
        srlzr.save()
        status_code = status.HTTP_200_OK if srlzr.instance else status.HTTP_201_CREATED
        return HttpResponse(status=status_code)


class CreatorListView(generics.ListCreateAPIView):
    model = Creator


class CreatorView(generics.RetrieveUpdateDestroyAPIView):
    model = Creator
    form_class = CreatorForm


# class CreatorDetailView(DetailView):
#     model = Creator


# class CreatorUpdateView(UpdateView):
#     model = Creator
#     form_class = CreatorForm


# class SiteListView(ListView):
#     model = Site


# class SiteCreateView(CreateView):
#     model = Site
#     form_class = SiteForm


# class SiteDetailView(DetailView):
#     model = Site


# class SiteUpdateView(UpdateView):
#     model = Site
#     form_class = SiteForm


# class SiteAccountListView(ListView):
#     model = SiteAccount


# class SiteAccountCreateView(CreateView):
#     model = SiteAccount
#     form_class = SiteAccountForm


# class SiteAccountDetailView(DetailView):
#     model = SiteAccount


# class SiteAccountUpdateView(UpdateView):
#     model = SiteAccount
#     form_class = SiteAccountForm


# class CreatorSiteAccountListView(ListView):
#     model = CreatorSiteAccount


# class CreatorSiteAccountCreateView(CreateView):
#     model = CreatorSiteAccount
#     form_class = CreatorSiteAccountForm


# class CreatorSiteAccountDetailView(DetailView):
#     model = CreatorSiteAccount


# class CreatorSiteAccountUpdateView(UpdateView):
#     model = CreatorSiteAccount
#     form_class = CreatorSiteAccountForm


# class SiteAccountChargeListView(ListView):
#     model = SiteAccountCharge


# class SiteAccountChargeCreateView(CreateView):
#     model = SiteAccountCharge
#     form_class = SiteAccountChargeForm


# class SiteAccountChargeDetailView(DetailView):
#     model = SiteAccountCharge


# class SiteAccountChargeUpdateView(UpdateView):
#     model = SiteAccountCharge
#     form_class = SiteAccountChargeForm


# class CreatorPhotoListView(ListView):
#     model = CreatorPhoto


# class CreatorPhotoCreateView(CreateView):
#     model = CreatorPhoto
#     form_class = CreatorPhotoForm


# class CreatorPhotoDetailView(DetailView):
#     model = CreatorPhoto


# class CreatorPhotoUpdateView(UpdateView):
#     model = CreatorPhoto
#     form_class = CreatorPhotoForm

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import render

# Create your views here.

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from rest_framework.decorators import APIView

from exchange_app.serializers import AdSerializer, ExchangeProposalSerializer
from .models import Ad, ExchangeProposal, ValidationError
from rest_framework import generics, viewsets, permissions

from .forms import AdCreateForm, AdFilterForm, ExchangeProposalForm, ProposalFilterForm
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
class AdListView(ListView):
    model = Ad
    template_name = 'ad/ad_list.html'
    context_object_name = 'ads'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        form = AdFilterForm(self.request.GET)
        
        if form.is_valid():
            search = form.cleaned_data.get('search')
            category = form.cleaned_data.get('category')
            condition = form.cleaned_data.get('condition')
            

            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) | 
                    Q(description__icontains=search)
                )
            
            if category:
                queryset = queryset.filter(category=category)
                
            if condition:
                queryset = queryset.filter(condition=condition)
                
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AdFilterForm(self.request.GET)
        return context
class AdCreateView(CreateView):
    model = Ad
    form_class = AdCreateForm  
    template_name = 'ad/ad_form.html'
    success_url = reverse_lazy('ad-list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "У вас нет возможности создавать объявления, пока вы не авторизованы.")
            return redirect('ad-list')  
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    

    
class AdUpdateView(UpdateView):
    model = Ad
    fields = ['title', 'description', 'image_url', 'category', 'condition']
    template_name = 'ad/ad_form.html'
    success_url = reverse_lazy('ad-list')
    
    def dispatch(self, request, *args, **kwargs):
        ad = self.get_object()
        if ad.user != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class AdDeleteView(LoginRequiredMixin, DeleteView):
    model = Ad
    success_url = reverse_lazy('ad-list')
    template_name = 'ad/ad_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):

        ad = self.get_object()
        if ad.user != request.user:
            raise PermissionDenied("Вы не можете удалить это объявление")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):

        return get_object_or_404(Ad, pk=self.kwargs['pk'])
class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'



def ad_list(request):
    ads = Ad.objects.all()

    category = request.GET.get('category')
    if category:
        ads = ads.filter(category=category)
    
    condition = request.GET.get('condition')
    if condition:
        ads = ads.filter(condition=condition)

    context = {
        'ads': ads,
        'category_choices': Ad.CATEGORY_CHOICES,
        'condition_choices': Ad.CONDITION_CHOICES,
    }
    return render(request, 'ad/ad_list.html', context)





class ExchangeProposalCreateView(LoginRequiredMixin, CreateView):
    model = ExchangeProposal
    form_class = ExchangeProposalForm
    template_name = 'exchange/proposal_form.html'
    success_url = reverse_lazy('proposal-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if form.instance.ad_sender.user != self.request.user:
            form.add_error('ad_sender', 'Неверное объявление-отправитель')
            return self.form_invalid(form)
        
        return super().form_valid(form)
class ExchangeProposalUpdateView(LoginRequiredMixin, UpdateView):
    model = ExchangeProposal
    fields = ['status']
    template_name = 'exchange/proposal_update.html'
    success_url = reverse_lazy('proposal-list')

    def get_queryset(self):
        return super().get_queryset().filter(ad_receiver__user=self.request.user)

class ExchangeProposalListView(LoginRequiredMixin, ListView):
    model = ExchangeProposal
    template_name = 'exchange/proposal_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        form = ProposalFilterForm(self.request.GET)

        if form.is_valid():
            data = form.cleaned_data

            if data.get('direction') == 'sent':
                queryset = queryset.filter(ad_sender__user=self.request.user)
            elif data.get('direction') == 'received':
                queryset = queryset.filter(ad_receiver__user=self.request.user)

            if data.get('status'):
                queryset = queryset.filter(status=data['status'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProposalFilterForm(self.request.GET)
        return context
    

class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ExchangeProposalViewSet(viewsets.ModelViewSet):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(ad_sender=self.request.user.ad)



class AdDeleteView(LoginRequiredMixin, DeleteView):
    model = Ad
    template_name = 'ad/ad_confirm_delete.html'  
    success_url = reverse_lazy('ad-list')  

    def dispatch(self, request, *args, **kwargs):
        ad = self.get_object()
        if ad.user != request.user:
            return HttpResponseForbidden("Вы не имеете права удалять это объявление")
        return super().dispatch(request, *args, **kwargs)
from django.urls import include, path
from fastapi_users import router
from rest_framework.routers import DefaultRouter
from .views import (
    AdListView,
    AdCreateView,
    AdUpdateView,
    AdDeleteView,
    AdViewSet,
    ExchangeProposalCreateView,
    ExchangeProposalListView,
    ExchangeProposalUpdateView,
    ExchangeProposalViewSet,
    SignUpView,
)
router = DefaultRouter()
router.register(r'api/ads', AdViewSet, basename='api-ads')
router.register(r'api/proposals', ExchangeProposalViewSet, basename='api-proposals')
urlpatterns = [
    path('', AdListView.as_view(), name='ad-list'),
    path('ad/new/', AdCreateView.as_view(), name='ad-create'),
    path('ad/<int:pk>/edit/', AdUpdateView.as_view(), name='ad-update'),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    path('proposals/', ExchangeProposalListView.as_view(), name='proposal-list'),
    path('proposals/create/', ExchangeProposalCreateView.as_view(), name='proposal-create'),
    path('proposals/<int:pk>/update/', ExchangeProposalUpdateView.as_view(), name='proposal-update'),
    path('', include(router.urls)),
    path('ads/<int:pk>/delete/', AdDeleteView.as_view(), name='ad-delete'),
]
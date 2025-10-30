from django.urls import path

from .views import IndexView, GroupDetailView, TeacherDetailView, SearchRedirectView, SearchSuggestionsView

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('search/', SearchRedirectView.as_view(), name='search_redirect'),
    path('search_suggestions/', SearchSuggestionsView.as_view(), name='search_suggestions'),
    path('groups/<slug:slug>/', GroupDetailView.as_view(), name='group_detail'),
    path('teachers/<slug:slug>/', TeacherDetailView.as_view(), name='teacher_detail'),
]
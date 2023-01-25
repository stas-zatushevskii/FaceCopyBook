from django.urls import path
from . import views
from .views import ProfileListView, ProfileDetailView

app_name = 'profiles'

urlpatterns = [
    path('', ProfileListView.as_view(), name='all-profiles'),
    path('myprofile', views.my_profile_view, name='my_profile'),
    path('my-invites/', views.invites_received, name='my_invites'),
    path('invite-profiles/', views.invite_profiles_list_view, name='invite-profiles'),
    path('send_invitation/', views.send_invitation, name='send_invitation'),
    path('delete_friend/', views.delete_friend, name='delete_friend'),
    path('<slug>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('my-invites/accept/', views.accept_invites, name='accept_invites'),
    path('my-invites/reject//', views.reject_invites, name='reject_invites'),
]

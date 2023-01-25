from .models import Profile, Relationship


def profile_pick(request):
    if request.user.is_authenticated:
        profile_object = Profile.objects.get(user=request.user)
        pic = profile_object.avatar
        return {'picture': pic}
    return {}


def invitation_received_num(request):
    if request.user.is_authenticated:
        profile_object = Profile.objects.get(user=request.user)
        invitations = Relationship.objects.invitation_received(profile_object).count()
        return {'invites_num': invitations}
    return {}
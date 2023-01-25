from django import forms
from .models import Post, Comment


class PostModelFrorm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))

    class Meta:
        model = Post
        fields = ('text', 'image')


class CommentModelFrorm(forms.ModelForm):
    text = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Add a comment...'}))

    class Meta:
        model = Comment
        fields = ('text',)

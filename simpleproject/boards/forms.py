from django import forms
from .models import *


class NewTopicForm(forms.ModelForm):
    """
    Cоздание нового топика и одновременно поста
    """
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'Post message here'}
        ),
        max_length=4000,
        help_text='The max length of the text is 4000.'
    )

    class Meta:
        model = Topic  # It’s a ModelForm associated with the Topic model
        fields = ['subject', 'message']


class PostForm(forms.ModelForm):
    """
    Reply post
    """
    class Meta:
        model = Post
        fields = ['message', ]


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

# for posts counting
from django.db.models import Count

# My stuff
from .models import *
from .forms import *

# Generic Class-Based View Modules
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.utils import timezone

# Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Generic Class-Based View
class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'boards/home.html'

# # Function-Based View
# def home(request):
#     boards = Board.objects.all()
#     return render(request, 'home.html', {'boards': boards})


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'boards/topics.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('board_id'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset

# # Function-Based View
# def board_topics(request, board_id):
#     board = get_object_or_404(Board, bo=board_id)
#     queryset = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
#     page = request.GET.get('page', 1)
#
#     paginator = Paginator(queryset, 5)
#
#     try:
#         topics = paginator.page(page)
#     except PageNotAnInteger:  # fallback to the first page
#         topics = paginator.page(1)
#     except EmptyPage:  # fallback to the last page
#         topics = paginator.page(paginator.num_pages)
#
#     return render(request, 'boards/topics.html', {'board': board, 'topics': topics})


@login_required
def new_topic(request, board_id):
    """
    1) If the user isn’t logged in, redirect to settings.LOGIN_URL, passing the current absolute path in the query string
    2) If the user is logged in, execute the view normally. The view code is free to assume the user is logged in.
    """
    board = get_object_or_404(Board, pk=board_id)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            print(Post.message, Post.topic)
            return redirect('topic_posts', board_id=board_id, topic_id=topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'boards/new_topic.html', {'board': board, 'form': form})


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'boards/topic_posts.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):

        session_key = 'viewed_topic_{}'.format(self.topic.pk)  # <-- here
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True

        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('board_id'), pk=self.kwargs.get('topic_id'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset

# # Function-based view
# def topic_posts(request, board_id, topic_id):
#     topic = get_object_or_404(Topic, board__pk=board_id, pk=topic_id)
#     topic.views += 1
#     topic.save()
#     return render(request, 'boards/topic_posts.html', {'topic': topic})


@login_required
def reply_topic(request, board_id, topic_id):
    topic = get_object_or_404(Topic, board__pk=board_id, pk=topic_id)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()

            return redirect('topic_posts', board_id=board_id, topic_id=topic_id)
        else:  # if from.is_valid() is False
            return render(request, 'boards/reply_topic.html', {'topic': topic, 'form': form})
    else:
        form = PostForm()
        return render(request, 'boards/reply_topic.html', {'topic': topic, 'form': form})


# Generic Class-Based View
class NewPostView(CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('post_list')
    template_name = 'new_post.html'

# # Class-Based View
# class NewPostView(View):
#     def render(self, request):
#         return render(request, 'new_post.html', {'form': self.form})
#
#     def post(self, request):
#         self.form = PostForm(request.POST)
#         if self.form.is_valid():
#             self.form.save()
#             return redirect('post_list')
#         return self.render(request)
#
#     def get(self, request):
#         self.form = PostForm()
#         return self.render(request)

# # Function-based view
# def new_post(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('post_list')
#     else:
#         form = PostForm()
#     return render(request, 'new_post.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'boards/edit_post.html'
    pk_url_kwarg = 'post_id'  # the name of the keyword argument used to retrieve the Post object.
    context_object_name = 'post'  # вместо object.params будет post.param

    # def get_context_data(self, **kwargs):
    #     print(self.kwargs)  # просто, чтобы в консольке видеть все
    #     return super().get_context_data(**kwargs)
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', board_id=post.topic.board.pk, topic_id=post.topic.pk)

#
# @method_decorator(login_required, name='dispatch')
# class PostDeleteView(DeleteView):
#     model = Post
#     pk_url_kwarg = 'post_id'
#     success_url = reverse_lazy('topic_posts')
#
#
#


@login_required()
def delete_post(request, board_id, topic_id, post_id):
    new_to_delete = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        form = DeletePostForm(request.POST, instance=new_to_delete)

        if form.is_valid():  # checks CSRF
            new_to_delete.delete()
            return redirect('topic_posts', board_id=board_id, topic_id=topic_id)
    else:
        print('hi')
        pass
    #     form = DeletePostForm(instance=new_to_delete)
    # template_vars = {'form': form}
    # return render(request, 'news/deleteNew.html', template_vars)

from django.urls import reverse, resolve
from django.test import TestCase

from ..views import *
from ..models import *
from ..forms import NewTopicForm

from django.contrib.auth.models import User


class LoginRequiredNewTopicTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', description='Django board.')
        self.url = reverse('new_topic', kwargs={'board_id': 1})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))


class NewTopicTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Test board', description='Lets test this one!')
        User.objects.create_user(username='john', email='john@doe.com', password='secret_password')
        self.client.login(username='john', password='123')

    def test_new_topic_view_success_status_code(self):
        """check if the request to the view is successful"""

        url = reverse('new_topic', kwargs={'board_id': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_new_topic_view_not_found_status_code(self):
        """check if the view is raising a 404 error when the Board does not exist"""

        url = reverse('new_topic', kwargs={'board_id': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_new_topic_url_resolves_new_topic_view(self):
        """check if the right view is being used"""

        view = resolve('/boards/1/new/')
        self.assertEquals(view.func, new_topic)

    def test_new_topic_view_contains_link_back_to_board_topics_view(self):
        """ensure the navigation back to the list of topics"""

        new_topic_url = reverse('new_topic', kwargs={'board_id': 1})  # запрос на 'new_topic' url
        board_topics_url = reverse('board_topics', kwargs={'board_id': 1})  # запрос на 'board_topics' url
        response = self.client.get(new_topic_url)
        self.assertContains(response, 'href="{}"'.format(board_topics_url))

    def test_csrf(self):
        """make sure our HTML contains the CSRF Token."""

        url = reverse('new_topic', kwargs={'board_id': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_new_topic_valid_post_data(self):
        """sends a valid combination of data and check if the view created a Topic instance and a Post instance."""

        url = reverse('new_topic', kwargs={'board_id': 1})
        data = {
            'subject': 'Test title',
            'message': 'Test message'
        }
        self.client.post(url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test_new_topic_invalid_post_data(self):
        """
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        """

        url = reverse('new_topic', kwargs={'board_id': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)  # make sure the form is showing errors when the data is invalid.

    def test_new_topic_invalid_post_data_empty_fields(self):
        """
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        """

        url = reverse('new_topic', kwargs={'board_id': 1})
        data = {
            'subject': '',
            'message': ''
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())

    def test_contains_form(self):
        """checking if the form instance in the context data is a NewTopicForm"""

        url = reverse('new_topic', kwargs={'board_id': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)  # так как form -- экземпляр нашего класса NewTopicForm


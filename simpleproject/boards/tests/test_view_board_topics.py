from django.urls import reverse, resolve
from django.test import TestCase
from ..views import *
from ..models import *


class BoardTopicsTests(TestCase):
    def setUp(self):
        """"To run the tests Django creates a new database on the fly, applies all the model migrations,
        runs the tests, and when done, destroys the testing database."""

        Board.objects.create(name='Test board', description='Lets test this one!')

    def test_board_topics_view_success_status_code(self):
        """check if the request to the view is successful"""

        url = reverse('board_topics', kwargs={'board_id': 1})  # url вида boards/1 из urls.py по name='board_topics'
        response = self.client.get(url)  # клиент зашел по нашему url
        self.assertEquals(response.status_code, 200)

    def test_board_topics_view_not_found_status_code(self):
        """check if the view is raising a 404 error when the Board does not exist"""

        url = reverse('board_topics', kwargs={'board_id': 99})  # url вида boards/99 из urls.py по name='board_topics'
        response = self.client.get(url)  # клиент зашел по нашему url
        self.assertEquals(response.status_code, 404)

    def test_board_topics_url_resolves_board_topics_view(self):
        """check if the right view is being used"""

        view = resolve('/boards/1/')  # по сути автоматический запрос на этот путь
        self.assertEquals(view.func, board_topics)   # вызвалась ли по этому view эта функция?

    def test_board_topics_view_contains_link_back_to_homepage(self):
        """ensure the navigation back to the list of topics"""

        board_topics_url = reverse('board_topics', kwargs={'board_id': 1})
        response = self.client.get(board_topics_url)
        homepage_url = reverse('homepage')
        self.assertContains(response, 'href="{}"'.format(homepage_url))

    def test_board_topics_view_contains_navigation_links(self):
        """make sure the user can reach the New topic view from boards page"""
        board_topics_url = reverse('board_topics', kwargs={'board_id': 1})
        homepage_url = reverse('homepage')
        new_topic_url = reverse('new_topic', kwargs={'board_id': 1})

        response = self.client.get(board_topics_url)

        self.assertContains(response, 'href="{}"'.format(homepage_url))
        self.assertContains(response, 'href="{}"'.format(new_topic_url))
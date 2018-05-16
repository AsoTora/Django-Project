from django.urls import reverse, resolve
from django.test import TestCase

from ..views import *
from ..models import *


class HomeTests(TestCase):
    """To test run: python manage.py test --verbosity=0/1/2"""

    def setUp(self):
        """To run the tests Django creates a new database on the fly, applies all the model migrations,
        runs the tests, and when done, destroys the testing database.
           And now we are going to need a Board instance and also we moved the url and response to the setUp,
        so we can reuse the same response in the new test."""

        self.board = Board.objects.create(name='Django', description='Django board.')
        url = reverse('homepage')  # получает нужный url из файла urls.py по его имени
        self.response = self.client.get(url)

    def test_home_view_status_code(self):
        url = reverse('homepage')  # получает нужный url из файла urls.py по его имени
        response = self.client.get(url)  # клиент зашел по нашему url
        self.assertEquals(response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        view = resolve('/')  # по сути автоматический запрос на этот путь
        print('Checking the', view.url_name, 'url')
        self.assertEquals(view.func.view_class, BoardListView)  # вызвалась ли по этому view эта функция?

    def test_home_view_contains_link_to_topics_page(self):
        """test if the response body contains a given text. """

        board_topics_url = reverse('board_topics', kwargs={'board_id': self.board.pk})
        self.assertContains(self.response, 'href="{}"'.format(board_topics_url))  # has the resp: href="/boards/1/" ?
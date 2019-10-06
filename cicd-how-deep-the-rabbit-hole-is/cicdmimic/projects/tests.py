from django.test import TestCase


class MyFirstTest(TestCase):

    def test_success(self):
        self.assertEqual(2, 2)

from django.test import TestCase


class LoginCsrfTests(TestCase):
    def test_login_get_sets_csrf_cookie(self):
        response = self.client.get('/authentication/login/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('csrftoken', response.cookies)

    def test_invalid_csrf_redirects_back_to_login(self):
        client = self.client_class(enforce_csrf_checks=True)
        response = client.post(
            '/authentication/login/',
            {
                'username_or_email': '26100001',
                'password': '26100001',
                'csrfmiddlewaretoken': 'invalid-token',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/authentication/login/')

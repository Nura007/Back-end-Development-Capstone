from datetime import date
from unittest.mock import Mock, patch
import requests
from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Concert, ConcertAttending


class ApplicationTests(TestCase):
    def setUp(self):
        self.concert = Concert.objects.create(concert_name="Test concert", duration=2, city="London", date=date(2027, 1, 1))

    def test_public_pages_and_admin_login(self):
        for path in ("/", "/concerts/", "/admin/login/"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)
        self.assertContains(self.client.get("/concerts/"), "Test concert")

    def test_signup_login_and_post_logout(self):
        data = {"username": "listener", "password1": "Test-password-129!", "password2": "Test-password-129!"}
        self.assertRedirects(self.client.post("/signup/", data), "/")
        self.assertTrue(get_user_model().objects.get(username="listener").check_password(data["password1"]))
        self.assertEqual(self.client.get("/logout/").status_code, 405)
        self.assertRedirects(self.client.post("/logout/"), "/")
        self.assertRedirects(self.client.post("/login/", {"username": "listener", "password": data["password1"]}), "/")

    def test_rsvp_requires_login_and_updates_only_current_user(self):
        payload = {"concert_id": self.concert.pk, "attendee_choice": "Attending"}
        self.assertEqual(self.client.post("/concert_attendee/", payload).status_code, 302)
        self.assertEqual(ConcertAttending.objects.count(), 0)
        user = get_user_model().objects.create_user("listener", password="Test-password-129!")
        self.client.force_login(user)
        self.client.post("/concert_attendee/", payload)
        self.client.post("/concert_attendee/", {**payload, "attendee_choice": "Not Attending"})
        self.assertEqual(ConcertAttending.objects.count(), 1)
        self.assertEqual(ConcertAttending.objects.get().attending, "Not Attending")
        self.assertEqual(self.client.post("/concert_attendee/", {**payload, "attendee_choice": "invalid"}).status_code, 400)

    @patch("concert.views.requests.get")
    def test_remote_song_lyrics_are_escaped(self, get):
        response = Mock()
        response.json.return_value = {"songs": [{"id": 1, "title": "Test song", "lyrics": "<script>unsafe</script>"}]}
        get.return_value = response
        page = self.client.get("/songs/")
        self.assertContains(page, "Test song")
        self.assertContains(page, "&lt;script&gt;unsafe&lt;/script&gt;")
        self.assertNotContains(page, "<script>unsafe</script>")

    @patch("concert.views.requests.get", side_effect=requests.ConnectionError())
    def test_service_outage_is_reported(self, get):
        self.assertEqual(self.client.get("/songs/").status_code, 503)
        self.assertEqual(self.client.get("/photos/").status_code, 503)

    @patch("concert.views.requests.get")
    def test_photos_pagination(self, get):
        response = Mock()
        response.json.return_value = [{"id": n, "event_city": f"City{n}", "pic_url": "https://example.org/photo.jpg"} for n in (1, 2)]
        get.return_value = response
        first = self.client.get("/photos/")
        self.assertContains(first, "City1")
        self.assertNotContains(first, "City2")
        self.assertContains(self.client.get("/photos/?page=2"), "City2")

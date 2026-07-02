from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Bounty

class WildWestAuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('auth_register')
        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        self.user_data = {
            'username': 'WyattEarp',
            'password': 'StrongPassword123!'
        }

    def test_user_registration_success(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='WyattEarp').exists())
        
        # Test duplicate username rejection
        response2 = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_and_refresh(self):
        # Register user
        self.client.post(self.register_url, self.user_data, format='json')
        
        # Login
        response = self.client.post(self.login_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        refresh_token = response.data['refresh']

        # Refresh token exchange
        response_refresh = self.client.post(self.refresh_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(response_refresh.status_code, status.HTTP_200_OK)
        self.assertIn('access', response_refresh.data)


class BountyAPITests(APITestCase):
    def setUp(self):
        # Clear cache before each test
        cache.clear()
        
        # Register and log in User A (Sheriff)
        self.user_a = User.objects.create_user(username='sheriff', password='Password123!')
        login_resp_a = self.client.post(reverse('token_obtain_pair'), {'username': 'sheriff', 'password': 'Password123!'}, format='json')
        self.token_a = login_resp_a.data['access']

        # Register and log in User B (Outlaw)
        self.user_b = User.objects.create_user(username='billy_the_kid', password='Password123!')
        login_resp_b = self.client.post(reverse('token_obtain_pair'), {'username': 'billy_the_kid', 'password': 'Password123!'}, format='json')
        self.token_b = login_resp_b.data['access']

        # URLs
        self.bounties_list_url = reverse('bounty-list')

        # Create a bounty for User A
        self.bounty_a = Bounty.objects.create(
            target_name="Jesse James",
            reward=5000.00,
            status="wanted",
            owner=self.user_a,
            danger_level="high",
            last_seen_at="Missouri"
        )

    def set_auth_header(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_anonymous_access_denied(self):
        # List
        response = self.client.get(self.bounties_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Retrieve
        detail_url = reverse('bounty-detail', kwargs={'pk': self.bounty_a.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bounty_creation_and_ownership(self):
        self.set_auth_header(self.token_a)
        data = {
            "target_name": "Butch Cassidy",
            "reward": 3000.00,
            "status": "wanted",
            "danger_level": "high",
            "last_seen_at": "Wyoming"
        }
        response = self.client.post(self.bounties_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['target_name'], "Butch Cassidy")
        self.assertEqual(response.data['owner'], self.user_a.username)

        # Verify it is stored under user_a
        created_bounty = Bounty.objects.get(target_name="Butch Cassidy")
        self.assertEqual(created_bounty.owner, self.user_a)

    def test_ownership_isolation(self):
        # Logged in as User B (billy_the_kid)
        self.set_auth_header(self.token_b)

        # Attempt to list (should return 200 but empty list since User B has no bounties)
        response = self.client.get(self.bounties_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        # Attempt to retrieve User A's bounty (should return 404 for security)
        detail_url = reverse('bounty-detail', kwargs={'pk': self.bounty_a.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Attempt to update User A's bounty (should return 404)
        response = self.client.patch(detail_url, {'status': 'captured'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Attempt to delete User A's bounty (should return 404)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_caching_and_invalidation(self):
        self.set_auth_header(self.token_a)
        cache_key_list = f"user_{self.user_a.id}_bounties_list"
        cache_key_detail = f"user_{self.user_a.id}_bounty_{self.bounty_a.id}"

        # Cache should be empty initially
        self.assertIsNone(cache.get(cache_key_list))
        self.assertIsNone(cache.get(cache_key_detail))

        # Retrieve list to populate list cache
        response_list = self.client.get(self.bounties_list_url)
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(cache.get(cache_key_list))

        # Retrieve detail to populate detail cache
        detail_url = reverse('bounty-detail', kwargs={'pk': self.bounty_a.id})
        response_detail = self.client.get(detail_url)
        self.assertEqual(response_detail.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(cache.get(cache_key_detail))

        # Create a new bounty -> both caches should invalidate
        data = {
            "target_name": "Sundance Kid",
            "reward": 2500.00,
            "status": "wanted"
        }
        self.client.post(self.bounties_list_url, data, format='json')
        self.assertIsNone(cache.get(cache_key_list))
        # Note: creating a new bounty doesn't delete detail cache of another bounty, but list cache must be cleared.
        # Let's verify detail invalidation on update:
        
        # Populate detail cache again
        self.client.get(detail_url)
        self.assertIsNotNone(cache.get(cache_key_detail))

        # Update bounty -> detail cache should invalidate
        self.client.patch(detail_url, {'status': 'captured'}, format='json')
        self.assertIsNone(cache.get(cache_key_detail))
        self.assertIsNone(cache.get(cache_key_list))

# Django Unchained REST API (Bounty Board)

Welcome to the Wild West. This repository hosts a robust, secure, and performant REST API for keeping track of a frontier town's **Bounty Board**. Built using **Django** and **Django REST Framework (DRF)**.

## Selected Frontier Concept
- **🎯 Bounty Board**: We run the town's bounty office. Outlaws get put up on the board with a cash reward for whoever brings them in. 

---

## Features & Defenses

### 1. Robust Access Control & Ownership Isolation
- **Authentication**: Secured using standard JSON Web Token (JWT) auth via `djangorestframework-simplejwt`.
- **Ownership Scope**: A logged-in user can **only** read, edit, or delete bounties that they own.
- **Defending Against ID Harvesting**: Instead of returning a `403 Forbidden` if a user tries to access another user's bounty ID, the API returns a `404 Not Found` (by scoping `get_queryset()` to `request.user`). This denies outlaws the ability to even scan if a bounty ID exists.

### 2. Rate Limiting (Throttling)
- **Burst Control on Auth**: The register, login, and refresh endpoints are throttled to a max of **10 requests per minute** to mitigate login brute-forcing and registration spam.
- **IP / Anonymous Limit**: General anonymous traffic is restricted to **30 requests per minute**.
- **Authenticated Limit**: Logged-in users have a standard limit of **100 requests per minute**.

### 3. Smart Caching & Invalidation
- **User-Isolated Cache**: Read-heavy endpoints (bounty list and detail views) are cached using Django's `LocMemCache`. The cache keys are namespaced by the user ID (e.g., `user_<user_id>_bounties_list`). This completely prevents info leaks (User A will never see User B's cached records).
- **Auto Invalidation**: Writing to the database via creation, updates, or deletion instantly invalidates that user's cache, ensuring they always get fresh data on subsequent reads.

---

## API Endpoints Reference

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/auth/register/` | Register a new citizen account | Public |
| **POST** | `/api/auth/login/` | Obtain JWT access & refresh tokens | Public |
| **POST** | `/api/auth/refresh/` | Obtain a new access token from a refresh token | Public |
| **GET** | `/api/bounties/` | List all bounties belonging to the user (cached) | Authenticated |
| **POST** | `/api/bounties/` | Post a new outlaw bounty on the board | Authenticated |
| **GET** | `/api/bounties/<id>/` | View a single bounty details (cached) | Auth + Owner |
| **PUT** | `/api/bounties/<id>/` | Fully update a bounty's details | Auth + Owner |
| **PATCH** | `/api/bounties/<id>/` | Partially update a bounty's details | Auth + Owner |
| **DELETE** | `/api/bounties/<id>/` | Delete a bounty from the board | Auth + Owner |

### Required JSON Payload Structure for Bounties
```json
{
  "target_name": "Jesse James",
  "reward": 5000.00,
  "status": "wanted",
  "danger_level": "high",
  "last_seen_at": "Missouri"
}
```

---

## Installation & Running Locally

Ensure you have Python 3 installed. Follow these commands to set up:

1. **Clone & Navigate** to the project folder:
   ```powershell
   cd LS26_WebDev
   ```

2. **Create and Activate a Virtual Environment**:
   ```powershell
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   ```

3. **Install Requirements**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run Database Migrations**:
   ```powershell
   python manage.py migrate
   ```

5. **Run the Test Suite**:
   Verify everything passes:
   ```powershell
   python manage.py test
   ```

6. **Start the server**:
   ```powershell
   python manage.py runserver
   ```
   The API will now be running on `http://127.0.0.1:8000/`.

---

## Code Overview
- [settings.py](file:///c:/Users/Shiva%20Upman/Downloads/LS26_WebDev/django_unchained/settings.py): Application configuration, REST Framework settings, SimpleJWT config, and LocMemCache setup.
- [models.py](file:///c:/Users/Shiva%20Upman/Downloads/LS26_WebDev/bounties/models.py): Defines the `Bounty` DB model containing target_name, reward, status, owner, danger_level, last_seen_at, and timestamps.
- [serializers.py](file:///c:/Users/Shiva%20Upman/Downloads/LS26_WebDev/bounties/serializers.py): Validations and mappings for user registrations and bounty details.
- [views.py](file:///c:/Users/Shiva%20Upman/Downloads/LS26_WebDev/bounties/views.py): Handles endpoint logic, filters objects by owner, and manages the caching/invalidation lifecycles.
- [tests.py](file:///c:/Users/Shiva%20Upman/Downloads/LS26_WebDev/bounties/tests.py): Suite verifying authentication flows, access control logic, and cache invalidation.

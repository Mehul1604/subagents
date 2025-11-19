"""
Comprehensive test suite for authentication module and API endpoints.

Tests cover:
- Login endpoint (valid, invalid, validation errors)
- Register endpoint (successful, duplicate username, invalid email)
- Logout endpoint (successful logout, token invalidation)
- Users endpoint (without auth, with admin auth, with non-admin auth)
- Password hashing and security features
- Token validation
- Edge cases and error handling
"""

import pytest
from fastapi.testclient import TestClient
from main import app, user_credentials, active_sessions, data_store


@pytest.fixture(autouse=True)
def reset_state():
    """Reset application state before each test"""
    # Clear all in-memory storage
    user_credentials.clear()
    active_sessions.clear()
    data_store.clear()
    yield
    # Clean up after test
    user_credentials.clear()
    active_sessions.clear()
    data_store.clear()


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def admin_token(client):
    """Create an admin user and return authentication token"""
    # Register admin user
    response = client.post(
        "/register",
        json={
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    return data["token"]


@pytest.fixture
def regular_user_token(client):
    """Create a regular user and return authentication token"""
    # Register regular user
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    return data["token"]


# ============================================================================
# LOGIN ENDPOINT TESTS
# ============================================================================

class TestLogin:
    """Test suite for POST /login endpoint"""

    def test_login_with_valid_credentials(self, client):
        """Test login with correct username and password"""
        # First register a user
        client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123"
            }
        )

        # Now try to login
        response = client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Login successful"
        assert data["username"] == "testuser"
        assert data["token"] is not None
        assert len(data["token"]) == 36  # UUID format

    def test_login_with_invalid_username(self, client):
        """Test login with non-existent username"""
        response = client.post(
            "/login",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["message"] == "Invalid username or password"
        assert data["token"] is None

    def test_login_with_invalid_password(self, client):
        """Test login with incorrect password"""
        # Register a user first
        client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123"
            }
        )

        # Try to login with wrong password
        response = client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["message"] == "Invalid username or password"
        assert data["token"] is None

    def test_login_with_missing_username(self, client):
        """Test login with missing username field"""
        response = client.post(
            "/login",
            json={
                "password": "password123"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_login_with_missing_password(self, client):
        """Test login with missing password field"""
        response = client.post(
            "/login",
            json={
                "username": "testuser"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_login_with_short_username(self, client):
        """Test login with username shorter than minimum length"""
        response = client.post(
            "/login",
            json={
                "username": "ab",  # Less than 3 characters
                "password": "password123"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_login_with_short_password(self, client):
        """Test login with password shorter than minimum length"""
        response = client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "12345"  # Less than 6 characters
            }
        )

        assert response.status_code == 422  # Validation error

    def test_login_creates_session_token(self, client):
        """Test that successful login creates an active session"""
        # Register a user
        client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123"
            }
        )

        # Clear sessions to isolate login test
        active_sessions.clear()

        # Login
        response = client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        token = data["token"]

        # Verify session was created
        assert token in active_sessions
        assert active_sessions[token] == "testuser"


# ============================================================================
# REGISTER ENDPOINT TESTS
# ============================================================================

class TestRegister:
    """Test suite for POST /register endpoint"""

    def test_register_with_valid_data(self, client):
        """Test successful user registration"""
        response = client.post(
            "/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Registration successful"
        assert data["username"] == "newuser"
        assert data["token"] is not None
        assert len(data["token"]) == 36  # UUID format

    def test_register_creates_user_credentials(self, client):
        """Test that registration creates user credentials"""
        response = client.post(
            "/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 200
        # Verify user was added to credentials store
        assert "newuser" in user_credentials

    def test_register_hashes_password(self, client):
        """Test that registration hashes passwords using bcrypt"""
        response = client.post(
            "/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 200
        # Verify password is hashed (bcrypt hashes start with $2b$)
        stored_hash = user_credentials["newuser"]
        assert stored_hash.startswith("$2b$")
        assert stored_hash != "password123"  # Not stored in plaintext

    def test_register_with_duplicate_username(self, client):
        """Test registration with an already existing username"""
        # Register first user
        client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test1@example.com",
                "password": "password123"
            }
        )

        # Try to register with same username
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test2@example.com",
                "password": "password456"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["message"] == "Username already exists"
        assert data["token"] is None

    def test_register_with_invalid_email(self, client):
        """Test registration with invalid email format"""
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "invalid-email",  # Missing @ and domain
                "password": "password123"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_register_with_missing_email(self, client):
        """Test registration with missing email field"""
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_register_with_short_username(self, client):
        """Test registration with username shorter than minimum length"""
        response = client.post(
            "/register",
            json={
                "username": "ab",  # Less than 3 characters
                "email": "test@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_register_with_short_password(self, client):
        """Test registration with password shorter than minimum length"""
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "12345"  # Less than 6 characters
            }
        )

        assert response.status_code == 422  # Validation error

    def test_register_creates_session_immediately(self, client):
        """Test that successful registration creates an active session"""
        response = client.post(
            "/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        token = data["token"]

        # Verify session was created
        assert token in active_sessions
        assert active_sessions[token] == "newuser"


# ============================================================================
# LOGOUT ENDPOINT TESTS
# ============================================================================

class TestLogout:
    """Test suite for POST /logout endpoint"""

    def test_logout_with_valid_token(self, client, regular_user_token):
        """Test successful logout with valid token"""
        # Verify token exists before logout
        assert regular_user_token in active_sessions

        response = client.post(
            "/logout",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logged out successfully"

        # Verify token was removed from active sessions
        assert regular_user_token not in active_sessions

    def test_logout_without_token(self, client):
        """Test logout without providing a token"""
        response = client.post("/logout")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logged out successfully"

    def test_logout_with_invalid_token(self, client):
        """Test logout with an invalid token"""
        response = client.post(
            "/logout",
            headers={"Authorization": "Bearer invalid-token-12345"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logged out successfully"

    def test_logout_invalidates_token(self, client, regular_user_token):
        """Test that logout invalidates the token for future requests"""
        # Logout
        client.post(
            "/logout",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )

        # Try to use the token after logout
        response = client.get(
            "/users",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )

        assert response.status_code == 401  # Unauthorized

    def test_logout_with_malformed_authorization_header(self, client):
        """Test logout with malformed Authorization header"""
        response = client.post(
            "/logout",
            headers={"Authorization": "InvalidFormat token123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logged out successfully"


# ============================================================================
# USERS ENDPOINT TESTS
# ============================================================================

class TestUsers:
    """Test suite for GET /users endpoint"""

    def test_users_without_authentication(self, client):
        """Test accessing /users endpoint without authentication"""
        response = client.get("/users")

        assert response.status_code == 401  # Unauthorized
        data = response.json()
        assert data["detail"] == "Not authenticated"

    def test_users_with_invalid_token(self, client):
        """Test accessing /users endpoint with invalid token"""
        response = client.get(
            "/users",
            headers={"Authorization": "Bearer invalid-token-12345"}
        )

        assert response.status_code == 401  # Unauthorized
        data = response.json()
        assert data["detail"] == "Invalid or expired token"

    def test_users_with_admin_authentication(self, client, admin_token):
        """Test accessing /users endpoint as admin"""
        response = client.get(
            "/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "count" in data
        assert isinstance(data["users"], list)
        assert data["count"] == len(data["users"])
        assert "admin" in data["users"]

    def test_users_with_non_admin_authentication(self, client, regular_user_token):
        """Test accessing /users endpoint as non-admin user"""
        response = client.get(
            "/users",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )

        assert response.status_code == 403  # Forbidden
        data = response.json()
        assert data["detail"] == "Forbidden: Admin access required"

    def test_users_does_not_expose_passwords(self, client, admin_token):
        """Test that /users endpoint does not expose password hashes"""
        response = client.get(
            "/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response only contains usernames, not passwords
        assert "users" in data
        assert isinstance(data["users"], list)
        for username in data["users"]:
            assert isinstance(username, str)
            # Make sure it's just a username, not a dict with password
            assert not isinstance(username, dict)

    def test_users_without_bearer_prefix(self, client, admin_token):
        """Test accessing /users endpoint without 'Bearer' prefix"""
        response = client.get(
            "/users",
            headers={"Authorization": admin_token}
        )

        assert response.status_code == 401  # Unauthorized
        data = response.json()
        assert data["detail"] == "Not authenticated"


# ============================================================================
# SECURITY AND PASSWORD HASHING TESTS
# ============================================================================

class TestPasswordSecurity:
    """Test suite for password hashing and security features"""

    def test_password_is_hashed_with_bcrypt(self, client):
        """Test that passwords are hashed using bcrypt"""
        client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123"
            }
        )

        stored_hash = user_credentials["testuser"]
        # Bcrypt hashes start with $2b$ or $2a$
        assert stored_hash.startswith("$2b$") or stored_hash.startswith("$2a$")

    def test_password_verification_works(self, client):
        """Test that password verification works correctly"""
        # Register user
        client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123"
            }
        )

        # Login with correct password
        response = client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_different_passwords_produce_different_hashes(self, client):
        """Test that same password hashed twice produces different hashes (due to salt)"""
        client.post(
            "/register",
            json={
                "username": "user1",
                "email": "user1@example.com",
                "password": "password123"
            }
        )

        client.post(
            "/register",
            json={
                "username": "user2",
                "email": "user2@example.com",
                "password": "password123"
            }
        )

        hash1 = user_credentials["user1"]
        hash2 = user_credentials["user2"]

        # Even though passwords are the same, hashes should be different
        assert hash1 != hash2


# ============================================================================
# TOKEN VALIDATION TESTS
# ============================================================================

class TestTokenValidation:
    """Test suite for token validation"""

    def test_token_is_uuid_format(self, client):
        """Test that generated tokens are valid UUIDs"""
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        token = data["token"]

        # UUID format: 8-4-4-4-12 hexadecimal characters
        assert len(token) == 36
        assert token.count('-') == 4

    def test_token_is_unique_per_session(self, client):
        """Test that each login generates a unique token"""
        # Register user
        client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123"
            }
        )

        # Login multiple times
        response1 = client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )

        response2 = client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )

        token1 = response1.json()["token"]
        token2 = response2.json()["token"]

        # Tokens should be different
        assert token1 != token2

    def test_token_validates_correctly(self, client, admin_token):
        """Test that valid tokens are accepted"""
        response = client.get(
            "/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200


# ============================================================================
# EDGE CASES AND ERROR HANDLING TESTS
# ============================================================================

class TestEdgeCases:
    """Test suite for edge cases and error handling"""

    def test_register_with_very_long_username(self, client):
        """Test registration with username at maximum length"""
        response = client.post(
            "/register",
            json={
                "username": "a" * 50,  # Maximum allowed length
                "email": "test@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 200

    def test_register_with_username_exceeding_max_length(self, client):
        """Test registration with username exceeding maximum length"""
        response = client.post(
            "/register",
            json={
                "username": "a" * 51,  # Exceeds maximum length
                "email": "test@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_register_with_very_long_password(self, client):
        """Test registration with password at maximum safe length (72 bytes for bcrypt)"""
        # bcrypt has a 72-byte limit, so test with 72 characters
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "a" * 72  # Bcrypt maximum safe length
            }
        )

        assert response.status_code == 200

    def test_register_with_password_exceeding_max_length(self, client):
        """Test registration with password exceeding maximum length"""
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "a" * 101  # Exceeds maximum length
            }
        )

        assert response.status_code == 422  # Validation error

    def test_login_with_empty_credentials(self, client):
        """Test login with empty username and password"""
        response = client.post(
            "/login",
            json={
                "username": "",
                "password": ""
            }
        )

        assert response.status_code == 422  # Validation error

    def test_register_with_special_characters_in_username(self, client):
        """Test registration with special characters in username"""
        response = client.post(
            "/register",
            json={
                "username": "test_user-123",
                "email": "test@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 200

    def test_register_with_special_characters_in_password(self, client):
        """Test registration with special characters in password"""
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "P@ssw0rd!#$%"
            }
        )

        assert response.status_code == 200

    def test_multiple_simultaneous_sessions_for_same_user(self, client):
        """Test that a user can have multiple active sessions"""
        # Register user
        client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123"
            }
        )

        # Create multiple sessions
        response1 = client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )

        response2 = client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )

        token1 = response1.json()["token"]
        token2 = response2.json()["token"]

        # Both tokens should be valid
        assert token1 in active_sessions
        assert token2 in active_sessions


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestAuthenticationFlow:
    """Test complete authentication flows"""

    def test_complete_registration_login_logout_flow(self, client):
        """Test complete user journey: register -> login -> logout"""
        # 1. Register
        register_response = client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123"
            }
        )
        assert register_response.status_code == 200
        register_token = register_response.json()["token"]

        # 2. Logout from registration session
        logout_response = client.post(
            "/logout",
            headers={"Authorization": f"Bearer {register_token}"}
        )
        assert logout_response.status_code == 200

        # 3. Login again
        login_response = client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )
        assert login_response.status_code == 200
        login_token = login_response.json()["token"]

        # 4. Verify token works
        assert login_token in active_sessions

        # 5. Logout
        final_logout = client.post(
            "/logout",
            headers={"Authorization": f"Bearer {login_token}"}
        )
        assert final_logout.status_code == 200
        assert login_token not in active_sessions

    def test_admin_access_control_flow(self, client):
        """Test admin access control for /users endpoint"""
        # 1. Create admin user
        admin_response = client.post(
            "/register",
            json={
                "username": "admin",
                "email": "admin@example.com",
                "password": "admin123"
            }
        )
        admin_token = admin_response.json()["token"]

        # 2. Create regular user
        user_response = client.post(
            "/register",
            json={
                "username": "regular",
                "email": "regular@example.com",
                "password": "password123"
            }
        )
        user_token = user_response.json()["token"]

        # 3. Admin can access /users
        admin_access = client.get(
            "/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert admin_access.status_code == 200

        # 4. Regular user cannot access /users
        user_access = client.get(
            "/users",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert user_access.status_code == 403

    def test_case_sensitive_username_handling(self, client):
        """Test that usernames are case-sensitive"""
        # Register with lowercase
        client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123"
            }
        )

        # Try to register with uppercase
        response = client.post(
            "/register",
            json={
                "username": "TestUser",
                "email": "test2@example.com",
                "password": "password123"
            }
        )

        # Should succeed (different username)
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

import pytest
from playwright.sync_api import Page, expect
import time

BASE_URL = "http://localhost:3000"
API_URL = "http://localhost:5000"


@pytest.fixture(scope="function")
def unique_email():
    """Generate a unique email for each test"""
    return f"test_{int(time.time())}@example.com"


class TestAuthentication:
    """Test suite for user authentication"""

    def test_registration_success(self, page: Page, unique_email: str):
        """Test successful user registration"""
        # Navigate to register page
        page.goto(f"{BASE_URL}/register")
        
        # Fill out registration form
        page.get_by_role("textbox", name="Email *").fill(unique_email)
        page.get_by_role("textbox", name="Username (Optional)").fill("testuser")
        page.get_by_role("textbox", name="Password *").fill("TestPass123")
        page.get_by_role("checkbox", name="I accept the terms and").check()
        
        # Submit form
        page.get_by_role("button", name="Create Account").click()
        
        # Should redirect to homepage
        expect(page).to_have_url(BASE_URL + "/")
        
        # Should show welcome message with username
        expect(page.get_by_text("Welcome, testuser!")).to_be_visible()

    def test_registration_password_validation(self, page: Page, unique_email: str):
        """Test password validation on registration"""
        page.goto(f"{BASE_URL}/register")
        
        # Try with weak password (no uppercase)
        page.get_by_role("textbox", name="Email *").fill(unique_email)
        page.get_by_role("textbox", name="Password *").fill("weakpass123")
        page.get_by_role("checkbox", name="I accept the terms and").check()
        page.get_by_role("button", name="Create Account").click()
        
        # Should show error message
        expect(page.get_by_text("Password must contain")).to_be_visible()

    def test_registration_email_validation(self, page: Page):
        """Test email validation on registration"""
        page.goto(f"{BASE_URL}/register")
        
        # Try with invalid email
        page.get_by_role("textbox", name="Email *").fill("invalid-email")
        page.get_by_role("textbox", name="Password *").fill("TestPass123")
        page.get_by_role("checkbox", name="I accept the terms and").check()
        page.get_by_role("button", name="Create Account").click()
        
        # Should show error message
        expect(page.get_by_text("Invalid email format")).to_be_visible()

    def test_registration_terms_required(self, page: Page, unique_email: str):
        """Test that terms acceptance is required"""
        page.goto(f"{BASE_URL}/register")
        
        # Fill form without accepting terms
        page.get_by_role("textbox", name="Email *").fill(unique_email)
        page.get_by_role("textbox", name="Password *").fill("TestPass123")
        page.get_by_role("button", name="Create Account").click()
        
        # Should show error message
        expect(page.get_by_text("You must accept the terms and conditions")).to_be_visible()

    def test_registration_duplicate_email(self, page: Page, unique_email: str):
        """Test registration with duplicate email"""
        # First registration
        page.goto(f"{BASE_URL}/register")
        page.get_by_role("textbox", name="Email *").fill(unique_email)
        page.get_by_role("textbox", name="Password *").fill("TestPass123")
        page.get_by_role("checkbox", name="I accept the terms and").check()
        page.get_by_role("button", name="Create Account").click()
        
        # Wait for redirect
        expect(page).to_have_url(BASE_URL + "/")
        
        # Logout
        page.get_by_role("button", name="Logout").click()
        
        # Try to register again with same email
        page.goto(f"{BASE_URL}/register")
        page.get_by_role("textbox", name="Email *").fill(unique_email)
        page.get_by_role("textbox", name="Password *").fill("TestPass123")
        page.get_by_role("checkbox", name="I accept the terms and").check()
        page.get_by_role("button", name="Create Account").click()
        
        # Should show error message
        expect(page.get_by_text("Email already registered")).to_be_visible()

    def test_login_success(self, page: Page, unique_email: str):
        """Test successful login"""
        # First, create an account
        page.goto(f"{BASE_URL}/register")
        page.get_by_role("textbox", name="Email *").fill(unique_email)
        page.get_by_role("textbox", name="Username (Optional)").fill("loginuser")
        page.get_by_role("textbox", name="Password *").fill("TestPass123")
        page.get_by_role("checkbox", name="I accept the terms and").check()
        page.get_by_role("button", name="Create Account").click()
        
        # Wait for redirect
        expect(page).to_have_url(BASE_URL + "/")
        
        # Logout
        page.get_by_role("button", name="Logout").click()
        
        # Now login
        page.goto(f"{BASE_URL}/login")
        page.get_by_role("textbox", name="Email").fill(unique_email)
        page.get_by_role("textbox", name="Password").fill("TestPass123")
        page.get_by_role("button", name="Log In").click()
        
        # Should redirect to homepage
        expect(page).to_have_url(BASE_URL + "/")
        
        # Should show welcome message
        expect(page.get_by_text("Welcome, loginuser!")).to_be_visible()

    def test_login_invalid_credentials(self, page: Page):
        """Test login with invalid credentials"""
        page.goto(f"{BASE_URL}/login")
        
        page.get_by_role("textbox", name="Email").fill("nonexistent@example.com")
        page.get_by_role("textbox", name="Password").fill("WrongPass123")
        page.get_by_role("button", name="Log In").click()
        
        # Should show error message
        expect(page.get_by_text("Invalid email or password")).to_be_visible()

    def test_logout(self, page: Page, unique_email: str):
        """Test logout functionality"""
        # Register and login
        page.goto(f"{BASE_URL}/register")
        page.get_by_role("textbox", name="Email *").fill(unique_email)
        page.get_by_role("textbox", name="Username (Optional)").fill("logoutuser")
        page.get_by_role("textbox", name="Password *").fill("TestPass123")
        page.get_by_role("checkbox", name="I accept the terms and").check()
        page.get_by_role("button", name="Create Account").click()
        
        # Wait for redirect
        expect(page).to_have_url(BASE_URL + "/")
        expect(page.get_by_text("Welcome, logoutuser!")).to_be_visible()
        
        # Logout
        page.get_by_role("button", name="Logout").click()
        
        # Should show login/register buttons instead of welcome message
        expect(page.get_by_role("link", name="Log In")).to_be_visible()
        expect(page.get_by_role("link", name="Register")).to_be_visible()


class TestProtectedEndpoints:
    """Test suite for protected endpoints that require authentication"""

    def test_profile_endpoint_without_auth(self, page: Page):
        """Test accessing profile endpoint without authentication"""
        # Clear cookies to ensure no authentication
        page.context.clear_cookies()
        
        # Try to access homepage (which calls profile API)
        page.goto(BASE_URL)
        
        # Should show login/register buttons (not logged in)
        expect(page.get_by_role("link", name="Log In")).to_be_visible()
        expect(page.get_by_role("link", name="Register")).to_be_visible()

    def test_profile_endpoint_with_auth(self, page: Page, unique_email: str):
        """Test accessing profile endpoint with valid authentication"""
        # Register a user
        page.goto(f"{BASE_URL}/register")
        page.get_by_role("textbox", name="Email *").fill(unique_email)
        page.get_by_role("textbox", name="Username (Optional)").fill("authuser")
        page.get_by_role("textbox", name="Password *").fill("TestPass123")
        page.get_by_role("checkbox", name="I accept the terms and").check()
        page.get_by_role("button", name="Create Account").click()
        
        # Should be authenticated and see welcome message
        expect(page).to_have_url(BASE_URL + "/")
        expect(page.get_by_text("Welcome, authuser!")).to_be_visible()

import requests
import sys
import json
from datetime import datetime
import uuid

class HOAAPITester:
    def __init__(self, base_url="https://communitypay-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session_token = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
            
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_user_registration(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_user = {
            "email": f"test_user_{timestamp}@example.com",
            "password": "TestPass123!",
            "name": f"Test User {timestamp}",
            "role": "resident",
            "unit_number": "A101",
            "phone": "+639123456789"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=test_user
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['user_id']
            print(f"   Registered user: {response['user']['email']}")
            return True
        return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        # First register a user
        timestamp = datetime.now().strftime('%H%M%S')
        test_user = {
            "email": f"login_test_{timestamp}@example.com",
            "password": "TestPass123!",
            "name": f"Login Test User {timestamp}",
            "role": "resident"
        }
        
        # Register first
        reg_success, reg_response = self.run_test(
            "Registration for Login Test",
            "POST",
            "auth/register",
            200,
            data=test_user
        )
        
        if not reg_success:
            return False
            
        # Now test login
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['user_id']
            return True
        return False

    def test_get_current_user(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_create_payment(self):
        """Test payment creation"""
        payment_data = {
            "amount": 1500.00,
            "payment_method": "stripe",
            "description": "Monthly HOA Dues - Test",
            "metadata": {"test": True}
        }
        
        success, response = self.run_test(
            "Create Payment",
            "POST",
            "payments/create",
            200,
            data=payment_data
        )
        
        if success and 'payment_id' in response:
            self.payment_id = response['payment_id']
            return True
        return False

    def test_get_payments(self):
        """Test getting payment history"""
        success, response = self.run_test(
            "Get Payments",
            "GET",
            "payments",
            200
        )
        return success

    def test_create_announcement(self):
        """Test announcement creation (requires admin/board_member role)"""
        announcement_data = {
            "title": "Test Announcement",
            "content": "This is a test announcement for the community.",
            "priority": "normal",
            "tags": ["test", "community"]
        }
        
        success, response = self.run_test(
            "Create Announcement",
            "POST",
            "announcements",
            200,
            data=announcement_data
        )
        
        if success and 'announcement' in response:
            self.announcement_id = response['announcement']['announcement_id']
            return True
        return False

    def test_get_announcements(self):
        """Test getting announcements"""
        success, response = self.run_test(
            "Get Announcements",
            "GET",
            "announcements",
            200
        )
        return success

    def test_ai_announcement_draft(self):
        """Test AI announcement drafting"""
        ai_request = {
            "prompt": "Create an announcement about upcoming community maintenance work on the swimming pool area scheduled for next weekend."
        }
        
        success, response = self.run_test(
            "AI Announcement Draft",
            "POST",
            "announcements/ai-draft",
            200,
            data=ai_request
        )
        
        if success and 'draft' in response:
            print(f"   AI Draft: {response['draft'][:100]}...")
            return True
        return False

    def test_create_discussion(self):
        """Test discussion creation"""
        discussion_data = {
            "title": "Test Discussion Topic",
            "content": "This is a test discussion about community matters.",
            "category": "general"
        }
        
        success, response = self.run_test(
            "Create Discussion",
            "POST",
            "discussions",
            200,
            data=discussion_data
        )
        
        if success and 'discussion' in response:
            self.discussion_id = response['discussion']['discussion_id']
            return True
        return False

    def test_get_discussions(self):
        """Test getting discussions"""
        success, response = self.run_test(
            "Get Discussions",
            "GET",
            "discussions",
            200
        )
        return success

    def test_reply_to_discussion(self):
        """Test replying to a discussion"""
        if not hasattr(self, 'discussion_id'):
            print("   Skipping - No discussion ID available")
            return True
            
        reply_data = {
            "content": "This is a test reply to the discussion."
        }
        
        success, response = self.run_test(
            "Reply to Discussion",
            "POST",
            f"discussions/{self.discussion_id}/reply",
            200,
            data=reply_data
        )
        return success

    def test_create_event(self):
        """Test event creation"""
        event_data = {
            "title": "Community Meeting",
            "description": "Monthly community meeting to discuss important matters.",
            "event_date": "2025-02-15T19:00:00",
            "location": "Community Center",
            "max_attendees": 50
        }
        
        success, response = self.run_test(
            "Create Event",
            "POST",
            "events",
            200,
            data=event_data
        )
        
        if success and 'event' in response:
            self.event_id = response['event']['event_id']
            return True
        return False

    def test_get_events(self):
        """Test getting events"""
        success, response = self.run_test(
            "Get Events",
            "GET",
            "events",
            200
        )
        return success

    def test_attend_event(self):
        """Test event attendance"""
        if not hasattr(self, 'event_id'):
            print("   Skipping - No event ID available")
            return True
            
        success, response = self.run_test(
            "Attend Event",
            "POST",
            f"events/{self.event_id}/attend",
            200
        )
        return success

    def test_get_notifications(self):
        """Test getting notifications"""
        success, response = self.run_test(
            "Get Notifications",
            "GET",
            "notifications",
            200
        )
        return success

    def test_update_profile(self):
        """Test profile update"""
        update_data = {
            "name": "Updated Test User",
            "unit_number": "B202",
            "phone": "+639987654321"
        }
        
        success, response = self.run_test(
            "Update Profile",
            "PUT",
            "users/profile",
            200,
            data=update_data
        )
        return success

    def test_logout(self):
        """Test user logout"""
        success, response = self.run_test(
            "User Logout",
            "POST",
            "auth/logout",
            200
        )
        return success

def main():
    print("🚀 Starting HOA Management App API Tests")
    print("=" * 50)
    
    tester = HOAAPITester()
    
    # Authentication Tests
    print("\n📋 AUTHENTICATION TESTS")
    if not tester.test_user_registration():
        print("❌ Registration failed, stopping tests")
        return 1
    
    if not tester.test_user_login():
        print("❌ Login failed, stopping tests")
        return 1
        
    if not tester.test_get_current_user():
        print("❌ Get current user failed")
    
    # Payment Tests
    print("\n💳 PAYMENT TESTS")
    tester.test_create_payment()
    tester.test_get_payments()
    
    # Announcement Tests
    print("\n📢 ANNOUNCEMENT TESTS")
    tester.test_get_announcements()
    # Note: Create announcement will likely fail due to role restrictions
    tester.test_create_announcement()
    tester.test_ai_announcement_draft()
    
    # Discussion Tests
    print("\n💬 DISCUSSION TESTS")
    tester.test_create_discussion()
    tester.test_get_discussions()
    tester.test_reply_to_discussion()
    
    # Event Tests
    print("\n📅 EVENT TESTS")
    tester.test_create_event()
    tester.test_get_events()
    tester.test_attend_event()
    
    # Other Tests
    print("\n🔔 OTHER TESTS")
    tester.test_get_notifications()
    tester.test_update_profile()
    tester.test_logout()
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Tests completed: {tester.tests_passed}/{tester.tests_run}")
    success_rate = (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0
    print(f"📈 Success rate: {success_rate:.1f}%")
    
    if success_rate >= 70:
        print("✅ Backend API tests mostly successful")
        return 0
    else:
        print("❌ Backend API tests have significant issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
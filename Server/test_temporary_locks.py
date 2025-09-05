#!/usr/bin/env python3
"""
Test script for temporary locking functionality
"""

import requests
import json
import time
from datetime import date, timedelta

# Test configuration
BASE_URL = "http://localhost:5000/api"
TEST_EMAIL = "raz.amzaleg@campus.technion.ac.il"  # Use existing user
TEST_PASSWORD = "your_password_here"  # You'll need the real password

def test_temporary_locks():
    """Test the temporary locking functionality"""
    print("🧪 Testing Temporary Locks Functionality")
    print("=" * 50)
    
    # Step 1: Login with existing user (skip registration)
    print("1. Logging in with existing user...")
    
    # Login directly
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        print("Please update TEST_EMAIL and TEST_PASSWORD with valid credentials")
        return
        
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ User setup complete")
    
    # Step 2: Get available items
    print("2. Getting available items...")
    items_response = requests.get(f"{BASE_URL}/items/", headers=headers)
    if items_response.status_code != 200:
        print(f"❌ Failed to get items: {items_response.text}")
        return
        
    items = items_response.json()["items"]
    if not items:
        print("❌ No items available for testing")
        return
        
    test_item = items[0]
    print(f"✅ Using test item: {test_item['name']} (ID: {test_item['id']})")
    
    # Step 3: Add item to cart
    print("3. Adding item to cart...")
    add_to_cart_response = requests.post(
        f"{BASE_URL}/bookings/cart/add/{test_item['id']}", 
        json={"amount": 1},
        headers=headers
    )
    
    if add_to_cart_response.status_code not in [200, 201]:
        print(f"❌ Failed to add to cart: {add_to_cart_response.text}")
        return
        
    print("✅ Item added to cart")
    
    # Step 4: Test temporary locking
    print("4. Testing temporary locking...")
    
    # Create date range for testing (tomorrow and day after)
    start_date = (date.today() + timedelta(days=1)).isoformat()
    end_date = (date.today() + timedelta(days=2)).isoformat()
    
    lock_data = {
        "start_date": start_date,
        "end_date": end_date,
        "session_id": "test_session_123"
    }
    
    lock_response = requests.post(
        f"{BASE_URL}/bookings/lock-items",
        json=lock_data,
        headers=headers
    )
    
    if lock_response.status_code != 201:
        print(f"❌ Failed to lock items: {lock_response.text}")
        return
        
    lock_result = lock_response.json()
    print(f"✅ Items locked successfully!")
    print(f"   Locked items: {len(lock_result['locked_items'])}")
    print(f"   Expires in: {lock_result['expires_in_minutes']} minutes")
    
    # Step 5: Test lock extension
    print("5. Testing lock extension...")
    
    extend_response = requests.post(
        f"{BASE_URL}/bookings/extend-locks",
        json={"additional_minutes": 15},
        headers=headers
    )
    
    if extend_response.status_code == 200:
        print("✅ Lock extension successful")
    else:
        print(f"❌ Lock extension failed: {extend_response.text}")
    
    # Step 6: Verify locks exist (try to create same lock from different session)
    print("6. Verifying locks prevent double booking...")
    
    # This should fail due to insufficient availability
    lock_data["session_id"] = "different_session_456"
    second_lock_response = requests.post(
        f"{BASE_URL}/bookings/lock-items",
        json=lock_data,
        headers=headers
    )
    
    if second_lock_response.status_code == 400:
        error_data = second_lock_response.json()
        if "INSUFFICIENT_AVAILABILITY" in error_data.get("error", ""):
            print("✅ Locks correctly prevent double booking")
        else:
            print(f"❌ Unexpected error: {error_data}")
    else:
        print(f"❌ Expected lock conflict but got: {second_lock_response.text}")
    
    # Step 7: Test lock release
    print("7. Testing lock release...")
    
    release_response = requests.delete(
        f"{BASE_URL}/bookings/release-locks",
        headers=headers
    )
    
    if release_response.status_code == 200:
        print("✅ Locks released successfully")
    else:
        print(f"❌ Lock release failed: {release_response.text}")
    
    # Step 8: Verify locks are gone (try to lock again)
    print("8. Verifying locks are released...")
    
    third_lock_response = requests.post(
        f"{BASE_URL}/bookings/lock-items",
        json=lock_data,
        headers=headers
    )
    
    if third_lock_response.status_code == 201:
        print("✅ Can lock items again after release")
        
        # Clean up - release the new locks
        requests.delete(f"{BASE_URL}/bookings/release-locks", headers=headers)
    else:
        print(f"❌ Could not lock items after release: {third_lock_response.text}")
    
    print("\n🎉 Temporary locks test completed!")
    print("=" * 50)

if __name__ == "__main__":
    try:
        test_temporary_locks()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

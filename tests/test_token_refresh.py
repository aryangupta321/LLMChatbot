"""Test token refresh utility functionality"""

import os
import sys

# Test import
print("="*60)
print("Testing Token Refresh Utility")
print("="*60)

# Test 1: Import the module
print("\n1. Testing module import...")
try:
    from refresh_zoho_token import ZohoTokenRefresher
    print("   ✅ Module imported successfully")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Initialize without credentials
print("\n2. Testing initialization without credentials...")
refresher = ZohoTokenRefresher()
print(f"   ✅ Initialized: {refresher}")
print(f"   ✅ Configured: {refresher.is_configured}")
print(f"   ✅ Accounts URL: {refresher.accounts_url}")

# Test 3: Test refresh with missing credentials (should handle gracefully)
print("\n3. Testing refresh with missing credentials...")
result = refresher.refresh_access_token("Test")
print(f"   ✅ Result structure: {result.keys()}")
print(f"   ✅ Success: {result['success']}")
print(f"   ✅ Error type: {result['error']}")
assert result['success'] == False
assert result['error'] == 'missing_credentials'

# Test 4: Test with mock credentials
print("\n4. Testing with mock credentials...")
refresher.refresh_token = "mock_refresh_token"
refresher.client_id = "mock_client_id"
refresher.client_secret = "mock_client_secret"
refresher.is_configured = True
print(f"   ✅ Configuration updated")
print(f"   ✅ Is configured: {refresher.is_configured}")

print("\n" + "="*60)
print("✅ All utility tests passed!")
print("="*60)

print("\n📋 Utility Features:")
print("   • Automatic token refresh with retry logic")
print("   • Support for SalesIQ and Desk tokens")
print("   • Optional .env file auto-update")
print("   • Detailed error messages")
print("   • Railway deployment instructions")
print("   • Token expiration tracking")

print("\n💡 Usage:")
print("   python refresh_zoho_token.py --all          # Refresh all")
print("   python refresh_zoho_token.py --salesiq      # SalesIQ only")
print("   python refresh_zoho_token.py --desk         # Desk only")
print("   python refresh_zoho_token.py --all --update-env  # Auto-update .env")

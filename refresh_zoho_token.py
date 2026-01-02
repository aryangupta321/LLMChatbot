"""
Zoho Access Token Refresh Utility

This script refreshes Zoho access tokens for SalesIQ and Desk APIs.
Run this before testing to ensure valid tokens (tokens expire after 1 hour).

Usage:
    python refresh_zoho_token.py [--salesiq] [--desk] [--all]
    
    --salesiq    Refresh SalesIQ access token only
    --desk       Refresh Desk access token only
    --all        Refresh all tokens (default)

Environment variables required:
    ZOHO_REFRESH_TOKEN - Refresh token (long-lived)
    ZOHO_CLIENT_ID - OAuth client ID
    ZOHO_CLIENT_SECRET - OAuth client secret
    
Optional:
    ZOHO_ACCOUNTS_URL - Zoho accounts URL (default: https://accounts.zoho.in)
"""

import os
import sys
import argparse
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ZohoTokenRefresher:
    """Handles Zoho OAuth token refresh"""
    
    def __init__(self):
        # Primary OAuth credentials (for shared token or SalesIQ)
        self.refresh_token = os.getenv("ZOHO_REFRESH_TOKEN", "").strip()
        self.client_id = os.getenv("ZOHO_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("ZOHO_CLIENT_SECRET", "").strip()
        self.accounts_url = os.getenv("ZOHO_ACCOUNTS_URL", "https://accounts.zoho.in").strip()
        
        # Optional: Separate Desk OAuth credentials (if using separate OAuth app)
        self.desk_refresh_token = os.getenv("ZOHO_DESK_REFRESH_TOKEN", "").strip() or self.refresh_token
        self.desk_client_id = os.getenv("ZOHO_DESK_CLIENT_ID", "").strip() or self.client_id
        self.desk_client_secret = os.getenv("ZOHO_DESK_CLIENT_SECRET", "").strip() or self.client_secret
        
        # Validate credentials
        self.is_configured = bool(self.refresh_token and self.client_id and self.client_secret)
        self.desk_separate = bool(
            os.getenv("ZOHO_DESK_REFRESH_TOKEN") and 
            (self.desk_refresh_token != self.refresh_token)
        )
    
    def refresh_access_token(self, service_name: str = "Zoho", use_desk_credentials: bool = False) -> dict:
        """
        Refresh Zoho access token using refresh token
        
        Args:
            service_name: Name of service for logging (e.g., "SalesIQ", "Desk")
            use_desk_credentials: Use separate Desk OAuth credentials if available
            
        Returns:
            dict with 'success', 'access_token', 'expires_in', 'error' keys
        """
        if not self.is_configured:
            return {
                "success": False,
                "error": "missing_credentials",
                "details": "Required: ZOHO_REFRESH_TOKEN, ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET"
            }
        
        # Use Desk-specific credentials if available and requested
        if use_desk_credentials and self.desk_separate:
            client_id = self.desk_client_id
            client_secret = self.desk_client_secret
            refresh_token = self.desk_refresh_token
            print(f"   Using separate Desk OAuth credentials")
        else:
            client_id = self.client_id
            client_secret = self.client_secret
            refresh_token = self.refresh_token
            if service_name == "Desk" and not self.desk_separate:
                print(f"   Using shOAuth credentials (same token for SalesIQ + Desk)")
        
        endpoint = f"{self.accounts_url}/oauth/v2/token"
        
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        try:
            print(f"🔄 Refreshing {service_name} access token...")
            print(f"   Endpoint: {endpoint}")
            print(f"   Client ID: {self.client_id[:20]}...")
            
            response = requests.post(endpoint, data=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token")
                expires_in = data.get("expires_in", 3600)
                
                if access_token:
                    print(f"✅ {service_name} token refreshed successfully!")
                    print(f"   Token: {access_token[:30]}...{access_token[-10:]}")
                    print(f"   Length: {len(access_token)} characters")
                    print(f"   Valid for: {expires_in // 60} minutes")
                    print(f"   Expires at: {datetime.now()}")
                    
                    return {
                        "success": True,
                        "access_token": access_token,
                        "expires_in": expires_in,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": "no_token_in_response",
                        "details": response.text
                    }
            else:
                error_msg = response.text
                print(f"❌ {service_name} token refresh failed: HTTP {response.status_code}")
                print(f"   Error: {error_msg}")
                
                return {
                    "success": False,
                    "error": f"HTTP_{response.status_code}",
                    "details": error_msg
                }
                
        except requests.exceptions.Timeout:
            print(f"❌ {service_name} token refresh timeout (>10s)")
            return {
                "success": False,
                "error": "timeout",
                "details": "Request timed out after 10 seconds"
            }
            
        except Exception as e:
            print(f"❌ {service_name} token refresh failed: {str(e)}")
            return {
                "success": False,
                "error": "exception",
                "details": str(e)
            }
    
    def update_env_file(self, token_key: str, new_token: str):
        """
        Update .env file with new token
        
        Args:
            token_key: Environment variable name (e.g., "SALESIQ_ACCESS_TOKEN")
            new_token: New access token value
        """
        env_file = ".env"
        
        if not os.path.exists(env_file):
            print(f"⚠️  Warning: {env_file} not found. Creating new file.")
            with open(env_file, 'w') as f:
                f.write(f"{token_key}={new_token}\n")
            print(f"✅ Created {env_file} with {token_key}")
            return
        
        # Read existing .env file
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update or append token
        token_found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{token_key}="):
                lines[i] = f"{token_key}={new_token}\n"
                token_found = True
                break
        
        if not token_found:
            lines.append(f"{token_key}={new_token}\n")
        
        # Write back to .env
        with open(env_file, 'w') as f:
            f.writelines(lines)
        
        print(f"✅ Updated {env_file} with new {token_key}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Refresh Zoho access tokens",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python refresh_zoho_token.py --all          # Refresh all tokens
  python refresh_zoho_token.py --salesiq      # Refresh SalesIQ token only
  python refresh_zoho_token.py --desk         # Refresh Desk token only
  
Environment variables (.env file):
  ZOHO_REFRESH_TOKEN=your_refresh_token
  ZOHO_CLIENT_ID=your_client_id
  ZOHO_CLIENT_SECRET=your_client_secret
        """
    )
    
    parser.add_argument("--salesiq", action="store_true", help="Refresh SalesIQ token only")
    parser.add_argument("--desk", action="store_true", help="Refresh Desk token only")
    parser.add_argument("--all", action="store_true", help="Refresh all tokens (default)")
    parser.add_argument("--update-env", action="store_true", help="Update .env file with new tokens")
    
    args = parser.parse_args()
    
    # Default to --all if no specific service selected
    if not (args.salesiq or args.desk):
        args.all = True
    
    print("=" * 70)
    print("🔐 Zoho Access Token Refresh Utility")
    print("=" * 70)
    print()
    
    refresher = ZohoTokenRefresher()
    
    # Display configuration mode
    if refresher.desk_separate:
        print("ℹ️  Mode: Separate OAuth apps (SalesIQ + Desk have different tokens)")
        print()
    else:
        print("ℹ️  Mode: Shared OAuth app (same token for SalesIQ + Desk)")
        print()
    
    if not refresher.is_configured:
        print("❌ Missing required credentials!")
        print("   Please set the following in your .env file:")
        print("   - ZOHO_REFRESH_TOKEN")
        print("   - ZOHO_CLIENT_ID")
        print("   - ZOHO_CLIENT_SECRET")
        print()
        sys.exit(1)
    
    results = {}
    
    # Refresh SalesIQ token
    if args.all or args.salesiq:
        print()
        result = refresher.refresh_access_token("SalesIQ")
        results["salesiq"] = result
        
        if result["success"] and args.update_env:
            refresher.update_env_file("SALESIQ_ACCESS_TOKEN", result["access_token"])
    
    # Refresh Desk token
    if args.all or args.desk:
        print()
        
        # Check if using separate Desk credentials or shared token
        if refresher.desk_separate:
            result = refresher.refresh_access_token("Desk", use_desk_credentials=True)
        elif args.all and results.get("salesiq", {}).get("success"):
            # If refreshing all and using shared token, reuse SalesIQ token
            print("🔄 Desk token (using same token as SalesIQ)...")
            print("   ℹ️  Shared OAuth app - using same access token for both services")
            result = results["salesiq"]  # Reuse the same token
        else:
            result = refresher.refresh_access_token("Desk", use_desk_credentials=False)
        
        results["desk"] = result
        
        if result["success"] and args.update_env:
            refresher.update_env_file("DESK_ACCESS_TOKEN", result["access_token"])
    
    # Summary
    print()
    print("=" * 70)
    print("📊 Summary")
    print("=" * 70)
    
    for service, result in results.items():
        status = "✅ Success" if result["success"] else "❌ Failed"
        print(f"{service.upper()}: {status}")
        if result["success"]:
            print(f"  Token: {result['access_token'][:30]}...{result['access_token'][-10:]}")
        else:
            print(f"  Error: {result.get('error', 'unknown')}")
    
    print()
    
    # Show Railway deployment instructions
    if any(r["success"] for r in results.values()):
        print("🚀 To use these tokens:")
        print()
        if not args.update_env:
            print("   1. Copy the tokens above")
            print("   2. Update your .env file or Railway environment variables")
        else:
            print("   1. .env file has been updated")
            print("   2. For Railway deployment:")
        
        print("      Railway Dashboard → Variables → Edit")
        for service, result in results.items():
            if result["success"]:
                token_var = f"{service.upper()}_ACCESS_TOKEN"
                print(f"      - {token_var}={result['access_token']}")
        
        print()
        print("   3. Restart the application to use new tokens")
        print()
    
    # Exit with appropriate code
    if all(r["success"] for r in results.values()):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

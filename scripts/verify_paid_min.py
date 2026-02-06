"""
Minimal Paid API Verification Script (Gate-7.2C)

Purpose:
- Verify API key retrieval from Keychain (no actual API calls yet)
- Check that keys are properly masked (no value exposure)
- Safe fallback when keys are not set

Security:
- API key values are NEVER printed
- Only shows \"OK\" or \"MISSING\" status
- No network calls in this phase
"""
import os
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description='Verify API key setup (no network calls)')
    parser.add_argument(
        '--check-keys', 
        action='store_true',
        help='Check if API keys are configured (without showing values)'
    )
    parser.add_argument(
        '--provider',
        choices=['OPENAI', 'GEMINI', 'DRY_RUN'],
        default='DRY_RUN',
        help='Provider to test (default: DRY_RUN, no real API call)'
    )
    parser.add_argument(
        '--max-calls',
        type=int,
        default=0,
        help='Max number of API calls (default: 0 = no calls)'
    )
    
    args = parser.parse_args()
    
    # Try to inject from Keychain if available
    try:
        from ajson.llm_gateway.keychain import inject_from_keychain_if_needed, check_keychain_status
        inject_from_keychain_if_needed()
    except ImportError:
        print(\"[Warning] Keychain module not available (non-macOS or not installed)\")
        check_keychain_status = None
    
    # Check keys mode
    if args.check_keys:
        print(\"\\n=== API Key Status Check ===\")
        
        if check_keychain_status:
            print(f\"OPENAI_API_KEY: {check_keychain_status('AJSON_OPENAI_API_KEY')}\")
            print(f\"GEMINI_API_KEY: {check_keychain_status('AJSON_GEMINI_API_KEY')}\")
        else:
            # Fallback: check env only (no value shown)
            openai_set = \"✅ 設定済み\" if os.getenv('OPENAI_API_KEY') else \"❌ 未設定\"
            gemini_set = \"✅ 設定済み\" if os.getenv('GEMINI_API_KEY') else \"❌ 未設定\"
            print(f\"OPENAI_API_KEY (env): {openai_set}\")
            print(f\"GEMINI_API_KEY (env): {gemini_set}\")
        
        print(\"\\n[Security] API key values are NOT shown for safety.\\n\")
        return
    
    # Provider test mode (Phase 2: NO actual API calls yet)
    if args.max_calls > 0:
        print(f\"\\n[Phase 2] API call testing is NOT implemented yet.\")
        print(f\"  Provider: {args.provider}\")
        print(f\"  Max calls: {args.max_calls}\")
        print(f\"  Status: Skipped (awaiting Gate approval for real API calls)\\n\")
        return
    
    print(\"\\n=== Verification Complete ===\")
    print(\"Phase 2 (Keychain integration) implemented.\"
)
    print(\"Real API calls require separate Gate approval.\\n\")


if __name__ == \"__main__\":
    main()

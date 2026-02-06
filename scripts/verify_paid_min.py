#!/usr/bin/env python3
"""
Minimal Paid API Verification Script

This script performs minimal verification of paid LLM providers (OpenAI, Gemini)
with the following constraints:
- Low-cost models only (gpt-4o-mini, gemini-1.5-flash)
- Minimal prompts ("ping")
- Limited calls (default: 1 per provider)
- Budget guard enforcement
- Audit logging

Usage:
  python -m scripts.verify_paid_min --provider OPENAI --max_calls 1
  python -m scripts.verify_paid_min --provider GEMINI --max_calls 1
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ajson.llm_gateway import get_gateway, LLMRequest
from ajson.llm_gateway.types import ApprovalRequired, BudgetExceeded


def mask_key(key: str) -> str:
    """Mask API key for display"""
    if not key or len(key) < 8:
        return "***"
    return key[:4] + "..." + key[-4:]


async def verify_provider(provider: str, max_calls: int = 1):
    """
    Verify a single provider with minimal calls
    
    Args:
        provider: "OPENAI" or "GEMINI"
        max_calls: Maximum number of test calls
    """
    print(f"\n{'='*60}")
    print(f"Verifying Provider: {provider}")
    print(f"Max Calls: {max_calls}")
    print(f"{'='*60}\n")
    
    # Check environment
    if provider == "OPENAI":
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            print(f"⚠️  OPENAI_API_KEY not set, skipping OpenAI verification")
            return
        print(f"✓ OPENAI_API_KEY: {mask_key(api_key)}")
    elif provider == "GEMINI":
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            print(f"⚠️  GEMINI_API_KEY not set, skipping Gemini verification")
            return
        print(f"✓ GEMINI_API_KEY: {mask_key(api_key)}")
    
    # Set provider environment
    os.environ["LLM_PROVIDER"] = provider
    os.environ["LLM_ENABLE_PAID"] = "1"  # Enable paid mode
    
    # Force new gateway instance
    from ajson.llm_gateway import gateway as gw_module
    gw_module._gateway = None
    
    gateway = get_gateway()
    
    print(f"✓ Gateway initialized with provider: {gateway.provider.provider_name}")
    print(f"✓ Daily budget limit: ${gateway.budget_guard.daily_limit:.2f}")
    
    # Test calls
    for i in range(max_calls):
        print(f"\n--- Call {i+1}/{max_calls} ---")
        
        request = LLMRequest(
            task_id=f"verify_paid_{provider.lower()}_{i+1}",
            role="planner",
            prompt="ping",  # Minimal prompt
            system_instruction="Respond with 'pong' only.",
        )
        
        try:
            # Check budget before call
            is_safe, current, predicted = gateway.budget_guard.check_budget()
            print(f"Budget check: current=${current:.4f}, predicted=${predicted:.4f}, safe={is_safe}")
            
            if not is_safe:
                print(f"⚠️  Budget guard would block (predicted ${predicted:.4f} > ${gateway.budget_guard.daily_limit:.2f})")
                print(f"⚠️  Stopping verification to prevent budget overrun")
                return
            
            # Call gateway
            print(f"→ Calling {provider} with prompt: '{request.prompt}'")
            start_time = datetime.now()
            
            response = await gateway.generate_text(request)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Display results
            print(f"✓ Response received in {duration:.2f}s")
            print(f"  Provider: {response.provider}")
            print(f"  Model: {response.model}")
            print(f"  Response text: {response.text[:100]}{'...' if len(response.text) > 100 else ''}")
            
            if response.usage:
                print(f"  Usage:")
                print(f"    Input tokens: {response.usage.input_tokens}")
                print(f"    Output tokens: {response.usage.output_tokens}")
                print(f"    Total tokens: {response.usage.total_tokens}")
            else:
                print(f"  ⚠️  Usage metadata not available")
            
            if response.cost_estimate_usd is not None:
                print(f"  Cost estimate: ${response.cost_estimate_usd:.6f}")
            else:
                print(f"  ⚠️  Cost estimate not available (conservative: would trigger approval)")
            
            if response.provider_request_id:
                print(f"  Request ID: {response.provider_request_id}")
            
            # Budget status after call
            is_safe, current, predicted = gateway.budget_guard.check_budget()
            print(f"Budget after call: current=${current:.4f}, predicted=${predicted:.4f}, safe={is_safe}")
            
        except ApprovalRequired as e:
            print(f"⚠️  ApprovalRequired: {e.reason}")
            print(f"   Details: {e.details}")
            return
        
        except BudgetExceeded as e:
            print(f"🛑 BudgetExceeded!")
            print(f"   Predicted: ${e.predicted_cost:.4f}")
            print(f"   Limit: ${e.limit:.2f}")
            print(f"   Current: ${e.current_cost:.4f}")
            print(f"   Stopping verification to prevent overrun")
            return
        
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return


def main():
    parser = argparse.ArgumentParser(description="Minimal paid API verification")
    parser.add_argument(
        "--provider",
        required=True,
        choices=["OPENAI", "GEMINI"],
        help="Provider to verify"
    )
    parser.add_argument(
        "--max_calls",
        type=int,
        default=1,
        help="Maximum number of test calls (default: 1)"
    )
    
    args = parser.parse_args()
    
    # Run verification
    asyncio.run(verify_provider(args.provider, args.max_calls))
    
    print(f"\n{'='*60}")
    print(f"Verification complete for {args.provider}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

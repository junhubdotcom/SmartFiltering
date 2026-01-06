"""
test_agent_api_call.py
----------------------

Quick test to verify the agent's search functions can fetch real data from the backend.
"""

import sys
sys.path.insert(0, '/Users/liuqi/PycharmProjects/SmartFilteringV1')

from my_agent.data.api_client import (
    get_transport_listings,
    get_accommodation_listings,
    get_item_listings,
    fetch_all_listings,
)
from my_agent.subagents.transport_agent import search_transport_listings
from my_agent.subagents.item_agent import search_item_listings
from my_agent.subagents.accommodation_agent import search_accommodation_listings
import json


def test_api_client():
    """Test the API client functions."""
    print("\n" + "="*60)
    print("🔌 Testing API Client")
    print("="*60)
    
    # Test fetch all
    result = fetch_all_listings()
    if result["success"]:
        print(f"✅ fetch_all_listings: {len(result['data'])} listings")
    else:
        print(f"❌ fetch_all_listings: {result['error']}")
        return False
    
    # Test by type
    transport = get_transport_listings()
    print(f"   - Transport listings: {len(transport)}")
    
    items = get_item_listings()
    print(f"   - Item listings: {len(items)}")
    
    accommodation = get_accommodation_listings()
    print(f"   - Accommodation listings: {len(accommodation)}")
    
    return True


def test_transport_search():
    """Test the transport agent search function."""
    print("\n" + "="*60)
    print("🚗 Testing Transport Search")
    print("="*60)
    
    result = search_transport_listings()
    
    if result.get("matched") or result.get("suggestions") or result.get("results"):
        print(f"✅ Transport search returned results")
        print(f"   Message: {result.get('message')}")
        results = result.get("results") or result.get("suggestions", [])
        for r in results[:2]:  # Show first 2
            print(f"   - {r.get('title')}: RM{r.get('pricePerDay')}/day")
        return True
    else:
        print(f"❌ Transport search failed: {result}")
        return False


def test_item_search():
    """Test the item agent search function."""
    print("\n" + "="*60)
    print("📦 Testing Item Search")
    print("="*60)
    
    result = search_item_listings()
    
    if result.get("matched") or result.get("suggestions") or result.get("results"):
        print(f"✅ Item search returned results")
        print(f"   Message: {result.get('message')}")
        results = result.get("results") or result.get("suggestions", [])
        for r in results[:2]:  # Show first 2
            print(f"   - {r.get('title')}: RM{r.get('pricePerDay')}/day")
        return True
    else:
        print(f"❌ Item search failed: {result}")
        return False


def test_accommodation_search():
    """Test the accommodation agent search function."""
    print("\n" + "="*60)
    print("🏠 Testing Accommodation Search")
    print("="*60)
    
    result = search_accommodation_listings()
    
    if result.get("matched") or result.get("suggestions") or result.get("results"):
        print(f"✅ Accommodation search returned results")
        print(f"   Message: {result.get('message')}")
        results = result.get("results") or result.get("suggestions", [])
        for r in results[:2]:  # Show first 2
            print(f"   - {r.get('title')}: RM{r.get('pricePerDay')}/day")
        return True
    else:
        print(f"❌ Accommodation search failed: {result}")
        return False


def test_filtered_search():
    """Test search with filters."""
    print("\n" + "="*60)
    print("🔍 Testing Filtered Search (max RM100/day)")
    print("="*60)
    
    # Search for vehicles under RM100/day
    result = search_transport_listings(max_price_per_day=100)
    print(f"   Transport under RM100: {len(result.get('results', []))} results")
    
    # Search for items under RM100/day
    result = search_item_listings(max_price_per_day=100)
    print(f"   Items under RM100: {len(result.get('results', []))} results")
    
    return True


def main():
    print("\n" + "="*60)
    print("🧪 AGENT API INTEGRATION TEST")
    print("="*60)
    print("Testing if your agent can call the backend API...")
    
    tests = [
        test_api_client,
        test_transport_search,
        test_item_search,
        test_accommodation_search,
        test_filtered_search,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    passed = sum(results)
    print(f"✅ Passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 SUCCESS! Your agent can call the backend API!")
        print("\nYou can now run your agent with:")
        print("   python3 -m my_agent.deployment.local")
    else:
        print("\n⚠️ Some tests failed. Make sure your backend is running at http://localhost:3000")
    
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())

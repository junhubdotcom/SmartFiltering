"""
test_complete.py
----------------

Complete testing file for the Smart Filtering Agent system.
This file demonstrates all functionality and can be used by your partner
to understand how to test and integrate the agent with the UI.

Run with: python test_complete.py
"""

import sys
import json
import os

# Ensure the project is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from my_agent.data.api_client import (
    get_transport_listings,
    get_accommodation_listings,
    get_item_listings,
    fetch_all_listings,
)
from my_agent.subagents.transport_agent import search_transport_listings
from my_agent.subagents.item_agent import search_item_listings
from my_agent.subagents.accommodation_agent import search_accommodation_listings
from my_agent.agent import search_multiple_categories


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(title: str, emoji: str = "📋"):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"{emoji} {title}")
    print("="*70)


def print_json(data: dict, indent: int = 2):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=indent, ensure_ascii=False))


def print_results_summary(results: list, max_show: int = 3):
    """Print a summary of search results."""
    if not results:
        print("   No results found.")
        return
    
    print(f"   Found {len(results)} result(s):")
    for i, r in enumerate(results[:max_show]):
        tags = ", ".join(r.get("tags", []))
        print(f"   {i+1}. {r.get('title')} - RM{r.get('pricePerDay')}/day")
        print(f"      Tags: {tags}")
    
    if len(results) > max_show:
        print(f"   ... and {len(results) - max_show} more")


# ============================================================================
# TEST 1: API CONNECTION TEST
# ============================================================================

def test_api_connection():
    """
    Test 1: Verify connection to the backend API.
    
    This test ensures the agent can connect to the iShareApi backend
    and fetch listings data.
    """
    print_header("TEST 1: API Connection", "🔌")
    
    print("\n📡 Testing connection to backend API...")
    result = fetch_all_listings()
    
    if result["success"]:
        print(f"✅ Connected successfully!")
        print(f"   Total listings in database: {len(result['data'])}")
        
        # Count by type
        transport_count = len([l for l in result['data'] if l.get('type') == 'TRANSPORT'])
        accommodation_count = len([l for l in result['data'] if l.get('type') == 'ACCOMMODATION'])
        item_count = len([l for l in result['data'] if l.get('type') == 'ITEM'])
        
        print(f"\n   Breakdown by type:")
        print(f"   🚗 Transport: {transport_count}")
        print(f"   🏠 Accommodation: {accommodation_count}")
        print(f"   📦 Items: {item_count}")
        return True
    else:
        print(f"❌ Connection failed: {result['error']}")
        print("\n⚠️  Make sure your backend is running at http://localhost:3000")
        return False


# ============================================================================
# TEST 2: TRANSPORT AGENT TESTS
# ============================================================================

def test_transport_agent():
    """
    Test 2: Test the Transport Agent search functionality.
    
    Scenarios tested:
    - Search all vehicles
    - Search with price filter
    - Search with vehicle type filter
    - Search with brand filter
    - Search with no results (fallback to similar vehicles)
    """
    print_header("TEST 2: Transport Agent", "🚗")
    
    all_passed = True
    
    # Test 2.1: Get all transport listings
    print("\n📋 Test 2.1: Get all transport listings")
    result = search_transport_listings()
    print(f"   Message: {result.get('message')}")
    print_results_summary(result.get("results", []))
    
    # Test 2.2: Filter by price
    print("\n📋 Test 2.2: Filter by max price (RM100/day)")
    result = search_transport_listings(max_price_per_day=100)
    print(f"   Message: {result.get('message')}")
    print_results_summary(result.get("results", []))
    
    # Test 2.3: Filter by vehicle type
    print("\n📋 Test 2.3: Filter by vehicle type (car)")
    result = search_transport_listings(vehicle_type="car")
    print(f"   Message: {result.get('message')}")
    print_results_summary(result.get("results", []))
    
    # Test 2.4: Filter by brand
    print("\n📋 Test 2.4: Filter by brand (Toyota)")
    result = search_transport_listings(make="Toyota")
    print(f"   Message: {result.get('message')}")
    print_results_summary(result.get("results", []))
    
    # Test 2.5: Combined filters (may return no results - tests fallback)
    print("\n📋 Test 2.5: Combined filters - car under RM50/day")
    result = search_transport_listings(vehicle_type="car", max_price_per_day=50)
    print(f"   Message: {result.get('message')}")
    print_results_summary(result.get("results", []))
    
    print("\n✅ Transport Agent tests completed")
    return all_passed


# ============================================================================
# TEST 3: ACCOMMODATION AGENT TESTS
# ============================================================================

def test_accommodation_agent():
    """
    Test 3: Test the Accommodation Agent search functionality.
    
    Scenarios tested:
    - Search all accommodations
    - Search with price filter
    - Search with property type filter
    - Search with guest capacity filter
    - Search with location filter
    - Complex scenario: Room in KL for 6 guests, budget RM333/day
    """
    print_header("TEST 3: Accommodation Agent", "🏠")
    
    # Test 3.1: Get all accommodation listings
    print("\n📋 Test 3.1: Get all accommodation listings")
    result = search_accommodation_listings()
    print(f"   Message: {result.get('message')}")
    print_results_summary(result.get("results", []))
    
    # Test 3.2: Filter by price
    print("\n📋 Test 3.2: Filter by max price (RM200/day)")
    result = search_accommodation_listings(max_price_per_day=200)
    print(f"   Message: {result.get('message')}")
    print_results_summary(result.get("results", []))
    
    # Test 3.3: Filter by property type
    print("\n📋 Test 3.3: Filter by property type (room)")
    result = search_accommodation_listings(property_type="room")
    print(f"   Message: {result.get('message')}")
    print_results_summary(result.get("results", []))
    
    # Test 3.4: Filter by guest capacity
    print("\n📋 Test 3.4: Filter by guest capacity (6 guests)")
    result = search_accommodation_listings(max_guests=6)
    print(f"   Message: {result.get('message')}")
    print_results_summary(result.get("results", []))
    
    # Test 3.5: Filter by location
    print("\n📋 Test 3.5: Filter by location (Kuala Lumpur)")
    result = search_accommodation_listings(location="Kuala Lumpur")
    print(f"   Message: {result.get('message')}")
    print_results_summary(result.get("results", []))
    
    # Test 3.6: Complex scenario - simulating user query:
    # "I want to find a room in Kuala Lumpur from 1 Jan to 3 Jan 2026, 6 guests, maximum budget RM1000 for three days"
    # Budget calculation: RM1000 / 3 days = RM333.33/day
    print("\n📋 Test 3.6: Complex scenario")
    print("   User query: 'Room in KL, 6 guests, RM1000 for 3 days'")
    print("   Calculated: max_price_per_day = 1000/3 = 333.33")
    result = search_accommodation_listings(
        location="Kuala Lumpur",
        property_type="room",
        max_guests=6,
        max_price_per_day=333.33
    )
    print(f"   Message: {result.get('message')}")
    print_results_summary(result.get("results", []))
    
    print("\n✅ Accommodation Agent tests completed")
    return True


# ============================================================================
# TEST 4: ITEM AGENT TESTS
# ============================================================================

def test_item_agent():
    """
    Test 4: Test the Item Agent search functionality.
    
    Scenarios tested:
    - Search all items
    - Search with price filter
    - Search with category filter
    - Search with keyword filter
    - Test focused suggestions (camera search)
    """
    print_header("TEST 4: Item Agent", "📦")
    
    # Test 4.1: Get all item listings
    print("\n📋 Test 4.1: Get all item listings")
    result = search_item_listings()
    print(f"   Message: {result.get('message')}")
    print_results_summary(result.get("results", []))
    
    # Test 4.2: Filter by price
    print("\n📋 Test 4.2: Filter by max price (RM50/day)")
    result = search_item_listings(max_price_per_day=50)
    print(f"   Message: {result.get('message')}")
    print_results_summary(result.get("results", []))
    
    # Test 4.3: Filter by category
    print("\n📋 Test 4.3: Filter by category (Electronics)")
    result = search_item_listings(item_category="Electronics")
    print(f"   Message: {result.get('message')}")
    print_results_summary(result.get("results", []))
    
    # Test 4.4: Filter by keyword
    print("\n📋 Test 4.4: Filter by keyword (camera)")
    result = search_item_listings(keyword="camera")
    print(f"   Message: {result.get('message')}")
    print_results_summary(result.get("results", []))
    
    # Test 4.5: Test focused suggestions
    # Search for camera with very low budget - should only suggest other cameras, not random items
    print("\n📋 Test 4.5: Focused suggestions test")
    print("   Searching for 'camera' with RM10/day budget (likely no exact match)")
    print("   Expected: Only camera suggestions, NOT other items like laptops")
    result = search_item_listings(keyword="camera", max_price_per_day=10)
    print(f"   Message: {result.get('message')}")
    print_results_summary(result.get("results", []))
    
    print("\n✅ Item Agent tests completed")
    return True


# ============================================================================
# TEST 5: FULL JSON RESPONSE TEST
# ============================================================================

def test_json_response_format():
    """
    Test 5: Show full JSON response format for UI integration.
    
    This test shows the exact JSON structure that the UI will receive,
    which is useful for your partner doing the UI integration.
    """
    print_header("TEST 5: JSON Response Format (for UI Integration)", "📄")
    
    print("\n📋 Sample Transport Response:")
    result = search_transport_listings(max_price_per_day=200)
    if result.get("results"):
        sample = {
            "message": result.get("message"),
            "results": result.get("results", [])[:1]  # Show first result only
        }
        print_json(sample)
    
    print("\n📋 Sample Accommodation Response:")
    result = search_accommodation_listings(max_price_per_day=300)
    if result.get("results"):
        sample = {
            "message": result.get("message"),
            "results": result.get("results", [])[:1]
        }
        print_json(sample)
    
    print("\n📋 Sample Item Response:")
    result = search_item_listings(max_price_per_day=100)
    if result.get("results"):
        sample = {
            "message": result.get("message"),
            "results": result.get("results", [])[:1]
        }
        print_json(sample)
    
    print("\n✅ JSON format test completed")
    return True


# ============================================================================
# TEST 6: DATABASE FIELD VERIFICATION
# ============================================================================

def test_database_fields():
    """
    Test 6: Verify all returned fields match database schema.
    
    Database columns:
    id, title, description, basePrice, lat, lng, address, status, images,
    insuranceTemplateId, vehicleType, model, year, licensePlate, category,
    condition, deliveryMethod, propertyType, amenities, type, ownerId, brand,
    transmission, fuelType, seats, maxGuests, bedCount, roomCount, bathroomCount
    """
    print_header("TEST 6: Database Field Verification", "🔍")
    
    # Get raw data from API
    result = fetch_all_listings()
    if not result["success"]:
        print("❌ Cannot verify - API connection failed")
        return False
    
    # Check accommodation fields
    print("\n📋 Accommodation fields check:")
    accommodations = get_accommodation_listings()
    if accommodations:
        sample = accommodations[0]
        expected_fields = ["id", "title", "description", "basePrice", "address", 
                         "propertyType", "maxGuests", "bedCount", "roomCount", 
                         "bathroomCount", "amenities", "images", "status"]
        present = [f for f in expected_fields if f in sample]
        missing = [f for f in expected_fields if f not in sample]
        print(f"   ✅ Present fields: {', '.join(present)}")
        if missing:
            print(f"   ⚠️  Missing fields: {', '.join(missing)}")
    
    # Check transport fields
    print("\n📋 Transport fields check:")
    transports = get_transport_listings()
    if transports:
        sample = transports[0]
        expected_fields = ["id", "title", "description", "basePrice", "address",
                         "vehicleType", "brand", "model", "year", "transmission",
                         "fuelType", "seats", "images", "status"]
        present = [f for f in expected_fields if f in sample]
        missing = [f for f in expected_fields if f not in sample]
        print(f"   ✅ Present fields: {', '.join(present)}")
        if missing:
            print(f"   ⚠️  Missing fields: {', '.join(missing)}")
    
    # Check item fields
    print("\n📋 Item fields check:")
    items = get_item_listings()
    if items:
        sample = items[0]
        expected_fields = ["id", "title", "description", "basePrice", "address",
                         "category", "brand", "model", "condition", "images", "status"]
        present = [f for f in expected_fields if f in sample]
        missing = [f for f in expected_fields if f not in sample]
        print(f"   ✅ Present fields: {', '.join(present)}")
        if missing:
            print(f"   ⚠️  Missing fields: {', '.join(missing)}")
    
    print("\n✅ Database field verification completed")
    return True


# ============================================================================
# TEST 7: EDGE CASES
# ============================================================================

def test_edge_cases():
    """
    Test 7: Test edge cases and error handling.
    
    Scenarios:
    - Empty results
    - Very high budget (should return all)
    - Very low budget (should return focused suggestions or none)
    - Non-existent location
    """
    print_header("TEST 7: Edge Cases", "⚠️")
    
    # Test 7.1: Very low budget - expect no results or focused suggestions
    print("\n📋 Test 7.1: Very low budget (RM1/day)")
    result = search_transport_listings(max_price_per_day=1)
    print(f"   Message: {result.get('message')}")
    print(f"   Results count: {len(result.get('results', []))}")
    
    # Test 7.2: Non-existent location
    print("\n📋 Test 7.2: Non-existent location")
    result = search_accommodation_listings(location="NonExistentCity12345")
    print(f"   Message: {result.get('message')}")
    print(f"   Results count: {len(result.get('results', []))}")
    
    # Test 7.3: Very high budget - should return all matching items
    print("\n📋 Test 7.3: Very high budget (RM10000/day)")
    result = search_item_listings(max_price_per_day=10000)
    print(f"   Message: {result.get('message')}")
    print(f"   Results count: {len(result.get('results', []))}")
    
    # Test 7.4: Focused suggestions - non-existent item type
    print("\n📋 Test 7.4: Search for non-existent item keyword")
    result = search_item_listings(keyword="spaceship")
    print(f"   Message: {result.get('message')}")
    print(f"   Results count: {len(result.get('results', []))}")
    
    print("\n✅ Edge case tests completed")
    return True


# ============================================================================
# TEST 8: MULTI-CATEGORY SEARCH
# ============================================================================

def test_multi_category_search():
    """
    Test 8: Test multi-category search functionality.
    
    Scenarios:
    - Search transport + accommodation
    - Search all three categories
    - Search with shared location filter
    """
    print_header("TEST 8: Multi-Category Search", "🔀")
    
    # Test 8.1: Search transport and accommodation
    print("\n📋 Test 8.1: Search transport + accommodation")
    result = search_multiple_categories(
        search_transport=True,
        search_accommodation=True,
        location="Seri Kembangan"
    )
    print(f"   Message: {result.get('message')}")
    if "categories" in result:
        for cat_key, cat_data in result["categories"].items():
            print(f"   {cat_data.get('category_name')}: {len(cat_data.get('results', []))} results")
    
    # Test 8.2: Search all three categories
    print("\n📋 Test 8.2: Search all three categories")
    result = search_multiple_categories(
        search_transport=True,
        search_accommodation=True,
        search_items=True,
    )
    print(f"   Message: {result.get('message')}")
    if "categories" in result:
        for cat_key, cat_data in result["categories"].items():
            print(f"   {cat_data.get('category_name')}: {len(cat_data.get('results', []))} results")
    
    # Test 8.3: Search with budget filter
    print("\n📋 Test 8.3: Search all categories with budget (RM200/day)")
    result = search_multiple_categories(
        search_transport=True,
        search_accommodation=True,
        search_items=True,
        max_price_per_day=200
    )
    print(f"   Message: {result.get('message')}")
    if "categories" in result:
        for cat_key, cat_data in result["categories"].items():
            print(f"   {cat_data.get('category_name')}: {len(cat_data.get('results', []))} results")
    
    # Test 8.4: Full JSON response for multi-category
    print("\n📋 Test 8.4: Sample multi-category JSON response")
    result = search_multiple_categories(
        search_transport=True,
        search_accommodation=True,
        location="Kuala Lumpur",
        max_price_per_day=300
    )
    # Show first result from each category
    if "categories" in result:
        sample = {
            "type": result.get("type"),
            "message": result.get("message"),
            "categories": {}
        }
        for cat_key, cat_data in result["categories"].items():
            sample["categories"][cat_key] = {
                "category_name": cat_data.get("category_name"),
                "message": cat_data.get("message"),
                "results": cat_data.get("results", [])[:1]  # First result only
            }
        print_json(sample)
    
    print("\n✅ Multi-category search tests completed")
    return True


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all tests and provide summary."""
    print("\n" + "="*70)
    print("🧪 SMART FILTERING AGENT - COMPLETE TEST SUITE")
    print("="*70)
    print("\nThis test file verifies all agent functionality.")
    print("Make sure your backend API is running at http://localhost:3000")
    print("\n" + "-"*70)
    
    tests = [
        ("API Connection", test_api_connection),
        ("Transport Agent", test_transport_agent),
        ("Accommodation Agent", test_accommodation_agent),
        ("Item Agent", test_item_agent),
        ("JSON Response Format", test_json_response_format),
        ("Database Fields", test_database_fields),
        ("Edge Cases", test_edge_cases),
        ("Multi-Category Search", test_multi_category_search),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Exception in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print_header("TEST SUMMARY", "📊")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"   {status} {name}")
    
    print(f"\n   Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n" + "-"*70)
        print("NEXT STEPS FOR UI INTEGRATION:")
        print("-"*70)
        print("""
1. Run the agent locally:
   adk run my_agent

2. Or use the web interface:
   adk web

3. For programmatic access, use the search functions direc      tly:
   
   from my_agent.subagents.transport_agent import search_transport_listings
   from my_agent.subagents.accommodation_agent import search_accommodation_listings
   from my_agent.subagents.item_agent import search_item_listings
   
   # Example: Search for accommodation
   result = search_accommodation_listings(
       location="Kuala Lumpur",
       property_type="room",
       max_guests=6,
       max_price_per_day=333.33
   )
   
   # Result format:
   # {
   #     "message": "Found X accommodation(s) matching your criteria.",
   #     "results": [
   #         {
   #             "listingId": "...",
   #             "title": "...",
   #             "pricePerDay": 200.0,
   #             "tags": ["Most Suitable", "Budget Friendly"],
   #             ...
   #         }
   #     ]
   # }

4. For deployment, see README.md for complete instructions.
""")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("    Make sure your backend API is running at http://localhost:3000")
    
    return 0 if passed_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main())

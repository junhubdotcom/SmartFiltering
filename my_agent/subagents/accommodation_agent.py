"""
accommodation_agent.py
----------------------

Defines the AccommodationAgent for the smart filtering system. This agent
handles user requests for places to stay. It provides a search function
that queries the backend API for accommodation listings and returns
multiple options sorted by suitability. The associated LlmAgent interprets
queries and calls the search tool when needed.
"""

from typing import Optional, Dict, Any, List

from google.adk.agents import LlmAgent

from ..data.api_client import get_accommodation_listings


def search_accommodation_listings(
    location: Optional[str] = None,
    max_price_per_day: Optional[float] = None,
    property_type: Optional[str] = None,
    num_guests: Optional[int] = None,
    min_rating: Optional[float] = None,
) -> Dict[str, Any]:
    """Search the backend API for accommodation listings.

    Filters the list of accommodation listings by optional parameters and
    returns multiple options sorted by suitability (best first), each with
    full details and reason tags. If no listings match, returns related
    suggestions from the same category.

    Args:
        location: Desired city or neighbourhood.
        max_price_per_day: Maximum acceptable rental price per day.
        property_type: Type of property (e.g. Apartment, House).
        num_guests: Minimum number of guests the place must accommodate.
        min_rating: Minimum acceptable average rating.

    Returns:
        A dictionary with 'results' (list of matching options) or 'suggestions'
        (related options if no exact match).
    """
    # Fetch real listings from backend API
    all_listings = get_accommodation_listings()
    
    if not all_listings:
        return {
            "matched": False,
            "message": "No accommodation listings available. The backend may be unavailable or have no accommodation listings.",
            "results": [],
        }
    
    candidates = all_listings.copy()
    
    # Apply filters - using API response field names
    if location:
        candidates = [l for l in candidates if location.lower() in (l.get("address") or "").lower()]
    if max_price_per_day is not None:
        candidates = [l for l in candidates if float(l.get("basePrice", 0)) <= max_price_per_day]
    if property_type:
        candidates = [l for l in candidates if property_type.lower() in (l.get("propertyType") or "").lower()]
    if num_guests:
        candidates = [l for l in candidates if (l.get("numGuests") or 0) >= num_guests]
    
    if not candidates:
        # No exact matches – return all accommodation listings as suggestions
        suggestion_data = []
        for s in all_listings:
            tags = _generate_tags(s, all_listings)
            suggestion_data.append({
                "listingId": s.get("id"),
                "title": s.get("title"),
                "description": s.get("description"),
                "address": s.get("address"),
                "propertyType": s.get("propertyType"),
                "numGuests": s.get("numGuests"),
                "pricePerDay": float(s.get("basePrice", 0)),
                "amenities": s.get("amenities", []),
                "images": s.get("images", []),
                "status": s.get("status"),
                "tags": tags,
            })
        return {
            "matched": False,
            "message": "No accommodations match your exact criteria. Here are all available options:",
            "suggestions": suggestion_data,
        }
    
    # Sort candidates by price (lowest first)
    candidates_sorted = sorted(candidates, key=lambda l: float(l.get("basePrice", 0)))
    
    results = []
    for idx, listing in enumerate(candidates_sorted):
        tags = _generate_tags(listing, candidates)
        if idx == 0:
            tags.insert(0, "Most Suitable")
        results.append({
            "listingId": listing.get("id"),
            "title": listing.get("title"),
            "description": listing.get("description"),
            "address": listing.get("address"),
            "propertyType": listing.get("propertyType"),
            "numGuests": listing.get("numGuests"),
            "pricePerDay": float(listing.get("basePrice", 0)),
            "amenities": listing.get("amenities", []),
            "images": listing.get("images", []),
            "status": listing.get("status"),
            "tags": tags,
        })
    
    return {
        "matched": True,
        "message": f"Found {len(results)} accommodation(s) matching your criteria, sorted from most suitable:",
        "results": results,
    }


def _generate_tags(listing: Dict[str, Any], pool: List[Dict[str, Any]]) -> List[str]:
    """Generate descriptive tags for why this listing is suitable."""
    tags = []
    
    prices = [float(l.get("basePrice", 0)) for l in pool]
    min_price = min(prices) if prices else 0
    
    listing_price = float(listing.get("basePrice", 0))
    
    # Price-based tags
    if listing_price <= min_price * 1.01:
        tags.append("Cheapest Option")
    elif listing_price <= min_price * 1.2:
        tags.append("Budget Friendly")
    
    # Capacity tags
    num_guests = listing.get("numGuests") or 0
    if num_guests >= 6:
        tags.append("Great for Groups")
    elif num_guests >= 4:
        tags.append("Family Friendly")
    
    # Property type tags
    property_type = (listing.get("propertyType") or "").lower()
    if property_type in ["villa", "house"]:
        tags.append("Spacious")
    elif property_type == "apartment":
        tags.append("City Living")
    elif property_type in ["room", "homestay"]:
        tags.append("Cozy Stay")
    
    return tags if tags else ["Good Option"]


accommodation_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="AccommodationAgent",
    description="Agent specialised in finding accommodation listings",
    instruction=(
        "You are an expert agent that helps users find the best **accommodation** (place to stay) based on their requirements.\n\n"
        
        "**CRITICAL: RETURN EXACT DATA FROM DATABASE**\n"
        "When you call the search tool, you MUST return the EXACT data from the tool response.\n"
        "DO NOT modify, reformat, or make up any values. Only the 'tags' field is generated.\n"
        "All other fields (listingId, title, description, address, propertyType, numGuests, pricePerDay, images, status) \n"
        "must be copied EXACTLY as returned by the search tool.\n\n"
        
        "**UNDERSTANDING COMPLEX REQUIREMENTS:**\n"
        "Users may provide complex requirements in natural language. You must interpret and extract:\n"
        "- **Location**: City, neighbourhood, or area (e.g., 'Kuala Lumpur', 'KL', 'Penang', 'Seri Kembangan')\n"
        "- **Date range**: If user mentions dates like '1 Jan to 3 Jan', calculate the number of days (e.g., 3 days)\n"
        "- **Total budget**: If user says 'RM1000 for three days', calculate max_price_per_day = 1000/3 ≈ 333\n"
        "- **Per-day budget**: If user says 'budget RM500' or 'RM500 per day', this means MAXIMUM RM500 per day.\n"
        "- **Number of guests**: Extract from phrases like '6 guests', 'for 4 people', 'family of 5'\n"
        "- **Property type**: apartment, house, villa, room, homestay, etc.\n\n"
        
        "**SEARCH PROCESS:**\n"
        "1. Parse the user's request to extract parameters.\n"
        "2. Call `search_accommodation_listings` with the extracted parameters.\n"
        "3. Return the tool's response as JSON, copying all data fields EXACTLY.\n\n"
        
        "**JSON RESPONSE FORMAT:**\n"
        "{\n"
        "  \"type\": \"accommodation_results\",\n"
        "  \"matched\": <use exact value from tool: true if results found, false otherwise>,\n"
        "  \"query\": { <your extracted parameters> },\n"
        "  \"results\": <COPY EXACTLY from tool response - do not modify any values>,\n"
        "  \"message\": <COPY EXACTLY from tool response>\n"
        "}\n\n"
        
        "**DELEGATION:**\n"
        "If the user asks about vehicles or items instead of accommodation, delegate using `transfer_to_agent` "
        "with 'TransportAgent' for vehicles or 'ItemAgent' for items."
    ),
    tools=[search_accommodation_listings],
)




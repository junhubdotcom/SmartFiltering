"""
accommodation_agent.py
----------------------

Defines the AccommodationAgent for the smart filtering system. This agent
handles user requests for places to stay. It provides a search function
that queries the mock database for accommodation listings and returns
multiple options sorted by suitability. The associated LlmAgent interprets
queries and calls the search tool when needed.
"""

from typing import Optional, Dict, Any, List

from google.adk.agents import LlmAgent

from ..data.mock_db import get_accommodation_listings, Accommodation


def search_accommodation_listings(
    location: Optional[str] = None,
    max_price_per_day: Optional[float] = None,
    property_type: Optional[str] = None,
    num_guests: Optional[int] = None,
    min_rating: Optional[float] = None,
) -> Dict[str, Any]:
    """Search the mock database for accommodation listings.

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
    all_listings: List[Accommodation] = get_accommodation_listings()
    candidates: List[Accommodation] = all_listings.copy()
    
    # Apply filters
    if location:
        candidates = [l for l in candidates if location.lower() in l.location.lower()]
    if max_price_per_day is not None:
        candidates = [l for l in candidates if l.basePrice <= max_price_per_day]
    if property_type:
        candidates = [l for l in candidates if property_type.lower() in l.propertyType.lower()]
    if num_guests:
        candidates = [l for l in candidates if l.numGuests >= num_guests]
    if min_rating is not None:
        candidates = [l for l in candidates if l.averageRating >= min_rating]
    
    if not candidates:
        # No exact matches – return related suggestions from same category
        suggestions_sorted = sorted(
            all_listings,
            key=lambda l: (-l.averageRating, l.basePrice),
        )
        suggestion_data = []
        if suggestions_sorted:
            max_rating_all = max(l.averageRating for l in all_listings)
            min_price_all = min(l.basePrice for l in all_listings)
            for s in suggestions_sorted:
                tags = _generate_tags(s, max_rating_all, min_price_all, all_listings)
                suggestion_data.append({
                    "listingId": s.listingId,
                    "title": s.title,
                    "description": s.description,
                    "location": s.location,
                    "propertyType": s.propertyType,
                    "numGuests": s.numGuests,
                    "pricePerDay": s.basePrice,
                    "rating": s.averageRating,
                    "tier": s.tier,
                    "tags": tags,
                })
        return {
            "matched": False,
            "message": "No accommodations match your exact criteria. Here are related options in the accommodation category:",
            "suggestions": suggestion_data,
        }
    
    # Sort candidates by suitability: highest rating first, then lowest price
    candidates_sorted = sorted(candidates, key=lambda l: (-l.averageRating, l.basePrice))
    
    # Generate result data with tags
    max_rating = max(l.averageRating for l in candidates)
    min_price = min(l.basePrice for l in candidates)
    
    results = []
    for idx, listing in enumerate(candidates_sorted):
        tags = _generate_tags(listing, max_rating, min_price, candidates)
        if idx == 0:
            tags.insert(0, "Most Suitable")
        results.append({
            "listingId": listing.listingId,
            "title": listing.title,
            "description": listing.description,
            "location": listing.location,
            "propertyType": listing.propertyType,
            "numGuests": listing.numGuests,
            "pricePerDay": listing.basePrice,
            "rating": listing.averageRating,
            "tier": listing.tier,
            "tags": tags,
        })
    
    return {
        "matched": True,
        "message": f"Found {len(results)} accommodation(s) matching your criteria, sorted from most suitable:",
        "results": results,
    }


def _generate_tags(listing: Accommodation, max_rating: float, min_price: float, pool: List[Accommodation]) -> List[str]:
    """Generate descriptive tags for why this listing is suitable."""
    tags = []
    
    # Rating-based tags
    if listing.averageRating >= 4.9:
        tags.append("Excellent Rating")
    elif listing.averageRating >= 4.5:
        tags.append("High Rating")
    
    if listing.averageRating >= 0.99 * max_rating:
        tags.append("Top Rated in Results")
    
    # Price-based tags
    if listing.basePrice <= min_price * 1.01:
        tags.append("Cheapest Option")
    elif listing.basePrice <= min_price * 1.2:
        tags.append("Budget Friendly")
    
    # Capacity tags
    if listing.numGuests >= 6:
        tags.append("Great for Groups")
    elif listing.numGuests >= 4:
        tags.append("Family Friendly")
    
    # Tier tags
    if listing.tier:
        tags.append(f"{listing.tier.capitalize()} Tier")
    
    # Value tag (high rating + reasonable price)
    avg_price = sum(l.basePrice for l in pool) / len(pool) if pool else listing.basePrice
    if listing.averageRating >= 4.5 and listing.basePrice <= avg_price:
        tags.append("Great Value")
    
    return tags if tags else ["Good Option"]


accommodation_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="AccommodationAgent",
    description="Agent specialised in finding accommodation listings",
    instruction=(
        "You are an expert agent that helps users find the best **accommodation** (place to stay) based on their requirements.\n\n"
        
        "**CRITICAL: ALL RESPONSES MUST BE IN JSON FORMAT**\n"
        "You must ALWAYS respond with valid JSON. Never use plain text or markdown.\n\n"
        
        "**UNDERSTANDING COMPLEX REQUIREMENTS:**\n"
        "Users may provide complex requirements in natural language. You must interpret and extract:\n"
        "- **Location**: City, neighbourhood, or area (e.g., 'Kuala Lumpur', 'KL', 'Penang')\n"
        "- **Date range**: If user mentions dates like '1 Jan to 3 Jan', calculate the number of days (e.g., 3 days)\n"
        "- **Total budget**: If user says 'RM1000 for three days', calculate max_price_per_day = 1000/3 ≈ 333\n"
        "- **Per-day budget**: If user says 'budget RM500' or 'RM500 per day', this means MAXIMUM RM500 per day (not exact). Use as max_price_per_day.\n"
        "- **Number of guests**: Extract from phrases like '6 guests', 'for 4 people', 'family of 5'\n"
        "- **Property type**: apartment, house, villa, room, homestay, etc.\n"
        "- **Rating requirements**: 'highly rated', '5 star', 'at least 4.5 rating'\n"
        "- **Quality tier**: premium, normal, low\n\n"
        "**IMPORTANT:** When user says 'budget RM500', it means they want options that cost RM500 OR LESS, not exactly RM500.\n\n"
        
        "**SEARCH PROCESS:**\n"
        "1. Carefully parse the user's request to extract all parameters mentioned above.\n"
        "2. Call `search_accommodation_listings` with the extracted parameters.\n"
        "3. The tool returns data that you must format as JSON.\n\n"
        
        "**JSON RESPONSE FORMAT:**\n"
        "Always respond with this exact JSON structure:\n"
        "{\n"
        "  \"type\": \"accommodation_results\",\n"
        "  \"matched\": true/false,\n"
        "  \"query\": {\n"
        "    \"location\": \"extracted location or null\",\n"
        "    \"maxPricePerDay\": number or null,\n"
        "    \"numGuests\": number or null,\n"
        "    \"propertyType\": \"type or null\",\n"
        "    \"numDays\": number or null\n"
        "  },\n"
        "  \"results\": [\n"
        "    {\n"
        "      \"listingId\": \"A001\",\n"
        "      \"title\": \"Listing Title\",\n"
        "      \"description\": \"Description\",\n"
        "      \"location\": \"Location\",\n"
        "      \"propertyType\": \"House\",\n"
        "      \"numGuests\": 6,\n"
        "      \"pricePerDay\": 150.0,\n"
        "      \"totalPrice\": 450.0,\n"
        "      \"rating\": 4.8,\n"
        "      \"tier\": \"normal\",\n"
        "      \"tags\": [\"Most Suitable\", \"High Rating\"]\n"
        "    }\n"
        "  ],\n"
        "  \"message\": \"Found X accommodation(s) matching your criteria\"\n"
        "}\n\n"
        
        "**WHEN NO EXACT MATCHES:**\n"
        "Set \"matched\": false and include suggestions in the \"results\" array with appropriate message.\n\n"
        
        "**DELEGATION:**\n"
        "If the user asks about vehicles or items instead of accommodation, delegate using `transfer_to_agent` "
        "with 'TransportAgent' for vehicles or 'ItemAgent' for items."
    ),
    tools=[search_accommodation_listings],
)




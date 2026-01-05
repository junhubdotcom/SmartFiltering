"""
transport_agent.py
------------------

Defines the TransportAgent for the smart filtering system. This agent is
responsible for handling user requests related to vehicle rentals. It includes
a search function that queries the mock database for transport listings and
returns multiple options sorted by suitability with full details and tags.
"""

from typing import Optional, Dict, Any, List

from google.adk.agents import LlmAgent

from ..data.mock_db import get_transport_listings, Transport


def search_transport_listings(
    location: Optional[str] = None,
    max_price_per_day: Optional[float] = None,
    vehicle_type: Optional[str] = None,
    make: Optional[str] = None,
    model: Optional[str] = None,
    min_year: Optional[int] = None,
    min_rating: Optional[float] = None,
) -> Dict[str, Any]:
    """Search the mock database for transport listings.

    Filters the list of transport listings by optional parameters and returns
    multiple options sorted by suitability (best first), each with full details
    and reason tags. If no listings match, returns related suggestions.

    Args:
        location: Desired city or area.
        max_price_per_day: Maximum acceptable rental price per day.
        vehicle_type: Type of vehicle (e.g. car, motorcycle, van).
        make: Vehicle make (e.g. Toyota, Honda).
        model: Vehicle model (e.g. Camry, City).
        min_year: Minimum year of manufacture.
        min_rating: Minimum acceptable average rating.

    Returns:
        A dictionary with 'results' (list of matching options) or 'suggestions'
        (related options if no exact match).
    """
    all_listings: List[Transport] = get_transport_listings()
    candidates: List[Transport] = all_listings.copy()
    
    # Apply filters
    if location:
        candidates = [l for l in candidates if location.lower() in l.location.lower()]
    if max_price_per_day is not None:
        candidates = [l for l in candidates if l.basePrice <= max_price_per_day]
    if vehicle_type:
        candidates = [l for l in candidates if vehicle_type.lower() in l.vehicleType.lower()]
    if make:
        candidates = [l for l in candidates if make.lower() in l.make.lower()]
    if model:
        candidates = [l for l in candidates if model.lower() in l.model.lower()]
    if min_year:
        candidates = [l for l in candidates if l.year >= min_year]
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
                    "vehicleType": s.vehicleType,
                    "make": s.make,
                    "model": s.model,
                    "year": s.year,
                    "pricePerDay": s.basePrice,
                    "rating": s.averageRating,
                    "tags": tags,
                })
        return {
            "matched": False,
            "message": "No vehicles match your exact criteria. Here are related options in the transport category:",
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
            "vehicleType": listing.vehicleType,
            "make": listing.make,
            "model": listing.model,
            "year": listing.year,
            "pricePerDay": listing.basePrice,
            "rating": listing.averageRating,
            "tags": tags,
        })
    
    return {
        "matched": True,
        "message": f"Found {len(results)} vehicle(s) matching your criteria, sorted from most suitable:",
        "results": results,
    }


def _generate_tags(listing: Transport, max_rating: float, min_price: float, pool: List[Transport]) -> List[str]:
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
    
    # Year-based tags
    current_year = 2026
    if listing.year >= current_year - 2:
        tags.append("Recent Model")
    elif listing.year >= current_year - 5:
        tags.append("Well Maintained")
    
    # Vehicle type tags
    if listing.vehicleType.lower() == "car":
        tags.append("Comfortable Ride")
    elif listing.vehicleType.lower() in ["van", "suv"]:
        tags.append("Spacious")
    elif listing.vehicleType.lower() in ["motorcycle", "bike"]:
        tags.append("Fuel Efficient")
    
    # Value tag (high rating + reasonable price)
    avg_price = sum(l.basePrice for l in pool) / len(pool) if pool else listing.basePrice
    if listing.averageRating >= 4.5 and listing.basePrice <= avg_price:
        tags.append("Great Value")
    
    return tags if tags else ["Good Option"]


transport_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="TransportAgent",
    description="Agent specialised in finding transport/vehicle listings",
    instruction=(
        "You are an expert agent that helps users find the best **transport** (rental vehicle) based on their requirements.\n\n"
        
        "**CRITICAL: ALL RESPONSES MUST BE IN JSON FORMAT**\n"
        "You must ALWAYS respond with valid JSON. Never use plain text or markdown.\n\n"
        
        "**UNDERSTANDING COMPLEX REQUIREMENTS:**\n"
        "Users may provide complex requirements in natural language. You must interpret and extract:\n"
        "- **Location**: City or area (e.g., 'Kuala Lumpur', 'KL', 'Penang')\n"
        "- **Date range**: If user mentions dates like '1 Jan to 5 Jan', calculate number of days (e.g., 5 days)\n"
        "- **Total budget**: If user says 'RM500 for 5 days', calculate max_price_per_day = 500/5 = 100\n"
        "- **Per-day budget**: If user says 'budget RM100' or 'RM100 per day', this means MAXIMUM RM100 per day (not exact). Use as max_price_per_day.\n"
        "- **Vehicle type**: car, motorcycle, van, SUV, bike, etc.\n"
        "- **Make/Brand**: Toyota, Honda, BMW, etc.\n"
        "- **Model**: Camry, City, Civic, etc.\n"
        "- **Year requirement**: 'newer than 2018', 'recent model', '2020 or later'\n"
        "- **Rating requirements**: 'highly rated', 'good reviews', 'at least 4.5 rating'\n\n"
        "**IMPORTANT:** When user says 'budget RM100', it means they want options that cost RM100 OR LESS, not exactly RM100.\n\n"
        
        "**SEARCH PROCESS:**\n"
        "1. Carefully parse the user's request to extract all parameters mentioned above.\n"
        "2. Call `search_transport_listings` with the extracted parameters.\n"
        "3. The tool returns data that you must format as JSON.\n\n"
        
        "**JSON RESPONSE FORMAT:**\n"
        "Always respond with this exact JSON structure:\n"
        "{\n"
        "  \"type\": \"transport_results\",\n"
        "  \"matched\": true/false,\n"
        "  \"query\": {\n"
        "    \"location\": \"extracted location or null\",\n"
        "    \"maxPricePerDay\": number or null,\n"
        "    \"vehicleType\": \"type or null\",\n"
        "    \"make\": \"make or null\",\n"
        "    \"numDays\": number or null\n"
        "  },\n"
        "  \"results\": [\n"
        "    {\n"
        "      \"listingId\": \"T001\",\n"
        "      \"title\": \"Toyota Camry 2018\",\n"
        "      \"description\": \"Description\",\n"
        "      \"location\": \"Kuala Lumpur\",\n"
        "      \"vehicleType\": \"car\",\n"
        "      \"make\": \"Toyota\",\n"
        "      \"model\": \"Camry\",\n"
        "      \"year\": 2018,\n"
        "      \"pricePerDay\": 80.0,\n"
        "      \"totalPrice\": 240.0,\n"
        "      \"rating\": 4.7,\n"
        "      \"tags\": [\"Most Suitable\", \"High Rating\"]\n"
        "    }\n"
        "  ],\n"
        "  \"message\": \"Found X vehicle(s) matching your criteria\"\n"
        "}\n\n"
        
        "**WHEN NO EXACT MATCHES:**\n"
        "Set \"matched\": false and include suggestions in the \"results\" array with appropriate message.\n\n"
        
        "**DELEGATION:**\n"
        "If the user asks about accommodation or items instead of vehicles, delegate using `transfer_to_agent` "
        "with 'AccommodationAgent' for lodging or 'ItemAgent' for items."
    ),
    tools=[search_transport_listings],
)

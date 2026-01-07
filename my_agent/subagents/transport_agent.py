"""
transport_agent.py
------------------

Defines the TransportAgent for the smart filtering system. This agent is
responsible for handling user requests related to vehicle rentals. It includes
a search function that queries the backend API for transport listings and
returns multiple options sorted by suitability with full details and tags.
"""

from typing import Optional, Dict, Any, List

from google.adk.agents import LlmAgent

from ..data.api_client import get_transport_listings


def search_transport_listings(
    location: Optional[str] = None,
    max_price_per_day: Optional[float] = None,
    vehicle_type: Optional[str] = None,
    make: Optional[str] = None,
    model: Optional[str] = None,
    min_year: Optional[int] = None,
    min_rating: Optional[float] = None,
) -> Dict[str, Any]:
    """Search the backend API for transport listings.

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
    # Fetch real listings from backend API
    all_listings = get_transport_listings()
    
    if not all_listings:
        return {
            "message": "No transport listings available. The backend may be unavailable or have no vehicle listings.",
            "results": [],
        }
    
    candidates = all_listings.copy()
    
    # Apply filters - using API response field names
    if location:
        candidates = [l for l in candidates if location.lower() in (l.get("address") or "").lower()]
    if max_price_per_day is not None:
        candidates = [l for l in candidates if float(l.get("basePrice", 0)) <= max_price_per_day]
    if vehicle_type:
        candidates = [l for l in candidates if vehicle_type.lower() in (l.get("vehicleType") or "").lower()]
    if make:
        candidates = [l for l in candidates if make.lower() in (l.get("brand") or "").lower()]
    if model:
        candidates = [l for l in candidates if model.lower() in (l.get("model") or "").lower()]
    if min_year:
        candidates = [l for l in candidates if (l.get("year") or 0) >= min_year]
    
    if not candidates:
        # No exact matches – try to find similar vehicles (same type or brand)
        similar_vehicles = []
        
        # First, try to find vehicles of the same type
        if vehicle_type:
            similar_vehicles = [l for l in all_listings if vehicle_type.lower() in (l.get("vehicleType") or "").lower()]
        
        # If no type matches, try same brand
        if not similar_vehicles and make:
            similar_vehicles = [l for l in all_listings if make.lower() in (l.get("brand") or "").lower()]
        
        # If still no matches, return empty with appropriate message
        if not similar_vehicles:
            search_term = vehicle_type or make or "requested vehicle"
            return {
                "message": f"No {search_term} listings available in our database.",
                "results": [],
            }
        
        # Sort similar vehicles by price
        similar_vehicles_sorted = sorted(similar_vehicles, key=lambda l: float(l.get("basePrice", 0)))
        
        suggestion_data = []
        for s in similar_vehicles_sorted:
            tags = _generate_tags(s, similar_vehicles_sorted)
            suggestion_data.append({
                "listingId": s.get("id"),
                "title": s.get("title"),
                "description": s.get("description"),
                "address": s.get("address"),
                "vehicleType": s.get("vehicleType"),
                "brand": s.get("brand"),
                "model": s.get("model"),
                "year": s.get("year"),
                "pricePerDay": float(s.get("basePrice", 0)),
                "transmission": s.get("transmission"),
                "fuelType": s.get("fuelType"),
                "seats": s.get("seats"),
                "images": s.get("images", []),
                "status": s.get("status"),
                "tags": tags,
            })
        
        search_term = vehicle_type or make or "vehicle"
        return {
            "message": f"No exact match found. Here are other {search_term} options available:",
            "results": suggestion_data,
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
            "vehicleType": listing.get("vehicleType"),
            "brand": listing.get("brand"),
            "model": listing.get("model"),
            "year": listing.get("year"),
            "pricePerDay": float(listing.get("basePrice", 0)),
            "transmission": listing.get("transmission"),
            "fuelType": listing.get("fuelType"),
            "seats": listing.get("seats"),
            "images": listing.get("images", []),
            "status": listing.get("status"),
            "tags": tags,
        })
    
    return {
        "message": f"Found {len(results)} vehicle(s) matching your criteria.",
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
    
    # Year-based tags
    current_year = 2026
    year = listing.get("year")
    if year and year >= current_year - 2:
        tags.append("Recent Model")
    elif year and year >= current_year - 5:
        tags.append("Well Maintained")
    
    # Vehicle type tags
    vehicle_type = (listing.get("vehicleType") or "").lower()
    if vehicle_type == "car":
        tags.append("Comfortable Ride")
    elif vehicle_type in ["van", "suv"]:
        tags.append("Spacious")
    elif vehicle_type in ["motorcycle", "bike"]:
        tags.append("Fuel Efficient")
    
    # Transmission tag
    if listing.get("transmission") == "Automatic":
        tags.append("Easy to Drive")
    
    # Seats tag
    seats = listing.get("seats")
    if seats and seats >= 7:
        tags.append("Great for Groups")
    elif seats and seats >= 5:
        tags.append("Family Friendly")
    
    return tags if tags else ["Good Option"]


transport_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="TransportAgent",
    description="Agent specialised in finding transport/vehicle listings",
    instruction=(
        "You are an expert agent that helps users find the best **transport** (rental vehicle) based on their requirements.\n\n"
        
        "**CRITICAL: RETURN EXACT DATA FROM DATABASE**\n"
        "When you call the search tool, you MUST return the EXACT data from the tool response.\n"
        "DO NOT modify, reformat, or make up any values. Only the 'tags' field is generated.\n"
        "All other fields (listingId, title, description, address, vehicleType, make, model, year, pricePerDay, \n"
        "transmission, fuelType, seats, images, status) must be copied EXACTLY as returned by the search tool.\n\n"
        
        "**UNDERSTANDING COMPLEX REQUIREMENTS:**\n"
        "Users may provide complex requirements in natural language. You must interpret and extract:\n"
        "- **Location**: City or area (e.g., 'Kuala Lumpur', 'KL', 'Penang')\n"
        "- **Date range**: If user mentions dates like '1 Jan to 5 Jan', calculate number of days (e.g., 5 days)\n"
        "- **Total budget**: If user says 'RM500 for 5 days', calculate max_price_per_day = 500/5 = 100\n"
        "- **Per-day budget**: If user says 'budget RM100' or 'RM100 per day', this means MAXIMUM RM100 per day.\n"
        "- **Vehicle type**: car, motorcycle, van, SUV, bike, etc.\n"
        "- **Make/Brand**: Toyota, Honda, BMW, Proton, Perodua, etc.\n"
        "- **Model**: Camry, City, Civic, Saga, Myvi, etc.\n"
        "- **Year requirement**: 'newer than 2018', 'recent model', '2020 or later'\n\n"
        
        "**SEARCH PROCESS:**\n"
        "1. Parse the user's request to extract parameters.\n"
        "2. Call `search_transport_listings` with the extracted parameters.\n"
        "3. Return the tool's response as JSON, copying all data fields EXACTLY.\n\n"
        
        "**JSON RESPONSE FORMAT:**\n"
        "{\n"
        "  \"type\": \"transport_results\",\n"
        "  \"message\": <COPY EXACTLY from tool response>,\n"
        "  \"results\": <COPY EXACTLY from tool response - do not modify any values>\n"
        "}\n\n"
        
        "**DELEGATION:**\n"
        "If the user asks about accommodation or items instead of vehicles, delegate using `transfer_to_agent` "
        "with 'AccommodationAgent' for lodging or 'ItemAgent' for items."
    ),
    tools=[search_transport_listings],
)

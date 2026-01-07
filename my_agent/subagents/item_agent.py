"""
item_agent.py
--------------

Defines the ItemAgent for the smart filtering system. This agent handles
requests to rent miscellaneous items (electronics, tools, etc.). It provides a
search function that queries the backend API for item listings and returns
multiple options sorted by suitability with full details and tags.
"""

from typing import Optional, Dict, Any, List

from google.adk.agents import LlmAgent

from ..data.api_client import get_item_listings


def search_item_listings(
    location: Optional[str] = None,
    max_price_per_day: Optional[float] = None,
    item_category: Optional[str] = None,
    min_rating: Optional[float] = None,
    keyword: Optional[str] = None,
) -> Dict[str, Any]:
    """Search the backend API for item listings.

    Filters the list of item listings by optional parameters and returns
    multiple options sorted by suitability (best first), each with full details
    and reason tags. If no listings match, returns related suggestions.

    Args:
        location: Desired city or area.
        max_price_per_day: Maximum acceptable rental price per day.
        item_category: Category of item (e.g. Electronics, Tools, Furniture).
        min_rating: Minimum acceptable average rating.
        keyword: Keyword to search in title or description.

    Returns:
        A dictionary with 'results' (list of matching options) or 'suggestions'
        (related options if no exact match).
    """
    # Fetch real listings from backend API
    all_listings = get_item_listings()
    
    if not all_listings:
        return {
            "message": "No item listings available. The backend may be unavailable or have no item listings.",
            "results": [],
        }
    
    candidates = all_listings.copy()
    
    # Apply filters - using API response field names
    if location:
        candidates = [l for l in candidates if location.lower() in (l.get("address") or "").lower()]
    if max_price_per_day is not None:
        candidates = [l for l in candidates if float(l.get("basePrice", 0)) <= max_price_per_day]
    if item_category:
        candidates = [l for l in candidates if item_category.lower() in (l.get("category") or "").lower()]
    if keyword:
        keyword_lower = keyword.lower()
        candidates = [l for l in candidates if keyword_lower in (l.get("title") or "").lower() or keyword_lower in (l.get("description") or "").lower()]
    
    if not candidates:
        # No exact matches – try to find similar items (same category or keyword)
        similar_items = []
        
        # First, try to find items matching the keyword in title/description
        if keyword:
            keyword_lower = keyword.lower()
            similar_items = [l for l in all_listings if keyword_lower in (l.get("title") or "").lower() or keyword_lower in (l.get("description") or "").lower()]
        
        # If no keyword matches, try same category
        if not similar_items and item_category:
            similar_items = [l for l in all_listings if item_category.lower() in (l.get("category") or "").lower()]
        
        # If still no matches, return empty with appropriate message
        if not similar_items:
            search_term = keyword or item_category or "requested item"
            return {
                "message": f"No {search_term} listings available in our database.",
                "results": [],
            }
        
        # Sort similar items by price
        similar_items_sorted = sorted(similar_items, key=lambda l: float(l.get("basePrice", 0)))
        
        suggestion_data = []
        for s in similar_items_sorted:
            tags = _generate_tags(s, similar_items_sorted)
            suggestion_data.append({
                "listingId": s.get("id"),
                "title": s.get("title"),
                "description": s.get("description"),
                "address": s.get("address"),
                "category": s.get("category"),
                "brand": s.get("brand"),
                "model": s.get("model"),
                "condition": s.get("condition"),
                "pricePerDay": float(s.get("basePrice", 0)),
                "images": s.get("images", []),
                "status": s.get("status"),
                "tags": tags,
            })
        
        search_term = keyword or item_category or "item"
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
            "category": listing.get("category"),
            "brand": listing.get("brand"),
            "model": listing.get("model"),
            "condition": listing.get("condition"),
            "pricePerDay": float(listing.get("basePrice", 0)),
            "images": listing.get("images", []),
            "status": listing.get("status"),
            "tags": tags,
        })
    
    return {
        "message": f"Found {len(results)} item(s) matching your criteria.",
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
    
    # Category-based tags
    category = (listing.get("category") or "").lower()
    if category == "electronics":
        tags.append("Tech Gear")
    elif category == "tools":
        tags.append("DIY Essential")
    elif category == "furniture":
        tags.append("Home & Living")
    elif category == "sports":
        tags.append("Active Lifestyle")
    elif "camera" in category or "camera" in (listing.get("title") or "").lower():
        tags.append("Photography Gear")
    
    # Condition tags
    condition = (listing.get("condition") or "").lower()
    if condition in ["new", "excellent"]:
        tags.append("Like New")
    elif condition == "good":
        tags.append("Good Condition")
    
    # Brand tag
    if listing.get("brand"):
        tags.append(f"{listing.get('brand')} Brand")
    
    return tags if tags else ["Good Option"]


item_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="ItemAgent",
    description="Agent specialised in finding rental items",
    instruction=(
        "You are an expert agent that helps users find the best **items** to rent based on their requirements.\n\n"
        
        "**CRITICAL: RETURN EXACT DATA FROM DATABASE**\n"
        "When you call the search tool, you MUST return the EXACT data from the tool response.\n"
        "DO NOT modify, reformat, or make up any values. Only the 'tags' field is generated.\n"
        "All other fields (listingId, title, description, address, itemCategory, brand, model, \n"
        "condition, pricePerDay, images, status) must be copied EXACTLY as returned by the search tool.\n\n"
        
        "**UNDERSTANDING COMPLEX REQUIREMENTS:**\n"
        "Users may provide complex requirements in natural language. You must interpret and extract:\n"
        "- **Location**: City or area (e.g., 'Kuala Lumpur', 'KL', 'Penang')\n"
        "- **Date range**: If user mentions dates like '1 Jan to 3 Jan', calculate number of days (e.g., 3 days)\n"
        "- **Total budget**: If user says 'RM300 for a week', calculate max_price_per_day = 300/7 ≈ 43\n"
        "- **Per-day budget**: If user says 'budget RM50' or 'RM50 per day', this means MAXIMUM RM50 per day.\n"
        "- **Item category**: Electronics, Tools, Furniture, Sports, Camera, etc.\n"
        "- **Specific item**: Extract keywords like 'camera', 'drill', 'projector', 'laptop'\n\n"
        
        "**SEARCH PROCESS:**\n"
        "1. Parse the user's request to extract parameters.\n"
        "2. Call `search_item_listings` with the extracted parameters.\n"
        "3. Return the tool's response as JSON, copying all data fields EXACTLY.\n\n"
        
        "**JSON RESPONSE FORMAT:**\n"
        "{\n"
        "  \"type\": \"item_results\",\n"
        "  \"message\": <COPY EXACTLY from tool response>,\n"
        "  \"results\": <COPY EXACTLY from tool response - do not modify any values>\n"
        "}\n\n"
        
        "**DELEGATION:**\n"
        "If the user asks about vehicles or accommodation instead of items, delegate using `transfer_to_agent` "
        "with 'TransportAgent' for vehicles or 'AccommodationAgent' for lodging."
    ),
    tools=[search_item_listings],
)

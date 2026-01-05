"""
item_agent.py
--------------

Defines the ItemAgent for the smart filtering system. This agent handles
requests to rent miscellaneous items (electronics, tools, etc.). It provides a
search function that queries the mock database for item listings and returns
multiple options sorted by suitability with full details and tags.
"""

from typing import Optional, Dict, Any, List

from google.adk.agents import LlmAgent

from ..data.mock_db import get_item_listings, Item


def search_item_listings(
    location: Optional[str] = None,
    max_price_per_day: Optional[float] = None,
    item_category: Optional[str] = None,
    min_rating: Optional[float] = None,
    keyword: Optional[str] = None,
) -> Dict[str, Any]:
    """Search the mock database for item listings.

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
    all_listings: List[Item] = get_item_listings()
    candidates: List[Item] = all_listings.copy()
    
    # Apply filters
    if location:
        candidates = [l for l in candidates if location.lower() in l.location.lower()]
    if max_price_per_day is not None:
        candidates = [l for l in candidates if l.basePrice <= max_price_per_day]
    if item_category:
        candidates = [l for l in candidates if item_category.lower() in l.itemCategory.lower()]
    if min_rating is not None:
        candidates = [l for l in candidates if l.averageRating >= min_rating]
    if keyword:
        keyword_lower = keyword.lower()
        candidates = [l for l in candidates if keyword_lower in l.title.lower() or keyword_lower in l.description.lower()]
    
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
                    "itemCategory": s.itemCategory,
                    "pricePerDay": s.basePrice,
                    "rating": s.averageRating,
                    "tags": tags,
                })
        return {
            "matched": False,
            "message": "No items match your exact criteria. Here are related options in the item category:",
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
            "itemCategory": listing.itemCategory,
            "pricePerDay": listing.basePrice,
            "rating": listing.averageRating,
            "tags": tags,
        })
    
    return {
        "matched": True,
        "message": f"Found {len(results)} item(s) matching your criteria, sorted from most suitable:",
        "results": results,
    }


def _generate_tags(listing: Item, max_rating: float, min_price: float, pool: List[Item]) -> List[str]:
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
    
    # Category-based tags
    category_lower = listing.itemCategory.lower()
    if category_lower == "electronics":
        tags.append("Tech Gear")
    elif category_lower == "tools":
        tags.append("DIY Essential")
    elif category_lower == "furniture":
        tags.append("Home & Living")
    elif category_lower == "sports":
        tags.append("Active Lifestyle")
    
    # Value tag (high rating + reasonable price)
    avg_price = sum(l.basePrice for l in pool) / len(pool) if pool else listing.basePrice
    if listing.averageRating >= 4.5 and listing.basePrice <= avg_price:
        tags.append("Great Value")
    
    return tags if tags else ["Good Option"]


item_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="ItemAgent",
    description="Agent specialised in finding rental items",
    instruction=(
        "You are an expert agent that helps users find the best **items** to rent based on their requirements.\n\n"
        
        "**CRITICAL: ALL RESPONSES MUST BE IN JSON FORMAT**\n"
        "You must ALWAYS respond with valid JSON. Never use plain text or markdown.\n\n"
        
        "**UNDERSTANDING COMPLEX REQUIREMENTS:**\n"
        "Users may provide complex requirements in natural language. You must interpret and extract:\n"
        "- **Location**: City or area (e.g., 'Kuala Lumpur', 'KL', 'Penang')\n"
        "- **Date range**: If user mentions dates like '1 Jan to 3 Jan', calculate number of days (e.g., 3 days)\n"
        "- **Total budget**: If user says 'RM300 for a week', calculate max_price_per_day = 300/7 ≈ 43\n"
        "- **Per-day budget**: If user says 'budget RM50' or 'RM50 per day', this means MAXIMUM RM50 per day (not exact). Use as max_price_per_day.\n"
        "- **Item category**: Electronics, Tools, Furniture, Sports, Camera, etc.\n"
        "- **Specific item**: Extract keywords like 'camera', 'drill', 'projector', 'laptop'\n"
        "- **Rating requirements**: 'highly rated', 'good condition', 'at least 4.5 rating'\n"
        "- **Purpose/use case**: 'for a wedding', 'for DIY project', 'for photography'\n\n"
        "**IMPORTANT:** When user says 'budget RM50', it means they want options that cost RM50 OR LESS, not exactly RM50.\n\n"
        
        "**SEARCH PROCESS:**\n"
        "1. Carefully parse the user's request to extract all parameters mentioned above.\n"
        "2. Call `search_item_listings` with the extracted parameters.\n"
        "3. The tool returns data that you must format as JSON.\n\n"
        
        "**JSON RESPONSE FORMAT:**\n"
        "Always respond with this exact JSON structure:\n"
        "{\n"
        "  \"type\": \"item_results\",\n"
        "  \"matched\": true/false,\n"
        "  \"query\": {\n"
        "    \"location\": \"extracted location or null\",\n"
        "    \"maxPricePerDay\": number or null,\n"
        "    \"itemCategory\": \"category or null\",\n"
        "    \"keyword\": \"search keyword or null\",\n"
        "    \"numDays\": number or null\n"
        "  },\n"
        "  \"results\": [\n"
        "    {\n"
        "      \"listingId\": \"I001\",\n"
        "      \"title\": \"Canon DSLR Camera\",\n"
        "      \"description\": \"Description\",\n"
        "      \"location\": \"Kuala Lumpur\",\n"
        "      \"itemCategory\": \"Electronics\",\n"
        "      \"pricePerDay\": 60.0,\n"
        "      \"totalPrice\": 180.0,\n"
        "      \"rating\": 4.8,\n"
        "      \"tags\": [\"Most Suitable\", \"High Rating\"]\n"
        "    }\n"
        "  ],\n"
        "  \"message\": \"Found X item(s) matching your criteria\"\n"
        "}\n\n"
        
        "**WHEN NO EXACT MATCHES:**\n"
        "Set \"matched\": false and include suggestions in the \"results\" array with appropriate message.\n\n"
        
        "**DELEGATION:**\n"
        "If the user asks about vehicles or accommodation instead of items, delegate using `transfer_to_agent` "
        "with 'TransportAgent' for vehicles or 'AccommodationAgent' for lodging."
    ),
    tools=[search_item_listings],
)

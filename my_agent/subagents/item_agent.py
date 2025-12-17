"""
item_agent.py
--------------

Defines the ItemAgent for the smart filtering system. This agent handles
requests to rent miscellaneous items (electronics, tools, etc.). It provides a
search function that queries the mock database for item listings and returns
the best match. The LlmAgent uses this function to fulfil user queries.
"""

from typing import Optional, Dict, Any, List

from google.adk.agents import LlmAgent

from ..data.mock_db import get_item_listings, Item
def search_item_listings(
    location: Optional[str] = None,
    max_price: Optional[float] = None,
    item_category: Optional[str] = None,
) -> Dict[str, Any]:
    """Search the mock database for the best item listing.

    Filters the list of item listings by optional parameters and returns
    a dictionary summarising the top result along with a short reason tag.
    If no listings match, returns an error message.

    Args:
        location: Desired city or area.
        max_price: Maximum acceptable rental price.
        item_category: Category of item (e.g. Electronics, Tools).

    Returns:
        A dictionary with keys 'listingId', 'title', 'location', 'basePrice'
        and 'reason', or an 'error' key if no result is found.
    """
    candidates: List[Item] = get_item_listings()
    if location:
        candidates = [l for l in candidates if location.lower() in l.location.lower()]
    if max_price is not None:
        candidates = [l for l in candidates if l.basePrice <= max_price]
    if item_category:
        candidates = [l for l in candidates if item_category.lower() in l.itemCategory.lower()]
    if not candidates:
        # No exact matches – prepare suggestions from the full item list
        all_listings: List[Item] = get_item_listings()
        suggestions_sorted = sorted(
            all_listings,
            key=lambda l: (-(l.averageRating * 2.0 - l.basePrice / 100.0), l.basePrice),
        )
        suggestions = suggestions_sorted[:3]
        suggestion_data = []
        if suggestions:
            max_rating_all = max(l.averageRating for l in all_listings)
            min_price_all = min(l.basePrice for l in all_listings)
            for s in suggestions:
                tag = "Related"
                if s.averageRating >= 4.5 and s.averageRating >= 0.99 * max_rating_all:
                    tag = "High Rating"
                elif s.basePrice <= min_price_all * 1.01:
                    tag = "Cheap"
                suggestion_data.append(
                    {
                        "listingId": s.listingId,
                        "title": s.title,
                        "location": s.location,
                        "basePrice": s.basePrice,
                        "reason": tag,
                    }
                )
        return {
            "error": "No matching item listings found.",
            "suggestions": suggestion_data,
        }
    best: Optional[Item] = None
    best_score = float("-inf")
    max_rating = max(l.averageRating for l in candidates)
    for listing in candidates:
        score = listing.averageRating * 2.0 - listing.basePrice / 100.0
        if score > best_score:
            best_score = score
            best = listing
    reason = "Best Match"
    if best:
        if best.averageRating >= 4.5 and best.averageRating >= 0.99 * max_rating:
            reason = "High Rating"
        else:
            min_price = min(l.basePrice for l in candidates)
            if best.basePrice <= min_price * 1.01:
                reason = "Cheap"
    return {
        "listingId": best.listingId,
        "title": best.title,
        "location": best.location,
        "basePrice": best.basePrice,
        "reason": reason,
    }


item_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="ItemAgent",
    description="Agent specialised in finding rental items",
    instruction=(
        "You are an agent that helps users find the best **item** to rent based on their requirements.\n"
        "When the user describes what they need (e.g. 'rent a DSLR camera in KL'), follow these steps:\n"
        "1. Extract search parameters from the request: the category of item (e.g., Electronics, Furniture), location, and maximum price if provided.\n"
        "2. Use the `search_item_listings` tool with the extracted filters to find the most suitable item.\n"
        "3. If a listing is found, reply with the item's title, location, price and a short reason tag such as Cheap or High Rating.\n"
        "4. If no item matches, apologise and then offer some alternative item options from the suggestions returned by the tool. "
        "List each suggestion with its title, location, price and reason tag (e.g., High Rating or Cheap).\n"
        "Do not answer questions outside of item rentals yourself. If the user asks about vehicles or accommodation instead of items, "
        "delegate the conversation by calling `transfer_to_agent` with 'TransportAgent' for vehicles or 'AccommodationAgent' for lodging. "
        "This ensures the user is redirected to the proper specialist."
    ),
    tools=[search_item_listings],
)
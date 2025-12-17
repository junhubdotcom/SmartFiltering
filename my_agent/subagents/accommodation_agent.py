"""
accommodation_agent.py
----------------------

Defines the AccommodationAgent for the smart filtering system. This agent
handles user requests for places to stay. It provides a search function
that queries the mock database for accommodation listings and returns the
best match based on user criteria. The associated LlmAgent interprets
queries and calls the search tool when needed.
"""

from typing import Optional, Dict, Any, List

from google.adk.agents import LlmAgent

from ..data.mock_db import get_accommodation_listings, Accommodation


def search_accommodation_listings(
    location: Optional[str] = None,
    max_price: Optional[float] = None,
    property_type: Optional[str] = None,
    num_guests: Optional[int] = None,
) -> Dict[str, Any]:
    """Search the mock database for the best accommodation listing.

    Filters the list of accommodation listings by optional parameters and
    returns a dictionary summarising the top result along with a short
    reason tag. If no listings match, returns an error message.

    Args:
        location: Desired city or neighbourhood.
        max_price: Maximum acceptable rental price.
        property_type: Type of property (e.g. Apartment, House).
        num_guests: Minimum number of guests the place must accommodate.

    Returns:
        A dictionary with keys 'listingId', 'title', 'location', 'basePrice'
        and 'reason', or an 'error' key if no result is found.
    """
    candidates: List[Accommodation] = get_accommodation_listings()
    if location:
        candidates = [l for l in candidates if location.lower() in l.location.lower()]
    if max_price is not None:
        candidates = [l for l in candidates if l.basePrice <= max_price]
    if property_type:
        candidates = [l for l in candidates if property_type.lower() in l.propertyType.lower()]
    if num_guests:
        candidates = [l for l in candidates if l.numGuests >= num_guests]
    if not candidates:
        # No exact matches – prepare suggestions from the full accommodation list
        all_listings: List[Accommodation] = get_accommodation_listings()
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
            "error": "No matching accommodation listings found.",
            "suggestions": suggestion_data,
        }
    best: Optional[Accommodation] = None
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


accommodation_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="AccommodationAgent",
    description="Agent specialised in finding accommodation listings",
    instruction=(
        "You are an agent that helps users find the best **accommodation** (place to stay) based on their requirements.\n"
        "When the user describes what they need (e.g. 'an apartment for 3 people in KL'), follow these steps:\n"
        "1. Extract relevant search parameters: location (city or neighbourhood), maximum price, property type (apartment, house, etc.), and number of guests.\n"
        "2. Call the `search_accommodation_listings` tool with these parameters to retrieve the best match.\n"
        "3. If a listing is found, summarise the recommendation with its title, location, price, and a short reason tag in parentheses (e.g., Cheap or High Rating).\n"
        "4. If no listing matches the criteria, apologise and then present some alternative accommodation options from the suggestions returned by the tool. "
        "Include each suggestion's title, location, price and reason tag (e.g., High Rating or Cheap).\n"
        "Do not handle requests outside of accommodations yourself. If the user asks about vehicles or other items instead of lodging, "
        "delegate the conversation by calling `transfer_to_agent` with 'TransportAgent' for vehicles or 'ItemAgent' for items. "
        "This way, the user will be passed to the correct agent."
    ),
    tools=[search_accommodation_listings],
)




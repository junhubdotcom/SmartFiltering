"""
transport_agent.py
------------------

Defines the TransportAgent for the smart filtering system. This agent is
responsible for handling user requests related to vehicle rentals. It includes
a search function that queries the mock database for transport listings and
returns the best match based on user‑provided criteria.

To run this agent, ensure that `mock_db.py` is available in the Python path
and that the Agent Development Kit (ADK) is installed. The agent uses
Google's LlmAgent class to interpret queries and decide when to call its
search tool.
"""

from typing import Optional, Dict, Any, List

from google.adk.agents import LlmAgent

from ..data.mock_db import get_transport_listings, Transport


def search_transport_listings(
    location: Optional[str] = None,
    max_price: Optional[float] = None,
    vehicle_type: Optional[str] = None,
    make: Optional[str] = None,
    model: Optional[str] = None,
    year: Optional[int] = None,
) -> Dict[str, Any]:
    """Search the mock database for the best transport listing.

    Filters the list of transport listings by optional parameters and returns
    a dictionary summarising the top result along with a short reason tag. If
    no listings match, returns an error message.

    Args:
        location: Desired city or area.
        max_price: Maximum acceptable rental price.
        vehicle_type: Type of vehicle (e.g. car, motorcycle).
        make: Vehicle make (e.g. Toyota).
        model: Vehicle model (e.g. Camry).
        year: Desired year of manufacture.

    Returns:
        A dictionary with keys 'listingId', 'title', 'location', 'basePrice'
        and 'reason', or an 'error' key if no result is found.
    """
    candidates: List[Transport] = get_transport_listings()
    # Apply filters conditionally
    if location:
        candidates = [l for l in candidates if location.lower() in l.location.lower()]
    if max_price is not None:
        candidates = [l for l in candidates if l.basePrice <= max_price]
    if vehicle_type:
        candidates = [l for l in candidates if vehicle_type.lower() in l.vehicleType.lower()]
    if make:
        candidates = [l for l in candidates if make.lower() in l.make.lower()]
    if model:
        candidates = [l for l in candidates if model.lower() in l.model.lower()]
    if year:
        candidates = [l for l in candidates if l.year == year]
    # No matches?
    if not candidates:
        # No exact matches – prepare suggestions from the full transport list
        all_listings: List[Transport] = get_transport_listings()
        # Sort by the same scoring heuristic: high rating, low price
        suggestions_sorted = sorted(
            all_listings,
            key=lambda l: (-(l.averageRating * 2.0 - l.basePrice / 100.0), l.basePrice),
        )
        # Select up to three suggestions
        suggestions = suggestions_sorted[:3]
        # Compute reason tags for suggestions
        suggestion_data = []
        if suggestions:
            # Determine high rating threshold and min price for suggestions
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
            "error": "No matching transport listings found.",
            "suggestions": suggestion_data,
        }
    # Select the best listing by simple heuristic (high rating, low price)
    best: Optional[Transport] = None
    best_score = float("-inf")
    max_rating = max(l.averageRating for l in candidates)
    for listing in candidates:
        score = listing.averageRating * 2.0 - listing.basePrice / 100.0
        if score > best_score:
            best_score = score
            best = listing
    # Create a reason tag
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


# Define the transport agent using the ADK LlmAgent
transport_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="TransportAgent",
    description="Agent specialised in finding transport/vehicle listings",
    instruction=(
        "You are an agent that helps users find the best **transport** listing (rental vehicle) based on their requirements.\n"
        "When the user describes what they need (e.g. 'I need a car in KL for under 100'), follow these steps:\n"
        "1. Extract relevant search parameters from the request: location (city or area), maximum price, vehicle type, make, model or year if specified.\n"
        "2. Call the `search_transport_listings` function tool with the extracted parameters to retrieve the best match from the database.\n"
        "3. If a listing is found, respond concisely with the listing's title, location, price, and a short tag in parentheses explaining why it's recommended (e.g., Cheap if it's low priced or High Rating if it has excellent reviews).\n"
        "4. If no suitable listing is found, apologise and then present some alternative transport options from the suggestions returned by the tool. "
        "For each suggestion, include its title, location, price and reason tag (e.g., High Rating or Cheap).\n"
        "Do not answer queries outside of transport rentals yourself. If the user's request is unrelated to vehicles (for example, if they ask about places to stay or other items), "
        "delegate the conversation to the appropriate agent by calling `transfer_to_agent` with 'AccommodationAgent' or 'ItemAgent' as appropriate. "
        "This ensures the user is redirected to the right specialist."
    ),
    tools=[search_transport_listings],
)

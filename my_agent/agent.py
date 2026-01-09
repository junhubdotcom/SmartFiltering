"""
root_agent.py
-------------

Defines the SmartFilterRootAgent that coordinates queries for the smart filtering
system. This agent routes incoming user messages to specialised sub‑agents
based on the category of the request (transport, accommodation or items) and
handles greetings or clarifications. It uses the `transfer_to_agent` directive
understood by the ADK framework to delegate control to sub‑agents when
necessary.
"""

from typing import Optional, Dict, Any, List

from google.adk.agents import LlmAgent

from .subagents.transport_agent import transport_agent, search_transport_listings
from .subagents.accommodation_agent import accommodation_agent, search_accommodation_listings
from .subagents.item_agent import item_agent, search_item_listings


def search_with_combined_budget(
    total_budget: float,
    num_days: int = 1,
    search_transport: bool = False,
    search_accommodation: bool = False,
    search_items: bool = False,
    location: Optional[str] = None,
    # Transport specific
    vehicle_type: Optional[str] = None,
    make: Optional[str] = None,
    # Accommodation specific
    property_type: Optional[str] = None,
    max_guests: Optional[int] = None,
    # Item specific
    item_category: Optional[str] = None,
    keyword: Optional[str] = None,
) -> Dict[str, Any]:
    """Search multiple categories with a COMBINED/TOTAL budget across all categories.
    
    Use this when the user provides ONE total budget for multiple categories.
    Example: "I want a car and homestay in Selangor for 2 days with budget RM1000"
    
    This function finds COMBINATIONS that fit within the total budget.
    
    Args:
        total_budget: The TOTAL budget across all categories for the entire duration.
        num_days: Number of rental days (used to calculate total cost).
        search_transport: Set to True to include vehicles.
        search_accommodation: Set to True to include accommodations.
        search_items: Set to True to include items.
        location: Desired city or area (applies to all categories).
        vehicle_type: Type of vehicle (car, motorcycle, van, etc.).
        make: Vehicle brand (Toyota, Honda, etc.).
        property_type: Type of property (room, apartment, homestay, etc.).
        max_guests: Minimum guest capacity for accommodation.
        item_category: Category of item (Electronics, Tools, etc.).
        keyword: Keyword to search in item title/description.
    
    Returns:
        A dictionary with suggested combinations that fit within the total budget.
    """
    # Calculate max price per day per category (rough split for initial search)
    categories_count = sum([search_transport, search_accommodation, search_items])
    if categories_count == 0:
        return {
            "type": "error",
            "message": "Please specify at least one category to search."
        }
    
    # Get all available listings from each category (no price filter initially)
    transport_listings = []
    accommodation_listings = []
    item_listings = []
    
    if search_transport:
        transport_results = search_transport_listings(
            location=location,
            max_price_per_day=None,  # Get all, filter later
            vehicle_type=vehicle_type,
            make=make,
        )
        transport_listings = transport_results.get("results", [])
    
    if search_accommodation:
        accommodation_results = search_accommodation_listings(
            location=location,
            max_price_per_day=None,  # Get all, filter later
            property_type=property_type,
            max_guests=max_guests,
        )
        accommodation_listings = accommodation_results.get("results", [])
    
    if search_items:
        item_results = search_item_listings(
            location=location,
            max_price_per_day=None,  # Get all, filter later
            item_category=item_category,
            keyword=keyword,
        )
        item_listings = item_results.get("results", [])
    
    # Generate combinations that fit within budget
    combinations = []
    
    def calculate_total_cost(items: List[Dict]) -> float:
        return sum(item.get("pricePerDay", 0) for item in items) * num_days
    
    def create_combination(combo_items: List[tuple], total_cost: float) -> Dict:
        """Create a combination with organized items array structure."""
        items_list = []
        for category, listing in combo_items:
            item_entry = {"category": category}
            item_entry.update(listing)
            items_list.append(item_entry)
        
        return {
            "totalCost": total_cost,
            "totalCostPerDay": round(total_cost / num_days, 2),
            "numDays": num_days,
            "remainingBudget": round(total_budget - total_cost, 2),
            "items": items_list
        }
    
    # Generate valid combinations based on which categories are searched
    if search_transport and search_accommodation and not search_items:
        # Car + Accommodation combinations
        for transport in transport_listings:
            for accommodation in accommodation_listings:
                total_cost = calculate_total_cost([transport, accommodation])
                if total_cost <= total_budget:
                    combinations.append(create_combination([
                        ("transport", transport),
                        ("accommodation", accommodation)
                    ], total_cost))
    
    elif search_transport and search_items and not search_accommodation:
        # Car + Item combinations
        for transport in transport_listings:
            for item in item_listings:
                total_cost = calculate_total_cost([transport, item])
                if total_cost <= total_budget:
                    combinations.append(create_combination([
                        ("transport", transport),
                        ("item", item)
                    ], total_cost))
    
    elif search_accommodation and search_items and not search_transport:
        # Accommodation + Item combinations
        for accommodation in accommodation_listings:
            for item in item_listings:
                total_cost = calculate_total_cost([accommodation, item])
                if total_cost <= total_budget:
                    combinations.append(create_combination([
                        ("accommodation", accommodation),
                        ("item", item)
                    ], total_cost))
    
    elif search_transport and search_accommodation and search_items:
        # All three categories
        for transport in transport_listings:
            for accommodation in accommodation_listings:
                for item in item_listings:
                    total_cost = calculate_total_cost([transport, accommodation, item])
                    if total_cost <= total_budget:
                        combinations.append(create_combination([
                            ("transport", transport),
                            ("accommodation", accommodation),
                            ("item", item)
                        ], total_cost))
    
    # Sort combinations by total cost (cheapest first, best value)
    combinations.sort(key=lambda x: x["totalCost"])
    
    # Limit to top 10 combinations
    combinations = combinations[:10]
    
    # Add recommendation tags to combinations
    for i, combo in enumerate(combinations):
        tags = []
        if i == 0:
            tags.append("Best Value")
        if combo["remainingBudget"] >= total_budget * 0.2:
            tags.append("Budget Saver")
        if combo["totalCost"] <= total_budget * 0.5:
            tags.append("Under Half Budget")
        combo["tags"] = tags
    
    if not combinations:
        return {
            "type": "combined_budget_results",
            "message": f"No combinations found within your budget of RM{total_budget} for {num_days} day(s).",
            "totalBudget": total_budget,
            "numDays": num_days,
            "combinations": []
        }
    
    return {
        "type": "combined_budget_results",
        "message": f"Found {len(combinations)} combination(s) within your budget of RM{total_budget} for {num_days} day(s).",
        "totalBudget": total_budget,
        "numDays": num_days,
        "combinations": combinations
    }


def search_multiple_categories(
    search_transport: bool = False,
    search_accommodation: bool = False,
    search_items: bool = False,
    # Transport specific parameters
    transport_location: Optional[str] = None,
    transport_max_price: Optional[float] = None,
    vehicle_type: Optional[str] = None,
    make: Optional[str] = None,
    # Accommodation specific parameters
    accommodation_location: Optional[str] = None,
    accommodation_max_price: Optional[float] = None,
    property_type: Optional[str] = None,
    max_guests: Optional[int] = None,
    # Item specific parameters
    item_location: Optional[str] = None,
    item_max_price: Optional[float] = None,
    item_category: Optional[str] = None,
    keyword: Optional[str] = None,
) -> Dict[str, Any]:
    """Search multiple categories at once with SEPARATE criteria for each category.
    
    Use this when the user wants to find multiple types of rentals in one request.
    Each category can have its OWN location and budget.
    
    For example: "I need a car in KL for RM50, a room in Seri Kembangan for RM200, and a camera in Selangor"
    
    Args:
        search_transport: Set to True to search for vehicles.
        search_accommodation: Set to True to search for accommodations.
        search_items: Set to True to search for items.
        transport_location: Location for transport search.
        transport_max_price: Max price per day for transport.
        vehicle_type: Type of vehicle (car, motorcycle, van, etc.).
        make: Vehicle brand (Toyota, Honda, etc.).
        accommodation_location: Location for accommodation search.
        accommodation_max_price: Max price per day for accommodation.
        property_type: Type of property (room, apartment, house, etc.).
        max_guests: Minimum guest capacity for accommodation.
        item_location: Location for item search.
        item_max_price: Max price per day for items.
        item_category: Category of item (Electronics, Tools, etc.).
        keyword: Keyword to search in item title/description (e.g., 'camera', 'guitar').
    
    Returns:
        A dictionary with results from each requested category.
    """
    results_list = []
    categories_searched = []
    
    if search_transport:
        transport_results = search_transport_listings(
            location=transport_location,
            max_price_per_day=transport_max_price,
            vehicle_type=vehicle_type,
            make=make,
        )
        results_list.append({
            "category": "transport",
            "message": transport_results.get("message"),
            "results": transport_results.get("results", [])
        })
        categories_searched.append("transport")
    
    if search_accommodation:
        accommodation_results = search_accommodation_listings(
            location=accommodation_location,
            max_price_per_day=accommodation_max_price,
            property_type=property_type,
            max_guests=max_guests,
        )
        results_list.append({
            "category": "accommodation",
            "message": accommodation_results.get("message"),
            "results": accommodation_results.get("results", [])
        })
        categories_searched.append("accommodation")
    
    if search_items:
        item_results = search_item_listings(
            location=item_location,
            max_price_per_day=item_max_price,
            item_category=item_category,
            keyword=keyword,
        )
        results_list.append({
            "category": "items",
            "message": item_results.get("message"),
            "results": item_results.get("results", [])
        })
        categories_searched.append("items")
    
    if not categories_searched:
        return {
            "type": "error",
            "message": "Please specify at least one category to search (transport, accommodation, or items)."
        }
    
    return {
        "type": "multi_category_results",
        "message": f"Here are the results for: {', '.join(categories_searched)}",
        "results": results_list
    }


root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="SmartFilterRootAgent",
    description="Routes listing queries to the correct specialist agent or prompts for rental requirements.",
    instruction=(
        "You are the central coordinator for iShare's smart filtering system.\n"
        "Your mission is to understand each user message, decide whether to respond yourself or delegate, "
        "and ensure the conversation flows smoothly between the user and the specialist agents.\n\n"
        
        "**CRITICAL: ALL RESPONSES MUST BE IN JSON FORMAT**\n"
        "Every response you give must be valid JSON. No plain text responses.\n\n"
        
        "**UNDERSTANDING COMPLEX USER REQUESTS:**\n"
        "Users may provide detailed, complex requirements in natural language. Examples:\n"
        "- 'I want to find a room in Kuala Lumpur from 1 Jan to 3 Jan 2026, 6 guests, maximum budget RM1000 for three days'\n"
        "- 'Need a car in KL for the weekend, budget RM400 total'\n"
        "- 'Looking for a camera to rent for my wedding next week, around RM200'\n"
        "- 'I need a car, a room, and a camera in Seri Kembangan' (MULTI-CATEGORY REQUEST)\n"
        "- 'I want a car and homestay in Selangor for 2 days with budget RM1000' (COMBINED BUDGET REQUEST)\n"
        "You must identify the CATEGORY (vehicle, accommodation, item, or MULTIPLE categories).\n"
        "You must also identify if the budget is COMBINED (one total for all) or SEPARATE (per category).\n\n"
        
        "**COMBINED BUDGET REQUESTS (VERY IMPORTANT!):**\n"
        "When user provides ONE TOTAL budget for MULTIPLE categories, use `search_with_combined_budget` tool.\n"
        "This finds COMBINATIONS of items that together fit within the total budget.\n"
        "Keywords: 'total budget', 'budget of', 'within RM', 'for X days with budget'\n\n"
        "Examples:\n"
        "- 'I want a car and homestay in Selangor for 2 days with budget RM1000' →\n"
        "  search_with_combined_budget(total_budget=1000, num_days=2, search_transport=True, search_accommodation=True, location='Selangor', property_type='homestay')\n"
        "- 'Book me a car and room for 3 days, my budget is RM500' →\n"
        "  search_with_combined_budget(total_budget=500, num_days=3, search_transport=True, search_accommodation=True)\n"
        "- 'I need transport and accommodation in KL for a week, total budget RM2000' →\n"
        "  search_with_combined_budget(total_budget=2000, num_days=7, search_transport=True, search_accommodation=True, location='Kuala Lumpur')\n\n"
        
        "**COMBINED BUDGET RESPONSE FORMAT:**\n"
        "The response shows COMBINATIONS that fit within the budget:\n"
        "{\n"
        "  \"type\": \"combined_budget_results\",\n"
        "  \"totalBudget\": 1000,\n"
        "  \"numDays\": 2,\n"
        "  \"combinations\": [\n"
        "    {\n"
        "      \"totalCost\": 300,\n"
        "      \"remainingBudget\": 700,\n"
        "      \"tags\": [\"Best Value\", \"Budget Saver\"],\n"
        "      \"transport\": { ... full transport listing ... },\n"
        "      \"accommodation\": { ... full accommodation listing ... }\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
        
        "**MULTI-CATEGORY REQUESTS (IMPORTANT!):**\n"
        "If the user asks for MULTIPLE categories at once, use `search_multiple_categories` tool.\n"
        "EACH CATEGORY CAN HAVE ITS OWN LOCATION AND BUDGET - extract them separately!\n"
        "→ Use category-specific parameters: transport_location, transport_max_price, accommodation_location, accommodation_max_price, item_location, item_max_price\n"
        "→ Extract category-specific details (vehicle_type, property_type, keyword, etc.).\n\n"
        "Examples:\n"
        "- 'I need a car in KL and a room in Seri Kembangan' →\n"
        "  search_multiple_categories(search_transport=True, transport_location='Kuala Lumpur', search_accommodation=True, accommodation_location='Seri Kembangan')\n"
        "- 'Find me a car for RM50 in KL, accommodation for RM200 in Seri Kembangan, and a camera in Selangor' →\n"
        "  search_multiple_categories(search_transport=True, transport_location='Kuala Lumpur', transport_max_price=50, search_accommodation=True, accommodation_location='Seri Kembangan', accommodation_max_price=200, search_items=True, item_location='Selangor', keyword='camera')\n"
        "- 'I need a bike, homestay, and guitar in Penang under RM100 each' →\n"
        "  search_multiple_categories(search_transport=True, transport_location='Penang', transport_max_price=100, vehicle_type='motorcycle', search_accommodation=True, accommodation_location='Penang', accommodation_max_price=100, property_type='homestay', search_items=True, item_location='Penang', item_max_price=100, keyword='guitar')\n\n"
        
        "**MULTI-CATEGORY RESPONSE FORMAT:**\n"
        "When returning multi-category results, return the tool response EXACTLY as-is in JSON format.\n"
        "DO NOT modify the structure. The response is an ARRAY of category results:\n"
        "{\n"
        "  \"type\": \"multi_category_results\",\n"
        "  \"message\": \"Here are the results for: transport, accommodation, items\",\n"
        "  \"results\": [\n"
        "    {\n"
        "      \"category\": \"transport\",\n"
        "      \"message\": \"Found X vehicle(s)\",\n"
        "      \"results\": [ { full listing data with tags }, ... ]\n"
        "    },\n"
        "    {\n"
        "      \"category\": \"accommodation\",\n"
        "      \"message\": \"Found X accommodation(s)\",\n"
        "      \"results\": [ { full listing data with tags }, ... ]\n"
        "    },\n"
        "    {\n"
        "      \"category\": \"items\",\n"
        "      \"message\": \"Found X item(s)\",\n"
        "      \"results\": [ { full listing data with tags }, ... ]\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "Each result contains ALL database fields plus 'tags' array with recommendation reasons.\n\n"
        
        "**ROUTING GUIDELINES:**\n"
        "1. **Greetings and small talk:** If the user greets you (e.g., 'hi', 'hello', 'hey') or engages in simple small talk, "
        "respond with JSON: {\"type\": \"prompt\", \"message\": \"Please tell me what you are looking for: a vehicle, accommodation or item to rent. You can also search for multiple categories at once!\"}\n\n"
        
        "2. **Single category - Vehicle/transport:** Keywords: 'car', 'bike', 'van', 'motorcycle', 'vehicle', 'drive', 'ride', 'transport'\n"
        "   → Delegate to TransportAgent via `transfer_to_agent` with 'TransportAgent'\n\n"
        
        "3. **Single category - Accommodation:** Keywords: 'room', 'apartment', 'hotel', 'house', 'stay', 'homestay', 'villa', 'place to stay', 'accommodation', 'guests'\n"
        "   → Delegate to AccommodationAgent via `transfer_to_agent` with 'AccommodationAgent'\n\n"
        
        "4. **Single category - Item:** Keywords: 'camera', 'laptop', 'tools', 'drill', 'equipment', 'rent a', 'borrow', 'guitar', 'musical'\n"
        "   → Delegate to ItemAgent via `transfer_to_agent` with 'ItemAgent'\n\n"
        
        "5. **COMBINED BUDGET multi-category requests:** When user mentions 2+ categories with ONE TOTAL budget:\n"
        "   → Use `search_with_combined_budget` tool\n"
        "   → This returns COMBINATIONS that fit within the total budget\n"
        "   → Example: 'car and homestay for 2 days with budget RM1000'\n\n"
        
        "6. **SEPARATE BUDGET multi-category requests:** When user mentions 2+ categories with separate budgets per category:\n"
        "   → Use `search_multiple_categories` tool\n"
        "   → Example: 'car for RM50 and room for RM200'\n\n"
        
        "7. **Ambiguous requests:** Respond with JSON: {\"type\": \"clarification\", \"message\": \"Are you looking for a vehicle, accommodation, item, or multiple categories?\"}\n\n"
        
        "8. **Outside scope:** Respond with JSON: {\"type\": \"error\", \"message\": \"I can only help with vehicle, accommodation, or item rentals.\"}\n\n"
        
        "**SPECIALIST AGENT CAPABILITIES:**\n"
        "- They return MULTIPLE options sorted from most suitable to least suitable in JSON format\n"
        "- Each option includes full details and tags explaining why it's recommended\n"
        "- They can interpret: date ranges, total budgets, per-day budgets, guest counts, ratings, etc.\n"
        "- If no exact matches, they suggest related options from the same category\n\n"
        
        "Always delegate single-category queries to the relevant specialist agent.\n"
        "For combined budget queries, use search_with_combined_budget.\n"
        "For separate budget multi-category queries, use search_multiple_categories."
    ),
    tools=[search_multiple_categories, search_with_combined_budget],
    sub_agents=[transport_agent, accommodation_agent, item_agent],
)


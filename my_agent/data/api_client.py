"""
api_client.py
-------------

API client for fetching real listings from the iShareApi backend.
This replaces the mock database with actual API calls.
"""

import os
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


# Backend API Configuration
# Use environment variable if set, otherwise default to localhost
API_BASE_URL = os.getenv("ISHARE_API_URL", "http://localhost:3000")
API_TIMEOUT = 10  # seconds


@dataclass
class Listing:
    """Base listing from API response."""
    id: str
    type: str  # TRANSPORT, ACCOMMODATION, ITEM
    title: str
    description: str
    basePrice: float
    status: str
    images: List[str]
    # Optional fields
    lat: Optional[float] = None
    lng: Optional[float] = None
    address: Optional[str] = None


@dataclass
class TransportListing(Listing):
    """Transport/vehicle listing."""
    vehicleType: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    transmission: Optional[str] = None
    fuelType: Optional[str] = None
    seats: Optional[int] = None
    licensePlate: Optional[str] = None


@dataclass
class AccommodationListing(Listing):
    """Accommodation listing."""
    propertyType: Optional[str] = None
    numGuests: Optional[int] = None
    amenities: Optional[List[str]] = None


@dataclass
class ItemListing(Listing):
    """Item listing."""
    category: Optional[str] = None
    condition: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None


def fetch_all_listings() -> Dict[str, Any]:
    """
    Fetch all listings from the backend API.
    
    Returns:
        Dict with 'success', 'data' (list of listings), and 'error' if failed.
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/listings",
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        return {
            "success": True,
            "data": response.json()
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Cannot connect to backend server. Is it running?",
            "data": []
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout - backend took too long to respond",
            "data": []
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": []
        }


def fetch_listings_by_owner(owner_id: int) -> Dict[str, Any]:
    """
    Fetch listings filtered by owner ID.
    
    Args:
        owner_id: The owner's user ID.
        
    Returns:
        Dict with 'success', 'data' (list of listings), and 'error' if failed.
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/listings",
            params={"ownerId": owner_id},
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        return {
            "success": True,
            "data": response.json()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": []
        }


def fetch_listing_by_id(listing_id: str) -> Dict[str, Any]:
    """
    Fetch a specific listing by ID.
    
    Args:
        listing_id: The listing's unique ID.
        
    Returns:
        Dict with 'success', 'data' (listing object), and 'error' if failed.
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/listings/{listing_id}",
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        return {
            "success": True,
            "data": response.json()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


def get_transport_listings() -> List[Dict[str, Any]]:
    """
    Fetch all TRANSPORT type listings from the backend.
    
    Returns:
        List of transport listing dictionaries.
    """
    result = fetch_all_listings()
    if not result["success"]:
        print(f"⚠️ API Error: {result['error']}")
        return []
    
    # Filter for TRANSPORT type
    listings = result["data"]
    transport_listings = [
        l for l in listings 
        if isinstance(l, dict) and l.get("type") == "TRANSPORT"
    ]
    return transport_listings


def get_accommodation_listings() -> List[Dict[str, Any]]:
    """
    Fetch all ACCOMMODATION type listings from the backend.
    
    Returns:
        List of accommodation listing dictionaries.
    """
    result = fetch_all_listings()
    if not result["success"]:
        print(f"⚠️ API Error: {result['error']}")
        return []
    
    # Filter for ACCOMMODATION type
    listings = result["data"]
    accommodation_listings = [
        l for l in listings 
        if isinstance(l, dict) and l.get("type") == "ACCOMMODATION"
    ]
    return accommodation_listings


def get_item_listings() -> List[Dict[str, Any]]:
    """
    Fetch all ITEM type listings from the backend.
    
    Returns:
        List of item listing dictionaries.
    """
    result = fetch_all_listings()
    if not result["success"]:
        print(f"⚠️ API Error: {result['error']}")
        return []
    
    # Filter for ITEM type
    listings = result["data"]
    item_listings = [
        l for l in listings 
        if isinstance(l, dict) and l.get("type") == "ITEM"
    ]
    return item_listings

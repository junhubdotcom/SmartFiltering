"""
mock_db.py
----------

This module defines simple data classes to represent listings in the iShare system
and provides a small mock database for testing agents. Each listing has a base
set of attributes, and category‑specific classes extend from the base. The
mock data can be imported by agent modules to simulate searching real
listings.

In a production system, you would replace these classes and data with your
database models or external service calls. The purpose here is to facilitate
local testing and demonstration of the smart filtering agents.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Listing:
    """Base class for all listings."""
    listingId: str
    ownerId: str
    title: str
    description: str
    basePrice: float
    location: str
    averageRating: float


@dataclass
class Transport(Listing):
    """Represents a vehicle available for rent."""
    vehicleType: str
    make: str
    model: str
    year: int


@dataclass
class Accommodation(Listing):
    """Represents a place to stay."""
    propertyType: str
    numGuests: int


@dataclass
class Item(Listing):
    """Represents a general item available for rent."""
    itemCategory: str


# Mock data for demonstration purposes. You can modify this list to test
# different scenarios or add more entries. Each category has at least one
# listing so that the agents can find a match.
mock_listings: List[Listing] = [
    Transport(
        listingId="T001",
        ownerId="U123",
        title="Toyota Camry 2018",
        description="A comfortable midsize sedan.",
        basePrice=80.0,
        location="Kuala Lumpur",
        averageRating=4.7,
        vehicleType="car",
        make="Toyota",
        model="Camry",
        year=2018,
    ),
    Transport(
        listingId="T002",
        ownerId="U124",
        title="Honda City 2019",
        description="Compact sedan with great fuel economy.",
        basePrice=70.0,
        location="Kuala Lumpur",
        averageRating=4.5,
        vehicleType="car",
        make="Honda",
        model="City",
        year=2019,
    ),
    Accommodation(
        listingId="A001",
        ownerId="U456",
        title="Cozy Apartment in KL",
        description="A modern one‑bedroom apartment close to downtown.",
        basePrice=150.0,
        location="Kuala Lumpur",
        averageRating=4.6,
        propertyType="Apartment",
        numGuests=2,
    ),
    Accommodation(
        listingId="A002",
        ownerId="U457",
        title="Family Home in Penang",
        description="A spacious house suitable for families.",
        basePrice=200.0,
        location="Penang",
        averageRating=4.8,
        propertyType="House",
        numGuests=6,
    ),
    Item(
        listingId="I001",
        ownerId="U789",
        title="Canon DSLR Camera",
        description="A professional DSLR camera for rent.",
        basePrice=60.0,
        location="Kuala Lumpur",
        averageRating=4.8,
        itemCategory="Electronics",
    ),
    Item(
        listingId="I002",
        ownerId="U790",
        title="Power Drill",
        description="Heavy duty power drill for DIY projects.",
        basePrice=20.0,
        location="Kuala Lumpur",
        averageRating=4.3,
        itemCategory="Tools",
    ),
]


def get_transport_listings() -> List[Transport]:
    """Return a list of transport listings from the mock database."""
    return [l for l in mock_listings if isinstance(l, Transport)]


def get_accommodation_listings() -> List[Accommodation]:
    """Return a list of accommodation listings from the mock database."""
    return [l for l in mock_listings if isinstance(l, Accommodation)]


def get_item_listings() -> List[Item]:
    """Return a list of item listings from the mock database."""
    return [l for l in mock_listings if isinstance(l, Item)]


__all__ = [
    "Listing",
    "Transport",
    "Accommodation",
    "Item",
    "mock_listings",
    "get_transport_listings",
    "get_accommodation_listings",
    "get_item_listings",
]

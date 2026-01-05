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
from typing import List, Optional


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
    tier: Optional[str] = None


@dataclass
class Item(Listing):
    """Represents a general item available for rent."""
    itemCategory: str


# Mock data for demonstration purposes. You can modify this list to test
# different scenarios or add more entries. Each category has at least one
# listing so that the agents can find a match.
mock_listings: List[Listing] = [
    # ==================== TRANSPORT LISTINGS ====================
    # Cars in Kuala Lumpur
    Transport(
        listingId="T001",
        ownerId="U123",
        title="Toyota Camry 2018",
        description="A comfortable midsize sedan, perfect for business trips.",
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
    Transport(
        listingId="T003",
        ownerId="U125",
        title="Perodua Myvi 2022",
        description="Affordable and fuel-efficient hatchback, ideal for city driving.",
        basePrice=50.0,
        location="Kuala Lumpur",
        averageRating=4.6,
        vehicleType="car",
        make="Perodua",
        model="Myvi",
        year=2022,
    ),
    Transport(
        listingId="T004",
        ownerId="U126",
        title="BMW 3 Series 2023",
        description="Luxury sedan with premium features and smooth handling.",
        basePrice=200.0,
        location="Kuala Lumpur",
        averageRating=4.9,
        vehicleType="car",
        make="BMW",
        model="3 Series",
        year=2023,
    ),
    # Vehicles in Penang
    Transport(
        listingId="T005",
        ownerId="U127",
        title="Toyota Vios 2020",
        description="Reliable sedan for exploring Penang island.",
        basePrice=65.0,
        location="Penang",
        averageRating=4.4,
        vehicleType="car",
        make="Toyota",
        model="Vios",
        year=2020,
    ),
    Transport(
        listingId="T006",
        ownerId="U128",
        title="Honda PCX 160 2022",
        description="Comfortable scooter for navigating Penang streets.",
        basePrice=35.0,
        location="Penang",
        averageRating=4.7,
        vehicleType="motorcycle",
        make="Honda",
        model="PCX 160",
        year=2022,
    ),
    # Vehicles in Johor Bahru
    Transport(
        listingId="T007",
        ownerId="U129",
        title="Toyota Hiace 2021",
        description="Spacious van for group travel, seats up to 10 passengers.",
        basePrice=150.0,
        location="Johor Bahru",
        averageRating=4.6,
        vehicleType="van",
        make="Toyota",
        model="Hiace",
        year=2021,
    ),
    Transport(
        listingId="T008",
        ownerId="U130",
        title="Yamaha Y15ZR 2023",
        description="Sporty motorcycle with excellent performance.",
        basePrice=40.0,
        location="Johor Bahru",
        averageRating=4.8,
        vehicleType="motorcycle",
        make="Yamaha",
        model="Y15ZR",
        year=2023,
    ),

    # ==================== ACCOMMODATION LISTINGS ====================
    # Kuala Lumpur Accommodations
    Accommodation(
        listingId="A001",
        ownerId="U456",
        title="Cozy Apartment in KL",
        description="A modern one-bedroom apartment close to downtown.",
        basePrice=150.0,
        location="Kuala Lumpur",
        averageRating=4.6,
        propertyType="Apartment",
        numGuests=2,
        tier="normal",
    ),
    Accommodation(
        listingId="A005",
        ownerId="U460",
        title="Budget Hostel in KL Central",
        description="Clean and affordable hostel near KL Sentral station.",
        basePrice=40.0,
        location="Kuala Lumpur",
        averageRating=4.2,
        propertyType="Hostel",
        numGuests=1,
        tier="low",
    ),
    Accommodation(
        listingId="A006",
        ownerId="U461",
        title="Luxury Suite at KLCC",
        description="Premium suite with stunning Petronas Towers view.",
        basePrice=500.0,
        location="Kuala Lumpur",
        averageRating=4.9,
        propertyType="Apartment",
        numGuests=4,
        tier="premium",
    ),
    Accommodation(
        listingId="A007",
        ownerId="U462",
        title="Family Condo in Bangsar",
        description="Spacious 3-bedroom condo in trendy Bangsar area.",
        basePrice=280.0,
        location="Kuala Lumpur",
        averageRating=4.7,
        propertyType="Apartment",
        numGuests=6,
        tier="normal",
    ),
    # Penang Accommodations
    Accommodation(
        listingId="A002",
        ownerId="U457",
        title="Family Home in Penang 1",
        description="A spacious house suitable for families near the beach.",
        basePrice=150.0,
        location="Penang",
        averageRating=4.8,
        propertyType="House",
        numGuests=6,
        tier="normal",
    ),
    Accommodation(
        listingId="A003",
        ownerId="U458",
        title="Family Home in Penang 2",
        description="A spacious house suitable for families with garden.",
        basePrice=300.0,
        location="Penang",
        averageRating=4.8,
        propertyType="House",
        numGuests=6,
        tier="premium",
    ),
    Accommodation(
        listingId="A004",
        ownerId="U459",
        title="Luxury Villa in Penang",
        description="Premium villa with private pool and sea view.",
        basePrice=450.0,
        location="Penang",
        averageRating=5.0,
        propertyType="Villa",
        numGuests=8,
        tier="premium",
    ),
    Accommodation(
        listingId="A008",
        ownerId="U463",
        title="Budget Homestay in Georgetown",
        description="Affordable homestay in the heart of Georgetown.",
        basePrice=60.0,
        location="Penang",
        averageRating=4.3,
        propertyType="Homestay",
        numGuests=3,
        tier="low",
    ),
    # Johor Bahru Accommodations
    Accommodation(
        listingId="A009",
        ownerId="U464",
        title="Modern Studio near Legoland",
        description="Convenient studio apartment near Legoland Malaysia.",
        basePrice=120.0,
        location="Johor Bahru",
        averageRating=4.5,
        propertyType="Apartment",
        numGuests=2,
        tier="normal",
    ),
    Accommodation(
        listingId="A010",
        ownerId="U465",
        title="Family House in JB",
        description="Comfortable house for families visiting Johor.",
        basePrice=180.0,
        location="Johor Bahru",
        averageRating=4.6,
        propertyType="House",
        numGuests=5,
        tier="normal",
    ),

    # ==================== ITEM LISTINGS ====================
    # Electronics in Kuala Lumpur
    Item(
        listingId="I001",
        ownerId="U789",
        title="Canon DSLR Camera",
        description="A professional DSLR camera for rent, perfect for events.",
        basePrice=60.0,
        location="Kuala Lumpur",
        averageRating=4.8,
        itemCategory="Electronics",
    ),
    Item(
        listingId="I003",
        ownerId="U791",
        title="Sony A7 III Mirrorless Camera",
        description="High-end mirrorless camera for professional photography.",
        basePrice=120.0,
        location="Kuala Lumpur",
        averageRating=4.9,
        itemCategory="Electronics",
    ),
    Item(
        listingId="I004",
        ownerId="U792",
        title="DJI Mavic 3 Drone",
        description="Professional drone for aerial photography and videography.",
        basePrice=150.0,
        location="Kuala Lumpur",
        averageRating=4.7,
        itemCategory="Electronics",
    ),
    Item(
        listingId="I005",
        ownerId="U793",
        title="MacBook Pro 16-inch",
        description="Powerful laptop for video editing and design work.",
        basePrice=80.0,
        location="Kuala Lumpur",
        averageRating=4.8,
        itemCategory="Electronics",
    ),
    # Tools
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
    Item(
        listingId="I006",
        ownerId="U794",
        title="Complete Tool Set",
        description="Comprehensive tool set with 200+ pieces for any project.",
        basePrice=45.0,
        location="Kuala Lumpur",
        averageRating=4.6,
        itemCategory="Tools",
    ),
    Item(
        listingId="I007",
        ownerId="U795",
        title="Pressure Washer",
        description="High-pressure washer for car and home cleaning.",
        basePrice=35.0,
        location="Penang",
        averageRating=4.4,
        itemCategory="Tools",
    ),
    # Sports & Outdoor
    Item(
        listingId="I008",
        ownerId="U796",
        title="Camping Tent (4-Person)",
        description="Waterproof tent suitable for 4 people, perfect for camping.",
        basePrice=30.0,
        location="Kuala Lumpur",
        averageRating=4.5,
        itemCategory="Sports",
    ),
    Item(
        listingId="I009",
        ownerId="U797",
        title="Mountain Bike",
        description="Quality mountain bike for trail riding and adventures.",
        basePrice=40.0,
        location="Penang",
        averageRating=4.6,
        itemCategory="Sports",
    ),
    Item(
        listingId="I010",
        ownerId="U798",
        title="Snorkeling Set",
        description="Complete snorkeling gear including mask, fins, and snorkel.",
        basePrice=25.0,
        location="Penang",
        averageRating=4.7,
        itemCategory="Sports",
    ),
    # Event Equipment
    Item(
        listingId="I011",
        ownerId="U799",
        title="PA System with Speakers",
        description="Professional sound system for events and parties.",
        basePrice=100.0,
        location="Kuala Lumpur",
        averageRating=4.5,
        itemCategory="Events",
    ),
    Item(
        listingId="I012",
        ownerId="U800",
        title="Projector and Screen",
        description="HD projector with portable screen for presentations.",
        basePrice=50.0,
        location="Johor Bahru",
        averageRating=4.4,
        itemCategory="Electronics",
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

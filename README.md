# Smart Filtering Agent for iShare

A multi-agent AI system for intelligent rental listing search and filtering. Built with Google ADK (Agent Development Kit) and integrates with the iShareApi backend.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Google Cloud Setup](#google-cloud-setup)
- [Running the Agent](#running-the-agent)
- [Testing](#testing)
- [Deployment](#deployment)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Smart Filtering Agent consists of:
- **Root Agent**: Routes queries to specialized sub-agents
- **Transport Agent**: Handles vehicle rental searches
- **Accommodation Agent**: Handles room/property rental searches
- **Item Agent**: Handles miscellaneous item rental searches

Each agent can:
- Search listings with multiple filters
- Return results sorted by suitability
- Provide focused suggestions when no exact match is found
- Generate descriptive tags for each result

---

## Prerequisites

Before starting, ensure you have:

1. **Python 3.10+** installed
2. **Google Cloud SDK** installed
3. **Google Cloud Project** with Vertex AI API enabled
4. **Backend API** (iShareApi) running at `http://localhost:3000`

---

## Installation

### Step 1: Clone and Setup Project

```bash
# Navigate to project directory
cd /path/to/SmartFilteringV1

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
.\venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
# Check if google-adk is installed
pip show google-adk

# Expected output should show version 1.21.0 or higher
```

---

## Google Cloud Setup

### Step 1: Install Google Cloud SDK

**macOS (using Homebrew):**
```bash
brew install --cask google-cloud-sdk
```

**macOS (manual installation):**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
Download and run the installer from: https://cloud.google.com/sdk/docs/install

### Step 2: Initialize Google Cloud CLI

```bash
# Initialize gcloud
gcloud init

# Follow the prompts:
# 1. Log in with your Google account
# 2. Select or create a Google Cloud project
# 3. Set default compute region (optional)
```

### Step 3: Authenticate Application Default Credentials

```bash
# Login for application default credentials
gcloud auth application-default login

# This opens a browser for authentication
# After login, credentials are saved locally
```

### Step 4: Set Your Project

```bash
# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Verify the project is set
gcloud config get-value project
```

### Step 5: Enable Required APIs

```bash
# Enable Vertex AI API (required for Gemini models)
gcloud services enable aiplatform.googleapis.com

# Enable Cloud Resource Manager API
gcloud services enable cloudresourcemanager.googleapis.com

# Verify APIs are enabled
gcloud services list --enabled | grep -E "aiplatform|cloudresourcemanager"
```

### Step 6: Verify Setup

```bash
# Check authentication status
gcloud auth list

# Should show your account with an asterisk (*)
# Example output:
#    ACTIVE  ACCOUNT
#    *       your-email@gmail.com
```

---

## Running the Agent

### Option 1: Using ADK CLI (Recommended)

```bash
# Run in terminal mode (interactive chat)
adk run my_agent

# Run with web interface
adk web
```

### Option 2: Using Local Deployment Script

```bash
# Run the local deployment
python3 -m my_agent.deployment.local
```

### Option 3: Direct Python Import

```python
from my_agent.subagents.transport_agent import search_transport_listings
from my_agent.subagents.accommodation_agent import search_accommodation_listings
from my_agent.subagents.item_agent import search_item_listings

# Search for vehicles
result = search_transport_listings(
    location="Kuala Lumpur",
    max_price_per_day=200,
    vehicle_type="car"
)

# Search for accommodation
result = search_accommodation_listings(
    location="Kuala Lumpur",
    property_type="room",
    max_guests=6,
    max_price_per_day=333.33
)

# Search for items
result = search_item_listings(
    keyword="camera",
    max_price_per_day=100
)
```

---

## Testing

### Run Complete Test Suite

```bash
# Make sure backend is running first!
# Then run the test file
python test_complete.py
```

### Test Output Example

```
======================================================================
🧪 SMART FILTERING AGENT - COMPLETE TEST SUITE
======================================================================

======================================================================
🔌 TEST 1: API Connection
======================================================================

📡 Testing connection to backend API...
✅ Connected successfully!
   Total listings in database: 15

   Breakdown by type:
   🚗 Transport: 5
   🏠 Accommodation: 5
   📦 Items: 5

... (more tests)

======================================================================
📊 TEST SUMMARY
======================================================================
   ✅ API Connection
   ✅ Transport Agent
   ✅ Accommodation Agent
   ✅ Item Agent
   ✅ JSON Response Format
   ✅ Database Fields
   ✅ Edge Cases

   Total: 7/7 tests passed

🎉 ALL TESTS PASSED!
```

### Quick API Test

```bash
# Test only the API connection
python test_agent_api_call.py
```

---

## Deployment

### Local Deployment

```bash
# Simple local run
adk run my_agent
```

### Remote Deployment (Google Cloud)

#### Step 1: Create a Deployment

```bash
python3 -m my_agent.deployment.remote --create
```

This will output a `RESOURCE_ID` - save this for later use.

#### Step 2: List All Deployments

```bash
python3 -m my_agent.deployment.remote --list
```

#### Step 3: Create a Session

```bash
python3 -m my_agent.deployment.remote --create_session \
    --resource_id YOUR_RESOURCE_ID \
    --user_id test_user
```

This will output a `SESSION_ID` - save this for later use.

#### Step 4: Send Messages to Deployed Agent

```bash
python3 -m my_agent.deployment.remote --send \
    --resource_id YOUR_RESOURCE_ID \
    --session_id YOUR_SESSION_ID \
    --message "I want to find a room in Kuala Lumpur for 6 guests"
```

#### Step 5: List Sessions

```bash
python3 -m my_agent.deployment.remote --list_sessions \
    --resource_id YOUR_RESOURCE_ID \
    --user_id test_user
```

#### Step 6: Delete Deployment (Cleanup)

```bash
python3 -m my_agent.deployment.remote --delete \
    --resource_id YOUR_RESOURCE_ID
```

---

## API Reference

### Search Functions

#### Transport Search

```python
search_transport_listings(
    location: str = None,           # City or area (e.g., "Kuala Lumpur")
    max_price_per_day: float = None, # Maximum price per day
    vehicle_type: str = None,       # "car", "motorcycle", "van", etc.
    make: str = None,               # Brand (e.g., "Toyota")
    model: str = None,              # Model (e.g., "Camry")
    min_year: int = None,           # Minimum year of manufacture
    min_rating: float = None        # Minimum rating
) -> Dict
```

#### Accommodation Search

```python
search_accommodation_listings(
    location: str = None,           # City or area
    max_price_per_day: float = None, # Maximum price per day
    property_type: str = None,      # "room", "apartment", "house", etc.
    max_guests: int = None,         # Minimum guest capacity
    min_rating: float = None        # Minimum rating
) -> Dict
```

#### Item Search

```python
search_item_listings(
    location: str = None,           # City or area
    max_price_per_day: float = None, # Maximum price per day
    item_category: str = None,      # "Electronics", "Tools", etc.
    keyword: str = None,            # Search in title/description
    min_rating: float = None        # Minimum rating
) -> Dict
```

### Response Format

All search functions return:

```json
{
    "message": "Found X listing(s) matching your criteria.",
    "results": [
        {
            "listingId": "abc123",
            "title": "Cozy Room in KL",
            "description": "...",
            "address": "Kuala Lumpur, Malaysia",
            "pricePerDay": 150.00,
            "images": ["url1", "url2"],
            "status": "AVAILABLE",
            "tags": ["Most Suitable", "Budget Friendly"],
            // ... type-specific fields
        }
    ]
}
```

### Database Schema

The backend database has these columns:

| Column | Description |
|--------|-------------|
| `id` | Unique identifier |
| `title` | Listing title |
| `description` | Detailed description |
| `basePrice` | Price per day (RM) |
| `lat`, `lng` | Location coordinates |
| `address` | Full address |
| `status` | AVAILABLE, RENTED, etc. |
| `images` | Array of image URLs |
| `type` | TRANSPORT, ACCOMMODATION, ITEM |
| `ownerId` | Owner's user ID |

**Transport-specific:**
| Column | Description |
|--------|-------------|
| `vehicleType` | car, motorcycle, van, etc. |
| `brand` | Vehicle brand |
| `model` | Vehicle model |
| `year` | Year of manufacture |
| `transmission` | Manual, Automatic |
| `fuelType` | Petrol, Diesel, Electric |
| `seats` | Number of seats |
| `licensePlate` | License plate number |

**Accommodation-specific:**
| Column | Description |
|--------|-------------|
| `propertyType` | room, apartment, house, etc. |
| `maxGuests` | Maximum guest capacity |
| `bedCount` | Number of beds |
| `roomCount` | Number of rooms |
| `bathroomCount` | Number of bathrooms |
| `amenities` | Array of amenities |

**Item-specific:**
| Column | Description |
|--------|-------------|
| `category` | Electronics, Tools, etc. |
| `condition` | New, Excellent, Good, etc. |
| `brand` | Item brand |
| `model` | Item model |
| `deliveryMethod` | Pickup, Delivery, etc. |

---

## Troubleshooting

### Common Issues

#### 1. "Cannot connect to backend server"

**Problem:** The iShareApi backend is not running.

**Solution:**
```bash
# Start your backend server
cd /path/to/iShareApi
npm start
# or
yarn start

# Verify it's running
curl http://localhost:3000/listings
```

#### 2. "gcloud: command not found"

**Problem:** Google Cloud SDK not installed or not in PATH.

**Solution:**
```bash
# Reinstall Google Cloud SDK
brew install --cask google-cloud-sdk

# Or add to PATH manually
export PATH="$PATH:/path/to/google-cloud-sdk/bin"
```

#### 3. "Application Default Credentials not found"

**Problem:** Not authenticated with Google Cloud.

**Solution:**
```bash
gcloud auth application-default login
```

#### 4. "Permission denied" or "API not enabled"

**Problem:** Vertex AI API not enabled or insufficient permissions.

**Solution:**
```bash
# Enable the API
gcloud services enable aiplatform.googleapis.com

# Check your project
gcloud config get-value project
```

#### 5. "Model not found" error

**Problem:** The Gemini model is not available in your region.

**Solution:**
- Ensure your project has access to Gemini models
- Try a different model version in the agent configuration

### Getting Help

1. Check the test output: `python test_complete.py`
2. Verify API connection: `python test_agent_api_call.py`
3. Check Google Cloud status: `gcloud auth list`
4. Review logs in the terminal

---

## Project Structure

```
SmartFilteringV1/
├── my_agent/
│   ├── __init__.py
│   ├── agent.py              # Root agent definition
│   ├── data/
│   │   ├── __init__.py
│   │   └── api_client.py     # Backend API client
│   ├── deployment/
│   │   ├── cleanup.py
│   │   ├── local.py          # Local deployment script
│   │   └── remote.py         # Remote deployment script
│   └── subagents/
│       ├── __init__.py
│       ├── accommodation_agent.py
│       ├── item_agent.py
│       └── transport_agent.py
├── test_complete.py          # Complete test suite
├── test_agent_api_call.py    # Quick API test
├── requirements.txt
└── README.md
```

---

## License

This project is part of the iShare platform.
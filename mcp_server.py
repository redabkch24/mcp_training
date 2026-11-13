import json
from fastmcp import FastMCP
from pathlib import Path

# initialize our MCP server instance
# name restaurants-server which identifies this server when clients connect to it
mcp = FastMCP("restaurants-server")


DATA_PATH = Path(__file__).parent / "restaurants.json"

# helper function
def load_restaurants_data() -> list[dict]:
    """Load restaurant records from the local JSON file"""
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)

# MCP Resource 
@mcp.resource("restaurants://all")
def get_all_restaurants() -> str:
    """Expose the complete restaurant JSON as an MCP resource."""
    return DATA_PATH.read_text(encoding="utf-8")


# MCP Tools
# tool 1 : Get restaurant information by name
@mcp.tool()
def get_restaurant_info(restaurant_name: str) -> str:
    """Find restaurants by full or partial name."""
    restaurants = load_restaurants_data()
    query = restaurant_name.lower().strip()

    matches = [
        restaurant
        for restaurant in restaurants
        if query in restaurant["name"].lower()
    ]

    if not matches:
        return json.dumps(
            {
                "status": "not_found",
                "message": f"No restaurant found matching '{restaurant_name}'.",
            },
            indent=2,
        )

    return json.dumps(
        {
            "status": "found",
            "count": len(matches),
            "results": matches,
        },
        indent=2,
    )

# tool 2 : Get restaurants by vibe
@mcp.tool()
def recommend_by_vibe(vibe: str) -> str:
    """Find restaurants by vibe, cuisine, location, or description text."""
    restaurants = load_restaurants_data()
    query = vibe.lower().strip()
    matches = []

    for restaurant in restaurants:
        searchable_text = " ".join(
            [
                restaurant.get("name", ""),
                restaurant.get("location", ""),
                restaurant.get("cuisine", ""),
                restaurant.get("description", ""),
                " ".join(restaurant.get("vibes", [])),
            ]
        ).lower()

        if query in searchable_text:
            matches.append(restaurant)

    return json.dumps(
        {
            "status": "found" if matches else "not_found",
            "query": vibe,
            "count": len(matches),
            "results": matches,
        },
        indent=2,
    )

# tool 3 : Get review and rating for a restaurant
@mcp.tool()
def get_review(restaurant_name: str) -> str:
    """Return the review and rating for a restaurant."""
    restaurants = load_restaurants_data()
    query = restaurant_name.lower().strip()

    for restaurant in restaurants:
        if query in restaurant["name"].lower():
            return json.dumps(
                {
                    "status": "found",
                    "restaurant": restaurant["name"],
                    "rating": restaurant.get("rating"),
                    "review": restaurant.get("review", "No review available."),
                },
                indent=2,
            )

    return json.dumps(
        {
            "status": "not_found",
            "message": f"No review found for '{restaurant_name}'.",
        },
        indent=2,
    )


if __name__ == "__main__":
    mcp.run()
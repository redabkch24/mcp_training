import asyncio

import gradio as gr

from mcp_client import call_tool


async def search_restaurants(query: str) -> str:
    """Search through the MCP server and format restaurant results."""
    result = await call_tool(
        "recommend_by_vibe",
        {"vibe": query},
    )

    if result.get("status") == "not_found":
        return f"No restaurants found for: {query}"

    output = []

    for restaurant in result.get("results", []):
        output.append(
            f"### {restaurant['name']}\n"
            f"- Location: {restaurant['location']}\n"
            f"- Cuisine: {restaurant['cuisine']}\n"
            f"- Rating: {restaurant['rating']}\n"
            f"- Price range: {'$' * restaurant['price_range']}\n"
            f"- Vibes: {', '.join(restaurant['vibes'])}\n"
            f"- Signature dish: {restaurant['signature_dish']}\n"
            f"- Description: {restaurant['description']}\n"
        )

    return "\n".join(output) or "No restaurants found."


async def restaurant_details(name: str) -> str:
    """Find one restaurant through the MCP server."""
    result = await call_tool(
        "get_restaurant_info",
        {"restaurant_name": name},
    )

    if result.get("status") == "not_found":
        return result["message"]

    restaurants = result.get("results", [])
    if not restaurants:
        return "No restaurant found."

    restaurant = restaurants[0]

    return (
        f"### {restaurant['name']}\n"
        f"- Location: {restaurant['location']}\n"
        f"- Cuisine: {restaurant['cuisine']}\n"
        f"- Rating: {restaurant['rating']}\n"
        f"- Price range: {'$' * restaurant['price_range']}\n"
        f"- Vibes: {', '.join(restaurant['vibes'])}\n"
        f"- Signature dish: {restaurant['signature_dish']}\n"
        f"- Description: {restaurant['description']}\n"
    )


async def review_details(name: str) -> str:
    """Retrieve a review through the MCP server."""
    result = await call_tool(
        "get_review",
        {"restaurant_name": name},
    )

    if result.get("status") == "not_found":
        return result["message"]

    return (
        f"### {result['restaurant']}\n"
        f"- Rating: {result['rating']}\n"
        f"- Review: {result['review']}"
    )


def run_search(query: str) -> str:
    if not query or not query.strip():
        return "Please enter a search term."
    return asyncio.run(search_restaurants(query.strip()))


def run_details(name: str) -> str:
    if not name or not name.strip():
        return "Please enter a restaurant name."
    return asyncio.run(restaurant_details(name.strip()))


def run_review(name: str) -> str:
    if not name or not name.strip():
        return "Please enter a restaurant name."
    return asyncio.run(review_details(name.strip()))


with gr.Blocks(title="Restaurant MCP Application") as demo:
    gr.Markdown("# Restaurant MCP Application")
    gr.Markdown(
        "This Gradio interface calls an MCP client, which calls an MCP server "
        "that searches restaurants.json."
    )

    with gr.Tab("Search"):
        search_input = gr.Textbox(
            label="Search by vibe, cuisine, location, or description",
            placeholder="Try: romantic, Japanese, Santa Monica, coastal",
        )
        search_button = gr.Button("Search restaurants")
        search_output = gr.Markdown()
        search_button.click(
            fn=run_search,
            inputs=search_input,
            outputs=search_output,
        )

    with gr.Tab("Restaurant details"):
        details_input = gr.Textbox(
            label="Restaurant name",
            placeholder="Try: Iron or Sakura",
        )
        details_button = gr.Button("Find restaurant")
        details_output = gr.Markdown()
        details_button.click(
            fn=run_details,
            inputs=details_input,
            outputs=details_output,
        )

    with gr.Tab("Review"):
        review_input = gr.Textbox(
            label="Restaurant name",
            placeholder="Try: Mar de Cortez",
        )
        review_button = gr.Button("Get review")
        review_output = gr.Markdown()
        review_button.click(
            fn=run_review,
            inputs=review_input,
            outputs=review_output,
        )


if __name__ == "__main__":
    demo.launch()
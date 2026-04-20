"""
tools.py - Resource Search Tool for the Smart Resource Finder Agent
Provides structured tool definitions and a resource search function.
"""

import json


# ─── Tool Definition (sent to Groq LLM as a callable tool) ────────────────────

RESOURCE_TOOL = {
    "type": "function",
    "function": {
        "name": "search_study_resources",
        "description": (
            "Search for high-quality academic learning resources for a given topic. "
            "Returns structured recommendations across multiple resource types: "
            "videos, documentation, tutorials, research papers, and practice sets."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The academic topic to search resources for.",
                },
                "level": {
                    "type": "string",
                    "enum": ["beginner", "intermediate", "advanced"],
                    "description": "The difficulty level of the resources.",
                },
                "resource_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Types of resources to find, e.g. "
                        "['video', 'documentation', 'tutorial', 'paper', 'practice']"
                    ),
                },
            },
            "required": ["topic", "level", "resource_types"],
        },
    },
}


# ─── Tool Executor ─────────────────────────────────────────────────────────────

def search_study_resources(topic: str, level: str, resource_types: list[str]) -> str:
    """
    Simulate a resource-search tool.

    In a real deployment this would hit APIs such as YouTube Data API,
    arXiv, or a web-search endpoint.  For the demo we return a structured
    prompt that the LLM will populate with real, accurate resource names.
    """

    resource_template = {
        "topic": topic,
        "level": level,
        "requested_types": resource_types,
        "instruction": (
            "Generate detailed, real, and accurate study resources for the topic above. "
            "For each resource type requested provide 2-3 concrete recommendations "
            "including: resource name, URL (real if known, otherwise best-guess), "
            "a one-sentence description, and why it is useful for this level. "
            "Format the final answer in clean Markdown with emoji icons."
        ),
    }

    return json.dumps(resource_template)


# ─── Tool Dispatcher ───────────────────────────────────────────────────────────

def execute_tool(tool_name: str, tool_args: dict) -> str:
    """Route a tool call to the correct Python function."""
    if tool_name == "search_study_resources":
        return search_study_resources(**tool_args)
    raise ValueError(f"Unknown tool: {tool_name}")

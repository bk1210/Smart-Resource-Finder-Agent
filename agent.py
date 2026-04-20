"""
agent.py - Smart Resource Finder Agent
Implements the Observe → Think → Act agentic loop using Groq + tool calling.
"""

import json
import os
from groq import Groq
from tools import RESOURCE_TOOL, execute_tool


# ─── Constants ────────────────────────────────────────────────────────────────

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are StudyBot, an expert AI academic assistant for college students.

Your mission: help students find the best possible learning resources for any academic topic.

## Your Behaviour
1. OBSERVE  — carefully read the student's topic.
2. THINK    — determine the appropriate difficulty level and which resource types will help most.
3. ACT      — call the `search_study_resources` tool with the right parameters, then use its
               output to compose a rich, well-structured Markdown response.

## Response Format (after tool call)
Structure your final answer with these sections:
- 🎯 **Topic Overview** — 2-3 sentences explaining what the topic is about
- 📚 **Recommended Resources** — grouped by type with names, URLs, and why they help
- 🗺️ **Suggested Study Path** — a short ordered plan (e.g., Step 1 → Step 2 → Step 3)
- 💡 **Pro Tips** — 2-3 quick study tips specific to this topic

Use clear Markdown: headers, bullet points, bold text, and emoji for readability.
Always include real, accurate resource names and URLs where you know them.
Keep the tone friendly, encouraging, and concise."""


# ─── Agent ────────────────────────────────────────────────────────────────────

class ResourceFinderAgent:
    """
    Agentic loop:
      1. Send user topic + system prompt to Groq LLM.
      2. LLM decides to call `search_study_resources` tool.
      3. Agent executes the tool and feeds result back to LLM.
      4. LLM composes the final Markdown answer.
    """

    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    # ── Step helpers ──────────────────────────────────────────────────────────

    def _observe(self, topic: str) -> list[dict]:
        """Build the initial message list from the student's topic."""
        return [
            {
                "role": "user",
                "content": (
                    f"I need study resources for the following topic: **{topic}**\n\n"
                    "Please find comprehensive learning materials that will help me "
                    "understand and master this subject."
                ),
            }
        ]

    def _think_and_act(self, messages: list[dict]) -> str:
        """
        Send messages to Groq.  If the model calls a tool, execute it and
        continue the loop until a final text response is produced.
        """
        max_iterations = 5  # safety cap

        for _ in range(max_iterations):
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=[RESOURCE_TOOL],
                tool_choice="auto",
                max_tokens=2048,
                temperature=0.7,
            )

            choice = response.choices[0]

            # ── Tool call branch ──────────────────────────────────────────
            if choice.finish_reason == "tool_calls":
                assistant_msg = {
                    "role": "assistant",
                    "content": choice.message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in choice.message.tool_calls
                    ],
                }
                messages.append(assistant_msg)

                # Execute every tool the model requested
                for tool_call in choice.message.tool_calls:
                    tool_args = json.loads(tool_call.function.arguments)
                    tool_result = execute_tool(tool_call.function.name, tool_args)

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result,
                        }
                    )

                # Loop back → model will now compose the final answer
                continue

            # ── Final text response ───────────────────────────────────────
            return choice.message.content or "No response generated."

        return "Agent reached maximum iterations without a final answer."

    # ── Public API ────────────────────────────────────────────────────────────

    def run(self, topic: str) -> dict:
        """
        Full Observe → Think → Act pipeline.
        Returns a dict with keys: topic, result, steps.
        """
        steps = []

        # 1. Observe
        steps.append(f"👁️ **Observe:** Received topic → _{topic}_")
        messages = self._observe(topic)

        # 2. Think + Act
        steps.append("🧠 **Think:** Analysing topic and selecting resource types…")
        steps.append("⚡ **Act:** Calling Groq LLM with tool-use enabled…")
        result = self._think_and_act(messages)
        steps.append("✅ **Done:** Resources compiled and formatted.")

        return {"topic": topic, "result": result, "steps": steps}

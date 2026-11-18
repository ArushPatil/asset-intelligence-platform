"""
LLM Client Module.

Provides the LLMClient class supporting live API calls to Google Gemini API (gemini-flash-latest / gemini-2.0-flash),
OpenAI API (gpt-4o), or a dynamic local context synthesis engine fallback.
"""

import re
import os
from typing import Optional

from config import config
from utils.logger import setup_logger
from utils.exceptions import LLMOrchestratorException

logger = setup_logger("llm.client", config.log_level)


class LLMClient:
    """Client wrapper managing LLM generation across Gemini API, OpenAI API, or local fallback."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> None:
        """
        Initialize LLMClient with API credentials and model targets.

        Args:
            api_key (Optional[str]): OpenAI or target API key.
            model_name (Optional[str]): Target model name.
        """
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.openai_key = api_key or config.llm.api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model_name or config.llm.model_name or "gpt-4o"

        self._gemini_client = None
        self._openai_client = None
        self.last_backend = "local"

        # 1. Initialize Gemini API Client if key is available
        if self.gemini_key and not self.gemini_key.startswith("your_"):
            try:
                from google import genai
                self._gemini_client = genai.Client(api_key=self.gemini_key)
                logger.info("Initialized Google GenAI Gemini API client.")
            except Exception as e:
                logger.warning("Failed to initialize Google GenAI client (%s).", e)

        # 2. Initialize OpenAI API Client if key is available
        if self.openai_key and not self.openai_key.startswith("your_"):
            try:
                import openai
                self._openai_client = openai.OpenAI(api_key=self.openai_key)
                logger.info("Initialized OpenAI API client (Model: %s).", self.model_name)
            except Exception as e:
                logger.warning("Failed to initialize OpenAI client (%s).", e)

    def generate_response(self, prompt: str) -> str:
        """
        Send completed prompt to live LLM (Gemini or OpenAI) and return generated natural language answer.

        Args:
            prompt (str): Completed formatted prompt string.

        Returns:
            str: Synthesized response text.

        Raises:
            LLMOrchestratorException: If prompt string is empty.
        """
        if not prompt.strip():
            raise LLMOrchestratorException("Prompt string cannot be empty.")

        # Re-check environment variables in case key was set at runtime
        if self._gemini_client is None:
            g_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if g_key and not g_key.startswith("your_"):
                try:
                    from google import genai
                    self._gemini_client = genai.Client(api_key=g_key)
                    logger.info("Initialized Google GenAI Gemini API client dynamically.")
                except Exception:
                    pass

        # 1. Live Call: Google Gemini API
        if self._gemini_client is not None:
            for m_target in ["gemini-1.5-flash", "gemini-flash-latest", "gemini-1.5-pro", "gemini-2.0-flash"]:
                try:
                    logger.info("Sending prompt to live Gemini API model '%s'...", m_target)
                    response = self._gemini_client.models.generate_content(
                        model=m_target,
                        contents=prompt
                    )
                    answer = response.text.strip()
                    logger.info("Received live response from Gemini API (%d characters).", len(answer))
                    self.last_backend = f"Gemini {m_target}"
                    return answer
                except Exception as e:
                    logger.warning("Gemini model '%s' call failed (%s). Trying next model target...", m_target, e)

        # 2. Live Call: OpenAI API
        if self._openai_client is not None:
            try:
                logger.info("Sending prompt to OpenAI model '%s'...", self.model_name)
                response = self._openai_client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are an enterprise AI Asset Intelligence assistant for facilities engineering."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=600
                )
                answer = response.choices[0].message.content.strip()
                logger.info("Received live response from OpenAI (%d characters).", len(answer))
                self.last_backend = f"OpenAI {self.model_name}"
                return answer
            except Exception as e:
                logger.warning("OpenAI API call failed (%s). Falling back to local dynamic context engine.", e)

        # 3. Fallback: High-performance local dynamic synthesis engine
        logger.info("Executing local dynamic contextual synthesis engine fallback...")
        self.last_backend = "local"
        return self._synthesize_fallback_response(prompt)

    def _synthesize_fallback_response(self, prompt: str) -> str:
        """
        Synthesize a factual, dynamic natural language answer directly from prompt context.
        Parses user question and retrieved context sections to generate query-specific answers.

        Args:
            prompt (str): Full prompt string containing context sections.

        Returns:
            str: Factual query-specific response.
        """
        # Extract user question
        question_match = re.search(r"User Question:\s*\"?(.*?)\"?(?=\n\n|\nResponse:|$)", prompt, re.DOTALL)
        question = question_match.group(1).strip() if question_match else ""
        q_lower = question.lower()

        # Extract context sections dynamically
        graph_text = ""
        telemetry_text = ""
        doc_text = ""

        if "--- KNOWLEDGE GRAPH CONTEXT ---" in prompt:
            graph_part = prompt.split("--- KNOWLEDGE GRAPH CONTEXT ---")[1]
            graph_text = graph_part.split("User Question:")[0].split("---")[0].strip()

        if "--- TELEMETRY ANALYTICS CONTEXT ---" in prompt:
            telemetry_part = prompt.split("--- TELEMETRY ANALYTICS CONTEXT ---")[1]
            telemetry_text = telemetry_part.split("User Question:")[0].split("---")[0].strip()

        if "--- TECHNICAL DOCUMENTATION RAG CONTEXT ---" in prompt:
            doc_part = prompt.split("--- TECHNICAL DOCUMENTATION RAG CONTEXT ---")[1]
            doc_text = doc_part.split("User Question:")[0].split("---")[0].strip()

        # Diagnostic questions ("why is Room A warm") must not be swallowed by the keyword branches below.
        is_diag = any(k in q_lower for k in ["why", "warm", "hot", "cold", "issue", "diagnose", "problem", "fault"])

        # 1. Question: Served Spaces / Areas
        if not is_diag and any(k in q_lower for k in ["area", "areas", "serve", "serves", "space", "spaces", "zone", "zones", "room", "rooms"]):
            for line in graph_text.split("\n"):
                if "Served Spaces" in line or "Zones" in line:
                    spaces = line.split(":", 1)[-1].strip()
                    space_bullets = "\n".join([f"• **{s.strip()}**" for s in spaces.split(",") if s.strip()])
                    return f"Air Handling Unit **AHU-01** serves the following spaces/zones:\n\n{space_bullets}"

        # 2. Question: Manufacturer / OEM
        if not is_diag and any(k in q_lower for k in ["manufacturer", "oem", "maker", "brand", "who made", "who manufactured"]):
            for line in graph_text.split("\n"):
                if "Manufacturer" in line:
                    mfg = line.split(":", 1)[-1].strip()
                    return f"Air Handling Unit **AHU-01** is manufactured by **{mfg}**."

        # 3. Question: Components / Hierarchy
        if not is_diag and any(k in q_lower for k in ["component", "components", "part", "parts", "hierarchy", "structure"]):
            for line in graph_text.split("\n"):
                if "Components:" in line:
                    comps = line.split(":", 1)[-1].strip()
                    comp_bullets = "\n".join([f"• **{c.strip()}**" for c in comps.split(",") if c.strip()])
                    return f"Air Handling Unit **AHU-01** consists of the following equipment components:\n\n{comp_bullets}"

        # 4. Question: Maintenance / History
        if not is_diag and any(k in q_lower for k in ["maintenance", "service", "history", "repair", "serviced", "technician"]):
            for line in graph_text.split("\n"):
                if "Recent Maintenance:" in line:
                    maint = line.split(":", 1)[-1].strip()
                    return f"Recent maintenance record for **AHU-01**:\n\n• {maint}"

        # 5. Question: Telemetry / Sensor Readings / Metrics / Anomalies
        if not is_diag and any(k in q_lower for k in ["telemetry", "sensor", "reading", "readings", "latest", "average", "avg", "metric", "metrics", "rpm", "pressure", "anomaly", "anomalies", "stat", "stats"]):
            if telemetry_text:
                formatted_lines = []
                for line in telemetry_text.split("\n"):
                    if line.strip():
                        formatted_lines.append(f"• **{line.strip()}**")
                return f"**Latest Telemetry Analytics for AHU-01 (24-Hour Time-Series)**:\n\n" + "\n".join(formatted_lines)
            return "Telemetry Engine is active and running, but no sensor metrics were matched for this specific query."

        # 6. Question: Diagnostics / Temperature / Faults
        if any(k in q_lower for k in ["temp", "temperature", "warm", "warmer", "hot", "issue", "diagnose", "problem", "fault", "why"]):
            # Built only from retrieved context, so the local engine never states numbers it was not given.
            parts = ["Operational diagnosis for **AHU-01** (local engine, no LLM key configured):", ""]
            spaces = next((l.split(":", 1)[-1].strip() for l in graph_text.split("\n") if "Served Spaces" in l), "")
            if spaces:
                parts.append(f"• **Topology**: AHU-01 serves {spaces}.")
            anomaly_lines = [l.strip().lstrip("•").strip() for l in telemetry_text.split("\n") if l.strip().startswith("•")]
            if anomaly_lines:
                parts.extend(f"• **Telemetry anomaly**: {a}" for a in anomaly_lines[:4])
            elif telemetry_text:
                parts.append("• **Telemetry**: no readings beyond the anomaly threshold in the analysed window.")
            passage = re.search(r'Passage #1 \((.*?)\):\s*"(.*?)"', doc_text, re.DOTALL)
            if passage:
                snippet = passage.group(2).strip()
                parts.append(f"• **OEM manual** ({passage.group(1)}): {snippet[:300]}{'…' if len(snippet) > 300 else ''}")
            if len(parts) == 2:
                parts.append("• No graph, telemetry or document evidence was retrieved for this question.")
            return "\n".join(parts)

        # 6. Generic Clean Synthesis Fallback
        clean_lines = []
        if graph_text:
            clean_lines.append(f"**Knowledge Graph Topology**:\n{graph_text}")
        if telemetry_text:
            clean_lines.append(f"**Telemetry Analytics**:\n{telemetry_text}")
        if doc_text:
            clean_lines.append(f"**Technical Documentation**:\n{doc_text}")

        if clean_lines:
            return f"Operational Summary for question *\"{question}\"*:\n\n" + "\n\n".join(clean_lines)

        return (
            "No evidence was retrieved for this question, so there is nothing to answer from. "
            "If it is about the asset's topology, check that Neo4j is running (see the sidebar)."
        )

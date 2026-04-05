from typing import List, Dict
from src.agents.base_agent import BaseAgent
import json
from loguru import logger

class GeneratorAgent(BaseAgent):
    def run(self, context_text: str, topics: List[str], personas: List[str], num_tests: int, acceptance_criteria: List[str] = None) -> List[Dict]:
        """
        Parses context and generates question/answer pairs governed by acceptance criteria.
        Returns a list of dicts: {"question": "...", "expected_answer": "...", "topic": "...", "persona": "..."}
        """
        model = self.system_config.llm.generator_model
        
        system_prompt = (
            "You are an expert testing engineer. Based on the provided context, "
            "generate highly diverse Q&A test cases. Return ONLY valid JSON."
        )
        
        user_prompt = f"""
        Context:
        {context_text[:10000]} # Trim to avoid context window explosion on giant pages

        Topics to cover: {topics}
        Personas to adopt for questions: {personas}
        Number of tests per topic: {num_tests}
        Acceptance Criteria limits to follow: {acceptance_criteria if acceptance_criteria else "None"}

        Output Format Requirement:
        Respond with a JSON object containing a key "test_cases", whose value is a list of objects.
        Each object must have the exact keys: 'question', 'expected_answer', 'topic', 'persona'.
        """
        
        logger.info(f"Generating {num_tests} tests per topic...")
        response = self.llm_client.generate_json(user_prompt, system_prompt, model=model)
        
        test_cases = response.get("test_cases", [])
        if not test_cases:
            logger.warning("GeneratorAgent did not return any test_cases in JSON.")
            
        return test_cases

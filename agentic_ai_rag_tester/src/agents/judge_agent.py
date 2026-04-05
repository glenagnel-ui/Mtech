from src.agents.base_agent import BaseAgent
from typing import Dict
from loguru import logger

class JudgeAgent(BaseAgent):
    def run(self, question: str, chatbot_answer: str, expected_answer: str) -> Dict:
        """
        Grades the chatbot answer against the expected answer.
        Returns: {"verdict": "CORRECT"|"PARTIAL"|"INCORRECT", "confidence_score": float}
        """
        model = self.system_config.llm.judge_model
        
        system_prompt = (
            "You are a strict academic evaluator. Grade the 'chatbot_answer' comparing it to the 'expected_answer'. "
            "Ignore minor formatting differences. Respond ONLY with valid JSON."
        )
        
        user_prompt = f"""
        Question Asked: {question}
        Expected Answer (Ground Truth): {expected_answer}
        Chatbot's Answer: {chatbot_answer}
        
        Determine if the Chatbot's Answer is:
        - "CORRECT": Contains all core semantics of the Expected Answer.
        - "PARTIAL": Missing some important details but technically not wrong.
        - "INCORRECT": Contradicts ground truth, hallucinates, or misses the point entirely.
        
        Output a JSON object with:
        "verdict": (one of the 3 labels)
        "confidence_score": (float between 0.0 and 1.0)
        "reason": (a brief one sentence justification)
        """
        
        logger.debug(f"Judging answer for question: {question}")
        response = self.llm_client.generate_json(user_prompt, system_prompt, model=model)
        
        verdict = response.get("verdict", "INCORRECT").upper()
        if verdict not in ["CORRECT", "PARTIAL", "INCORRECT"]:
            verdict = "INCORRECT"
            
        return {
            "verdict": verdict,
            "confidence_score": float(response.get("confidence_score", 0.0)),
            "reason": response.get("reason", "")
        }

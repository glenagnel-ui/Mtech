from src.agents.base_agent import BaseAgent
from typing import Dict
from loguru import logger

class ClassifierAgent(BaseAgent):
    def run(self, question: str, chatbot_answer: str, expected_answer: str, judge_reason: str) -> Dict:
        """
        Analyzes a failed test case and classifies the error mode.
        Returns JSON with {"failure_category": str, "explanation": str, "severity": int}
        """
        model = self.system_config.llm.classifier_model
        
        system_prompt = (
            "You are an AI diagnostic agent. Analyze why the chatbot failed to answer correctly. "
            "Respond ONLY with valid JSON."
        )
        
        user_prompt = f"""
        The chatbot failed answering the following question.
        Question: {question}
        Expected: {expected_answer}
        Actual Answer: {chatbot_answer}
        Judge Reason against it: {judge_reason}
        
        Classify the failure into one of these strict categories:
        - "hallucination": Chatbot made up fake info.
        - "missing_info": Chatbot refused to answer or claimed missing data when it should know.
        - "contradiction": Chatbot directly contradicted the core truth.
        - "off_topic": Chatbot rambled about an unrelated topic.
        - "other": Catch-all.
        
        Output JSON format:
        "failure_category": "..."
        "explanation": "..."
        "severity": (Integer 1 to 5, where 5 is a critical hallucination/contradiction)
        """
        
        logger.debug(f"Classifying failure for question: {question}")
        response = self.llm_client.generate_json(user_prompt, system_prompt, model=model)
        
        return {
            "failure_category": response.get("failure_category", "other"),
            "explanation": response.get("explanation", "Could not classify automatically."),
            "severity": response.get("severity", 3)
        }

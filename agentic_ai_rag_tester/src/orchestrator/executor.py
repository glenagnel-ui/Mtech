from src.core.config_loader import config_loader
from src.agents.generator_agent import GeneratorAgent
from src.agents.judge_agent import JudgeAgent
from src.agents.classifier_agent import ClassifierAgent
from src.tools.web_scraper import WebScraper
from src.tools.playwright_runner import PlaywrightRunner
from src.utils.file_utils import save_to_csv, load_from_csv
from src.utils.db_utils import NeonDBHandler
from src.utils.logger import logger
import os

class Executor:
    def __init__(self):
        self.config = config_loader.load_system_config()
        self.test_suite = config_loader.load_test_suite()
        self.generator = GeneratorAgent()
        self.judge = JudgeAgent()
        self.classifier = ClassifierAgent()
        self.scraper = WebScraper()
        self.runner = PlaywrightRunner()
        self.db_handler = NeonDBHandler()

    def generate_suite(self) -> str:
        """
        Scrapes content and generates test cases offline.
        """
        logger.info("Starting test suite generation...")
        all_tests = []
        for target in self.test_suite.targets:
            context = self.scraper.scrape_text(target.url)
            if not context:
                continue
            
            tests = self.generator.run(
                context_text=context,
                topics=target.topics,
                personas=self.test_suite.personas,
                num_tests=target.tests_per_topic,
                acceptance_criteria=target.acceptance_criteria
            )
            all_tests.extend(tests)

        filepath = save_to_csv(all_tests, "data/synthetic_data/prompt", prefix="generated_tests")
        logger.info(f"Test suite generation complete. Saved to {filepath}")
        return filepath

    def execute_pipeline(self, test_case_file: str = None):
        """
        Runs the full end-to-end pipeline: load tests -> run chatbot UI -> grade -> save.
        """
        logger.info("Starting Execution Pipeline...")
        
        if not test_case_file:
            test_case_file = self.generate_suite()
            
        test_cases = load_from_csv(test_case_file)
        results = []
        
        logger.info("Initializing Playwright...")
        self.runner.start()
        
        try:
            for tc in test_cases:
                question = tc.get("question")
                expected = tc.get("expected_answer")
                
                # 1. Ask Chatbot via UI
                chatbot_answer = self.runner.ask_chatbot(question)
                tc["chatbot_answer"] = chatbot_answer
                
                # 2. Judge Answer
                judge_result = self.judge.run(question, chatbot_answer, expected)
                tc.update(judge_result)
                
                # 3. Classify Failure if needed
                if judge_result["verdict"] != "CORRECT":
                    class_result = self.classifier.run(
                        question, chatbot_answer, expected, judge_result["reason"]
                    )
                    tc.update(class_result)
                else:
                    tc["failure_category"] = None
                    tc["severity"] = 0
                    tc["explanation"] = ""
                    
                results.append(tc)
                
        finally:
            self.runner.stop()
            
        # Save results
        filepath = save_to_csv(results, "reports/execution_results", prefix="execution_summary")
        self.db_handler.save_results(results)
        
        logger.info(f"Pipeline Execution Complete. Local results saved to {filepath}.")

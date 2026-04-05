from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from loguru import logger
from src.core.config_loader import config_loader
import os

class PlaywrightRunner:
    def __init__(self):
        self.system_config = config_loader.load_system_config()
        self.chatbot_url = config_loader.get_env("CHATBOT_URL")
        self.input_selector = config_loader.get_env("CHATBOT_INPUT_SELECTOR")
        self.send_selector = config_loader.get_env("CHATBOT_SEND_SELECTOR")
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self):
        logger.info("Initializing Playwright browser...")
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.system_config.browser.headless,
                slow_mo=self.system_config.browser.slow_mo
            )
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            self.page.set_default_timeout(self.system_config.browser.timeout_ms)
        except Exception as e:
            logger.error(f"Failed to start Playwright: {e}")
            self.stop()
            raise

    def stop(self):
        logger.info("Stopping Playwright browser...")
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def ask_chatbot(self, question: str) -> str:
        """
        Navigates to the chatbot, inputs the question, and streams/waits for the answer.
        Returns the raw answer text.
        """
        if not self.page:
            self.start()

        try:
            # We navigate per question to ensure clean state, or just reload.
            # Depending on chatbot, you might not want to reload every time.
            # Assuming reload to clear previous chat history.
            self.page.goto(self.chatbot_url)
            self.page.wait_for_selector(self.input_selector, state="visible")
            
            # Type question
            self.page.fill(self.input_selector, question)
            
            # Click send
            self.page.click(self.send_selector)
            
            # Since the user might need specific selectors to target the "answer" div,
            # we'll look for the last added paragraph or specific assistant message.
            # Without a specific config for that, we can just wait a fixed amount 
            # and extract text, or wait for network idle.
            logger.debug(f"Waiting for answer for question: {question[:30]}...")
            self.page.wait_for_load_state("networkidle")
            
            # NOTE: In reality, we'd need a CHATBOT_ANSWER_SELECTOR.
            # We will default to looking for `.agent-message`, `p`, or `div.markdown`.
            answer_selector = os.getenv("CHATBOT_ANSWER_SELECTOR", "body")
            
            # Wait a few seconds for inference to complete
            self.page.wait_for_timeout(3000) 
            
            elements = self.page.locator(answer_selector)
            if elements.count() > 0:
                answer = elements.last.inner_text()
                return answer
            return "No Answer Extracted"
            
        except PlaywrightTimeout:
            logger.error("Timeout occurred while interacting with the chatbot.")
            return "TIMEOUT"
        except Exception as e:
            logger.error(f"Error asking chatbot: {e}")
            return "ERROR"

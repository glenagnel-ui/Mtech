from src.orchestrator.executor import Executor
from src.utils.logger import configure_logger

if __name__ == "__main__":
    configure_logger("INFO")
    executor = Executor()
    print("Generating offline test cases...")
    executor.generate_suite()
    print("Done. Check data/synthetic_data/prompt/")

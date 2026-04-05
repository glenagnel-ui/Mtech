from src.orchestrator.executor import Executor
from src.utils.logger import configure_logger
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the RAG testing pipeline.")
    parser.add_argument("--test-file", type=str, help="Path to a predefined CSV test file (if skipping generation).")
    args = parser.parse_args()

    configure_logger("DEBUG")
    executor = Executor()
    
    executor.execute_pipeline(test_case_file=args.test_file)

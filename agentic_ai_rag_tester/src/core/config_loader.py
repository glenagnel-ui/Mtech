import os
from pathlib import Path
from pydantic import BaseModel, Field
import yaml
from dotenv import load_dotenv

# Load env variables from .env if present
load_dotenv()

class LLMConfig(BaseModel):
    generator_model: str = "gpt-4o-mini"
    judge_model: str = "gpt-4o"
    classifier_model: str = "gpt-4o"

class BrowserConfig(BaseModel):
    headless: bool = True
    timeout_ms: int = 30000
    slow_mo: int = 50

class LoggingConfig(BaseModel):
    level: str = "INFO"

class SystemConfig(BaseModel):
    llm: LLMConfig
    browser: BrowserConfig
    logging: LoggingConfig

class TargetConfig(BaseModel):
    url: str
    topics: list[str]
    tests_per_topic: int
    acceptance_criteria: list[str] = Field(default_factory=list)

class TestSuiteConfig(BaseModel):
    targets: list[TargetConfig]
    personas: list[str]

class ConfigLoader:
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)

    def load_system_config(self) -> SystemConfig:
        config_path = self.config_dir / "system_config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Missing system config at {config_path}")
        
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        return SystemConfig(**data)

    def load_test_suite(self) -> TestSuiteConfig:
        config_path = self.config_dir / "test_suite.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Missing test suite config at {config_path}")
            
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        return TestSuiteConfig(**data)

    def get_env(self, key: str, required: bool = True) -> str:
        val = os.getenv(key)
        if required and not val:
            raise ValueError(f"Environment variable {key} is required but missing.")
        return val or ""

config_loader = ConfigLoader()

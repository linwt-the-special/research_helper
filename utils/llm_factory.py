from typing import Any
import time
from litellm import completion
from utils.config_loader import config_loader
import litellm

class LLMFactory:
    @staticmethod
    def get_completion(agent_name: str, messages: list, **kwargs) -> Any:
        conf = config_loader.get_agent_config(agent_name)
        call_kwargs = {
            "model": conf.get("model"),
            "messages": messages,
            "api_base": conf.get("api_base"),
            "api_key": conf.get("api_key"),
            "timeout": config_loader.get_settings().get("timeout", 60)
        }
        call_kwargs.update(kwargs)
        
        for attempt in range(3):
            try:
                return completion(**call_kwargs)
            except litellm.exceptions.RateLimitError:
                if attempt < 2:
                    time.sleep((attempt + 1) * 5)
                    continue
                raise
            except Exception as e: raise e

llm_factory = LLMFactory()

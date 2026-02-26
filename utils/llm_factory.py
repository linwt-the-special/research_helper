from typing import Any
import time
from litellm import completion
from utils.config_loader import config_loader
import litellm

class LLMFactory:
    @staticmethod
    def get_completion(agent_name: str, messages: list, **kwargs) -> Any:
        """
        统一的模型调用接口
        """
        conf = config_loader.get_agent_config(agent_name)
        model = conf.get("model")
        api_base = conf.get("api_base")
        api_key = conf.get("api_key")
        
        call_kwargs = {
            "model": model,
            "messages": messages,
            "api_base": api_base,
            "api_key": api_key,
            "timeout": config_loader.get_settings().get("timeout", 60)
        }
        call_kwargs.update(kwargs)
        
        for attempt in range(3):
            try:
                return completion(**call_kwargs)
            except litellm.exceptions.RateLimitError:
                if attempt < 2:
                    wait_time = (attempt + 1) * 5
                    time.sleep(wait_time)
                    continue
                raise
            except Exception as e:
                raise e

llm_factory = LLMFactory()

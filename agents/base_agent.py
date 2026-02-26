from utils.llm_factory import llm_factory

class BaseAgent:
    def __init__(self, name: str):
        self.name = name

    def call_llm(self, prompt: str, system_message: str = "You are a helpful research assistant.") -> str:
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        response = llm_factory.get_completion(self.name, messages)
        return response.choices[0].message.content

import requests
import time

class Agent:
    def __init__(self, model_name: str, name: str, temperature: float, sleep_time: float = 0):
        self.model_name = model_name
        self.name = name
        self.temperature = temperature
        self.memory_lst = []
        self.sleep_time = sleep_time

    def query(self, messages: list, temperature: float = None) -> str:
        """
        Query Ollama locally with a list of chat messages.
        """
        time.sleep(self.sleep_time)
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,  # Fixed variable name
                    "temperature": temperature if temperature is not None else self.temperature,
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            if "message" in result and "content" in result["message"]:
                return result["message"]["content"].strip()
            elif "response" in result:  # fallback for /generate-style response
                return result["response"].strip()
            else:
                print("[ERROR] Unexpected Ollama response:", result)
                return "[Error: Unexpected Ollama response]"
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Ollama query failed: {e}")
            return "[Error: Ollama query failed]"

    def set_meta_prompt(self, meta_prompt: str):
        self.memory_lst.append({"role": "system", "content": meta_prompt})

    def add_event(self, event: str):
        self.memory_lst.append({"role": "user", "content": event})

    def add_memory(self, memory: str):
        self.memory_lst.append({"role": "assistant", "content": memory})
        print(f"----- {self.name} -----\n{memory}\n")

    def ask(self, temperature: float = None):
        return self.query(self.memory_lst, temperature=temperature)
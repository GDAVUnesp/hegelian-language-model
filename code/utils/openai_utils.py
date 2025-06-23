# utils/ollama_utils.py

# Context limits for local models (approximate, adjust per actual config)
model2max_context = {
    "gemma3:4b": 2048, # model and number of tokens
    "gemma:2b": 2048,
    "deepseek-r1:8b": 4096,
}

class OutOfQuotaException(Exception):
    "Not really used in Ollama, kept for compatibility"
    def __init__(self, key="N/A", cause=None):
        super().__init__(f"No quota for key: {key}")
        self.key = key
        self.cause = cause

    def __str__(self):
        return f"{super().__str__()}. Caused by {self.cause}" if self.cause else super().__str__()

class AccessTerminatedException(Exception):
    "Not applicable to local models, but kept for compatibility"
    def __init__(self, key="N/A", cause=None):
        super().__init__(f"Access terminated for key: {key}")
        self.key = key
        self.cause = cause

    def __str__(self):
        return f"{super().__str__()}. Caused by {self.cause}" if self.cause else super().__str__()

def num_tokens_from_string(string: str, model_name: str) -> int:
    """
    Approximate token count for local models (not exact, but useful for truncation).
    A simple rule of thumb: 1 token ≈ 4 characters in English.
    """
    approx_tokens = len(string) // 4
    return approx_tokens
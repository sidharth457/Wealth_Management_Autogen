import os


# LLM provider config (supports openai, azure_openai, gemini)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_API_KEY = os.getenv("LLM_API_KEY", "sk-REPLACE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "gemini-REPLACE")
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "120"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))

def get_llm_config():
	if LLM_PROVIDER == "gemini":
		return {
			"provider": "gemini",
			"model": LLM_MODEL,
			"api_key": GEMINI_API_KEY,
			"timeout": TIMEOUT_SECONDS,
			"max_tokens": MAX_TOKENS
		}
	else:
		return {
			"provider": LLM_PROVIDER,
			"model": LLM_MODEL,
			"api_key": LLM_API_KEY,
			"timeout": TIMEOUT_SECONDS,
			"max_tokens": MAX_TOKENS
		}

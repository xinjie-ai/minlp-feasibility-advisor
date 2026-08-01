# test_qwen.py

from llm_client import ask_llm

response = ask_llm(
    "Reply with only the word hello."
)

print(repr(response))
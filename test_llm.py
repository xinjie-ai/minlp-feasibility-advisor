# test_llm.py

from llm_client import ask_llm

response = ask_llm(
    "Reply with only the word hello."
)

print(response)
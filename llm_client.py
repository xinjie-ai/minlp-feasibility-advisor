import requests


def ask_llm(
    prompt,
    model="qwen3:8b"
):

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 500,
                "temperature": 0.2,
            },
        },
        timeout=300,
    )

    response.raise_for_status()

    result = response.json()

    print("\nOLLAMA RESPONSE:")
    print(result)

    return result["response"]
import requests
import json

def get_code_review(code: str):
    url = "http://84.201.152.196:8020/v1/completions"
    headers = {
        "Authorization": "3rL3VN4295xYPlTNMzvt32VGwQl45e1b",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-nemo-instruct-2407",
        "messages": [
            {"role": "system", "content": "отвечай на русском языке"},
            {"role": "user", "content": code}
        ],
        "max_tokens": 1000,
        "temperature": 0.3
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Пример использования
code = "def calculate(x, y): return x + y"
review = get_code_review(code)
print(json.dumps(review, indent=2, ensure_ascii=False))
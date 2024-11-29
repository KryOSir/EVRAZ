import requests
import json


def find_relevant_reviews(code, reviews_db):
    relevant_reviews = []
    for review_entry in reviews_db:
        if code in review_entry["code"]:  # Это упрощенная версия поиска
            relevant_reviews.append(review_entry["review"])
    return relevant_reviews


def get_code_review_with_rag(code: str, reviews_db: list):
    # Извлекаем релевантные отзывы из базы
    relevant_reviews = find_relevant_reviews(code, reviews_db)

    # Подготавливаем данные для запроса
    url = "http://84.201.152.196:8020/v1/completions"
    headers = {
        "Authorization": "3rL3VN4295xYPlTNMzvt32VGwQl45e1b",
        "Content-Type": "application/json"
    }

    # Формируем запрос с добавлением отзывов из базы
    payload = {
        "model": "mistral-nemo-instruct-2407",
        "messages": [
            {"role": "system", "content": "отвечай на русском языке"},
            {"role": "user",
             "content": f"Вот новый код: {code}. Вот несколько отзывов из базы, которые могут быть полезными: {', '.join(relevant_reviews)}"}
        ],
        "max_tokens": 1000,
        "temperature": 0.3
    }

    # Отправляем запрос в модель
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


# Пример использования
reviews_db = [
    {"code": "def calculate(x, y): return x + y",
     "review": "Функция работает правильно, но можно добавить типизацию для параметров и вернуть значение явно."},
    {"code": "def multiply(a, b): return a * b",
     "review": "Этот код хорош, но желательно обработать исключения при передаче некорректных типов данных."}
]

code = "def calculate(x, y): return x + y"
review = get_code_review_with_rag(code, reviews_db)
print(json.dumps(review, indent=2, ensure_ascii=False))

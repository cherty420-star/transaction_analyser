"""
Создание демонстрационных данных.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

print("Создание демо-данных...")

# Создаем папку data если её нет
os.makedirs('data', exist_ok=True)

# Генерация данных
data = []
start_date = datetime(2023, 10, 1)

for i in range(200):
    date = start_date + timedelta(days=random.randint(0, 90))
    is_expense = random.random() < 0.8

    if is_expense:
        amount = -random.uniform(100, 20000)
        categories = ['Супермаркеты', 'Кафе', 'Транспорт', 'Развлечения', 'Одежда']
    else:
        amount = random.uniform(50000, 100000)
        categories = ['Зарплата', 'Перевод', 'Возврат']

    data.append({
        'Дата операции': date,
        'Дата платежа': date + timedelta(days=random.randint(0, 3)),
        'Номер карты': random.choice(['1234', '5678']),
        'Статус': 'OK',
        'Сумма операции': round(amount, 2),
        'Валюта операции': 'RUB',
        'Сумма платежа': round(amount, 2),
        'Валюта платежа': 'RUB',
        'Кешбэк': round(abs(amount) * 0.01, 2) if amount < 0 else 0,
        'Категория': random.choice(categories),
        'MCC': random.randint(1000, 9999),
        'Описание': f'Транзакция {i + 1} в {random.choice(categories)}',
        'Бонусы (включая кешбэк)': round(abs(amount) * 0.02, 2) if amount < 0 else 0,
        'Округление на Инвесткопилку': round(random.uniform(0, 50), 2),
        'Сумма операции с округлением': round(amount - (amount % 10), 2)
    })

# Создаем DataFrame и сохраняем
df = pd.DataFrame(data)
df.to_excel('data/operations.xlsx', index=False)

print(f"✅ Создан файл data/operations.xlsx с {len(df)} транзакциями")
print(f"📅 Период: {df['Дата операции'].min().date()} - {df['Дата операции'].max().date()}")
"""
Генерация тестовых данных для анализа транзакций.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Настройки
NUM_TRANSACTIONS = 1000
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2023, 12, 31)

# Категории транзакций
CATEGORIES = [
    'Супермаркеты', 'Кафе и рестораны', 'Транспорт', 'Здоровье',
    'Развлечения', 'Одежда', 'Электроника', 'Красота',
    'Образование', 'Переводы', 'Наличные', 'Интернет'
]

# Статусы транзакций
STATUSES = ['OK', 'FAILED', 'PENDING']

# Валюты
CURRENCIES = ['RUB', 'USD', 'EUR']


def generate_transactions(n: int) -> pd.DataFrame:
    """Генерирует тестовые транзакции."""
    data = []

    for i in range(n):
        # Случайная дата
        days_diff = (END_DATE - START_DATE).days
        random_days = random.randint(0, days_diff)
        date = START_DATE + timedelta(days=random_days)

        # Сумма операции (80% расходов, 20% доходов)
        if random.random() < 0.8:
            amount = -random.uniform(100, 50000)
        else:
            amount = random.uniform(1000, 100000)

        # Платеж может отличаться из-за курса валют
        payment_amount = amount * random.uniform(0.95, 1.05)

        transaction = {
            'Дата операции': date,
            'Дата платежа': date + timedelta(days=random.randint(0, 3)),
            'Номер карты': f"{random.randint(1000, 9999)}",
            'Статус': random.choice(STATUSES),
            'Сумма операции': round(amount, 2),
            'Валюта операции': random.choice(CURRENCIES),
            'Сумма платежа': round(payment_amount, 2),
            'Валюта платежа': 'RUB',
            'Кешбэк': round(abs(amount) * 0.01, 2) if amount < 0 else 0,
            'Категория': random.choice(CATEGORIES),
            'MCC': random.randint(1000, 9999),
            'Описание': f"Платеж {i + 1} в {random.choice(CATEGORIES)}",
            'Бонусы (включая кешбэк)': round(abs(amount) * 0.02, 2) if amount < 0 else 0,
            'Округление на Инвесткопилку': round(random.uniform(0, 50), 2),
            'Сумма операции с округлением': round(amount - (amount % 10), 2)
        }

        data.append(transaction)

    return pd.DataFrame(data)


if __name__ == "__main__":
    print("Генерация тестовых данных...")
    df = generate_transactions(NUM_TRANSACTIONS)

    # Сохраняем в Excel
    output_file = "data/operations.xlsx"
    df.to_excel(output_file, index=False)

    print(f"Сгенерировано {NUM_TRANSACTIONS} транзакций")
    print(f"Сохранено в {output_file}")

    # Статистика
    print(f"\nСтатистика:")
    print(f"  Расходы: {len(df[df['Сумма операции'] < 0])}")
    print(f"  Доходы: {len(df[df['Сумма операции'] > 0])}")
    print(f"  Период: {df['Дата операции'].min().date()} - {df['Дата операции'].max().date()}")
    print(f"  Категории: {df['Категория'].nunique()}")
"""
Создание реальных тестовых данных.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

print("Создание тестовых данных для транзакций...")

# Создаем папку data если её нет
os.makedirs('data', exist_ok=True)

# Генерация данных за декабрь 2023
data = []
start_date = datetime(2023, 12, 1)

# Карты
cards = ['1234', '5678', '9012']

# Категории
expense_categories = ['Супермаркеты', 'Кафе и рестораны', 'Транспорт',
                      'Развлечения', 'Одежда', 'Электроника', 'Красота']
income_categories = ['Зарплата', 'Перевод', 'Возврат средств']

for i in range(150):
    # Дата в декабре 2023
    date = start_date + timedelta(days=random.randint(0, 30))

    # 85% расходов, 15% доходов
    is_expense = random.random() < 0.85

    if is_expense:
        # Расходы с разными суммами для тестирования округления
        base_amount = random.choice([1712.50, 845.30, 2317.80, 956.40, 1823.90])
        amount = -base_amount
        category = random.choice(expense_categories)
        description = f"Оплата: {category}"
    else:
        # Доходы
        amount = random.choice([50000.00, 75000.00, 100000.00])
        category = random.choice(income_categories)
        description = f"Поступление: {category}"

    # Для инвесткопилки: округление
    if is_expense:
        rounded_amount = base_amount + (50 - (base_amount % 50)) if base_amount % 50 != 0 else base_amount
        investment = rounded_amount - base_amount
    else:
        investment = 0

    transaction = {
        'Дата операции': date,
        'Дата платежа': date + timedelta(days=random.randint(0, 3)),
        'Номер карты': random.choice(cards),
        'Статус': 'OK',
        'Сумма операции': round(amount, 2),
        'Валюта операции': 'RUB',
        'Сумма платежа': round(amount, 2),
        'Валюта платежа': 'RUB',
        'Кешбэк': round(abs(amount) * 0.01, 2) if amount < 0 else 0,
        'Категория': category,
        'MCC': random.randint(1000, 9999),
        'Описание': description,
        'Бонусы (включая кешбэк)': round(abs(amount) * 0.02, 2) if amount < 0 else 0,
        'Округление на Инвесткопилку': round(investment, 2),
        'Сумма операции с округлением': round(amount - investment if amount < 0 else amount, 2)
    }

    data.append(transaction)

# Сортируем по дате
data.sort(key=lambda x: x['Дата операции'])

# Создаем DataFrame и сохраняем
df = pd.DataFrame(data)
output_file = "data/operations.xlsx"
df.to_excel(output_file, index=False)

print(f"✅ Создан файл {output_file}")
print(f"📊 Статистика:")
print(f"  📅 Период: {df['Дата операции'].min().date()} - {df['Дата операции'].max().date()}")
print(f"  💳 Карт: {df['Номер карты'].nunique()}")
print(f"  🏷️ Категорий: {df['Категория'].nunique()}")
print(f"  📉 Расходов: {len(df[df['Сумма операции'] < 0])}")
print(f"  📈 Доходов: {len(df[df['Сумма операции'] > 0])}")
print(f"  💰 Общая сумма расходов: {abs(df[df['Сумма операции'] < 0]['Сумма операции'].sum()):.2f} руб.")
print(f"  💰 Общая сумма доходов: {df[df['Сумма операции'] > 0]['Сумма операции'].sum():.2f} руб.")

# Примеры транзакций для инвесткопилки
print("\n🔍 Примеры транзакций для инвесткопилки (лимит 50):")
expenses = df[df['Сумма операции'] < 0].head(5)
for idx, row in expenses.iterrows():
    amount = abs(row['Сумма операции'])
    rounded = amount + (50 - (amount % 50)) if amount % 50 != 0 else amount
    investment = rounded - amount
    print(f"  {row['Дата операции'].date()}: {amount:.2f} руб. → {rounded:.2f} руб. "
          f"(+{investment:.2f} руб. в копилку)")

print("\n📁 Файл готов к использованию!")
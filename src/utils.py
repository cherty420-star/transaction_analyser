"""
Модуль вспомогательных функций для работы с данными.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import requests
from dotenv import load_dotenv
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()


def create_demo_data() -> pd.DataFrame:
    """
    Создает демонстрационные данные для тестирования.

    Returns:
        DataFrame с демо-транзакциями
    """
    logger.info("Создание демонстрационных данных")

    data = []
    # Создаем данные за декабрь 2023 для тестирования
    start_date = datetime(2023, 12, 1)

    for i in range(100):
        # Данные за декабрь 2023
        date = start_date + timedelta(days=i % 25)  # 25 дней декабря

        is_expense = i < 80  # 80% расходов

        if is_expense:
            amount = -float((i + 1) * 100 + i % 10 * 50)
            categories = ['Супермаркеты', 'Кафе', 'Транспорт', 'Развлечения', 'Одежда']
        else:
            amount = float(50000 + i * 1000)
            categories = ['Зарплата']

        # Для инвесткопилки: суммы, которые будут округляться
        # Например: 1712.50 округлится до 1750 при лимите 50
        if i % 10 == 0:  # Каждая 10-я транзакция
            amount = -1712.50  # Будет округляться

        data.append({
            'Дата операции': date,
            'Дата платежа': date + timedelta(days=2),
            'Номер карты': '1234' if i % 2 == 0 else '5678',
            'Статус': 'OK',
            'Сумма операции': amount,
            'Валюта операции': 'RUB',
            'Сумма платежа': amount,
            'Валюта платежа': 'RUB',
            'Кешбэк': abs(amount) * 0.01 if amount < 0 else 0,
            'Категория': categories[i % len(categories)] if is_expense else 'Зарплата',
            'MCC': 5411 if i % 4 == 0 else 5812,
            'Описание': f'Транзакция {i + 1}: {categories[i % len(categories)] if is_expense else "Зарплата"}',
            'Бонусы (включая кешбэк)': abs(amount) * 0.02 if amount < 0 else 0,
            'Округление на Инвесткопилку': i % 10,
            'Сумма операции с округлением': amount - (amount % 10)
        })

    df = pd.DataFrame(data)
    logger.info(f"Создано {len(df)} демо-транзакций за декабрь 2023")
    return df


def load_excel_data(filepath: str = "data/operations.xlsx") -> pd.DataFrame:
    """
    Загружает данные из Excel файла. Если файл не найден, создает демо-данные.

    Args:
        filepath: Путь к Excel файлу

    Returns:
        DataFrame с транзакциями
    """
    try:
        logger.info(f"Загрузка данных из {filepath}")

        # Пробуем загрузить файл
        df = pd.read_excel(filepath)

        # Преобразование дат
        date_columns = ['Дата операции', 'Дата платежа']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Заполнение пустых значений
        if 'Категория' in df.columns:
            df['Категория'] = df['Категория'].fillna('Неизвестно')
        if 'Описание' in df.columns:
            df['Описание'] = df['Описание'].fillna('')

        logger.info(f"Успешно загружено {len(df)} транзакций")
        return df

    except FileNotFoundError:
        logger.warning(f"Файл {filepath} не найден, создаем демо-данные")
        return create_demo_data()
    except Exception as e:
        logger.error(f"Ошибка при загрузке файла: {str(e)}. Создаем демо-данные")
        return create_demo_data()


def filter_by_date_range(
    df: pd.DataFrame,
    end_date: str,
    period: str = 'M'
) -> pd.DataFrame:
    """
    Фильтрует транзакции по временному периоду.

    Args:
        df: DataFrame с транзакциями
        end_date: Конечная дата в формате 'YYYY-MM-DD HH:MM:SS'
        period: Период ('W' - неделя, 'M' - месяц, 'Y' - год, 'ALL' - все)

    Returns:
        Отфильтрованный DataFrame
    """
    try:
        if df.empty or 'Дата операции' not in df.columns:
            logger.warning("Нет данных для фильтрации")
            return pd.DataFrame()

        end_dt = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

        # Определяем начальную дату в зависимости от периода
        if period == 'W':
            start_dt = end_dt - timedelta(days=end_dt.weekday())
        elif period == 'M':
            start_dt = end_dt.replace(day=1)
        elif period == 'Y':
            start_dt = end_dt.replace(month=1, day=1)
        elif period == 'ALL':
            mask = df['Дата операции'] <= end_dt
            filtered = df[mask].copy()
            logger.info(f"Отфильтровано {len(filtered)} транзакций (ALL)")
            return filtered
        else:
            raise ValueError(f"Неизвестный период: {period}")

        mask = (df['Дата операции'] >= start_dt) & (df['Дата операции'] <= end_dt)
        filtered = df[mask].copy()

        logger.info(
            f"Отфильтровано {len(filtered)} транзакций "
            f"за период {period} ({start_dt.date()} - {end_dt.date()})"
        )
        return filtered

    except ValueError as e:
        logger.error(f"Ошибка в формате даты или периода: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Неожиданная ошибка при фильтрации: {e}")
        return pd.DataFrame()


def get_currency_rates(currencies: List[str]) -> Dict[str, float]:
    """
    Получает текущие курсы валют.

    Args:
        currencies: Список валютных пар

    Returns:
        Словарь с курсами валют к RUB
    """
    try:
        logger.info(f"Получение курсов валют: {currencies}")

        # Моковые данные для примера
        mock_rates = {
            'USD': 91.45,
            'EUR': 99.12,
            'CNY': 12.75,
            'GBP': 115.80,
            'JPY': 0.62
        }

        result = {}
        for currency in currencies:
            rate = mock_rates.get(currency.upper())
            if rate:
                result[currency] = rate
            else:
                logger.warning(f"Курс для {currency} не найден")
                result[currency] = 0.0

        return result

    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
        return {currency: 0.0 for currency in currencies}


def get_stock_prices(stocks: List[str]) -> Dict[str, float]:
    """
    Получает текущие цены акций.

    Args:
        stocks: Список тикеров акций

    Returns:
        Словарь с ценами акций в USD
    """
    try:
        logger.info(f"Получение цен акций: {stocks}")

        # Моковые данные для примера
        mock_prices = {
            'AAPL': 185.64,
            'AMZN': 145.22,
            'GOOGL': 135.81,
            'MSFT': 370.92,
            'TSLA': 235.43,
            'NVDA': 488.88,
            'META': 322.12
        }

        result = {}
        for stock in stocks:
            price = mock_prices.get(stock.upper())
            if price:
                result[stock] = price
            else:
                logger.warning(f"Цена для акции {stock} не найдена")
                result[stock] = 0.0

        return result

    except Exception as e:
        logger.error(f"Ошибка при получении цен акций: {e}")
        return {stock: 0.0 for stock in stocks}


def convert_to_json_serializable(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Конвертирует DataFrame в список словарей для JSON.

    Args:
        df: DataFrame для конвертации

    Returns:
        Список словарей
    """
    try:
        if df.empty:
            return []

        result = []
        for _, row in df.iterrows():
            item = {}
            for col in df.columns:
                value = row[col]

                # Обработка специальных типов
                if pd.isna(value):
                    item[col] = None
                elif isinstance(value, (pd.Timestamp, datetime)):
                    item[col] = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, (pd.Timedelta, timedelta)):
                    item[col] = str(value)
                elif isinstance(value, (int, float)):
                    item[col] = float(value)
                else:
                    item[col] = str(value)

            result.append(item)

        return result

    except Exception as e:
        logger.error(f"Ошибка при конвертации в JSON: {e}")
        return []
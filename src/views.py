"""
Модуль для генерации JSON-ответов веб-страниц.
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd
from . import utils

logger = logging.getLogger(__name__)


def get_time_based_greeting(current_time: datetime) -> str:
    """
    Возвращает приветствие в зависимости от времени суток.

    Args:
        current_time: Текущее время

    Returns:
        Приветствие: 'Доброе утро', 'Добрый день', 'Добрый вечер', 'Доброй ночи'
    """
    hour = current_time.hour

    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_card_statistics(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Анализирует статистику по картам.

    Args:
        df: DataFrame с транзакциями

    Returns:
        Словарь с статистикой по картам
    """
    if df.empty or 'Номер карты' not in df.columns:
        return {}

    cards_stats = {}

    for card in df['Номер карты'].unique():
        if pd.isna(card):
            continue

        card_df = df[df['Номер карты'] == card]

        # Сумма расходов (отрицательные значения или положительные?)
        # Предполагаем, что расходы - отрицательные значения
        expenses = card_df[card_df['Сумма операции'] < 0]
        total_spent = abs(expenses['Сумма операции'].sum())

        # Кешбэк 1% от расходов
        cashback = total_spent * 0.01

        cards_stats[str(card)] = {
            'total_spent': round(float(total_spent), 2),
            'cashback': round(float(cashback), 2),
            'transactions_count': len(card_df)
        }

    return cards_stats


def get_top_transactions(df: pd.DataFrame, top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Возвращает топ-N транзакций по сумме платежа.

    Args:
        df: DataFrame с транзакциями
        top_n: Количество транзакций в топе

    Returns:
        Список словарей с информацией о транзакциях
    """
    if df.empty:
        return []

    # Берем самые крупные транзакции по модулю
    df_copy = df.copy()
    df_copy['abs_amount'] = df_copy['Сумма платежа'].abs()
    top_df = df_copy.nlargest(top_n, 'abs_amount')

    result = []
    for _, row in top_df.iterrows():
        transaction = {
            'date': row['Дата операции'].strftime('%Y-%m-%d %H:%M:%S')
                    if not pd.isna(row['Дата операции']) else None,
            'amount': float(row['Сумма операции']),
            'payment_amount': float(row['Сумма платежа']),
            'category': str(row.get('Категория', 'Неизвестно')),
            'description': str(row.get('Описание', '')),
            'currency': str(row.get('Валюта операции', 'RUB'))
        }
        result.append(transaction)

    return result


def main_page(date_str: str) -> Dict[str, Any]:
    """
    Генерирует JSON-ответ для главной страницы.

    Args:
        date_str: Дата и время в формате 'YYYY-MM-DD HH:MM:SS'

    Returns:
        JSON-совместимый словарь с данными для главной страницы
    """
    try:
        logger.info(f"Генерация главной страницы для даты: {date_str}")

        # Загрузка пользовательских настроек
        try:
            with open('user_settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except FileNotFoundError:
            logger.warning("Файл настроек не найден, используются настройки по умолчанию")
            settings = {
                'user_currencies': ['USD', 'EUR'],
                'user_stocks': ['AAPL', 'MSFT']
            }

        # Загрузка данных
        df = utils.load_excel_data()

        # Фильтрация данных за месяц
        filtered_df = utils.filter_by_date_range(df, date_str, 'M')

        if filtered_df.empty:
            logger.warning("Нет данных за указанный период")
            return {'error': 'Нет данных за указанный период'}

        # Приветствие
        current_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        greeting = get_time_based_greeting(current_time)

        # Статистика по картам
        cards_stats = get_card_statistics(filtered_df)

        # Топ транзакций
        top_transactions = get_top_transactions(filtered_df, 5)

        # Курсы валют
        currencies = utils.get_currency_rates(settings.get('user_currencies', []))

        # Цены акций
        stocks = utils.get_stock_prices(settings.get('user_stocks', []))

        # Общая статистика
        total_spent = abs(filtered_df[filtered_df['Сумма операции'] < 0]['Сумма операции'].sum())
        total_income = filtered_df[filtered_df['Сумма операции'] > 0]['Сумма операции'].sum()
        avg_transaction = filtered_df['Сумма операции'].mean()

        response = {
            'status': 'success',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': {
                'greeting': greeting,
                'period': {
                    'start': filtered_df['Дата операции'].min().strftime('%Y-%m-%d'),
                    'end': date_str.split()[0],
                    'days': (filtered_df['Дата операции'].max() - filtered_df['Дата операции'].min()).days + 1
                },
                'cards': cards_stats,
                'transactions': {
                    'total_count': len(filtered_df),
                    'top_5': top_transactions,
                    'statistics': {
                        'total_spent': round(float(total_spent), 2),
                        'total_income': round(float(total_income), 2),
                        'average_transaction': round(float(avg_transaction), 2),
                        'transaction_types': {
                            'expenses': len(filtered_df[filtered_df['Сумма операции'] < 0]),
                            'income': len(filtered_df[filtered_df['Сумма операции'] > 0])
                        }
                    }
                },
                'financial_data': {
                    'exchange_rates': currencies,
                    'stock_prices': stocks
                },
                'summary': {
                    'cards_count': len(cards_stats),
                    'has_data': not filtered_df.empty,
                    'message': f"Анализ за период с {filtered_df['Дата операции'].min().strftime('%d.%m.%Y')}"
                }
            }
        }

        logger.info("Главная страница успешно сгенерирована")
        return response

    except ValueError as e:
        logger.error(f"Ошибка формата даты: {e}")
        return {
            'status': 'error',
            'error': f'Неверный формат даты: {str(e)}',
            'expected_format': 'YYYY-MM-DD HH:MM:SS'
        }
    except Exception as e:
        logger.error(f"Ошибка при генерации главной страницы: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }
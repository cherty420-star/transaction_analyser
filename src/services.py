"""
Модуль бизнес-логики сервисов.
"""
import json
import logging
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from . import utils

logger = logging.getLogger(__name__)


def investment_bank(
        month: str,
        transactions: List[Dict[str, Any]],
        limit: int
) -> Dict[str, Any]:
    """
    Расчет суммы для инвесткопилки через округление транзакций.

    Args:
        month: Месяц в формате 'YYYY-MM'
        transactions: Список транзакций
        limit: Лимит округления (10, 50, 100)

    Returns:
        Словарь с результатом расчета
    """
    try:
        logger.info(f"Расчет инвесткопилки для {month}, лимит {limit}")

        if not transactions:
            logger.warning("Нет данных о транзакциях")
            return {
                'status': 'error',
                'error': 'Нет данных о транзакциях',
                'total_investment': 0.0
            }

        if limit not in [10, 50, 100]:
            logger.warning(f"Неподдерживаемый лимит округления: {limit}")
            return {
                'status': 'error',
                'error': 'Лимит должен быть 10, 50 или 100',
                'total_investment': 0.0
            }

        total_investment = 0.0
        rounded_transactions = []

        for transaction in transactions:
            # Проверяем, что транзакция в нужном месяце
            try:
                trans_date = transaction.get('Дата операции')
                if not trans_date:
                    continue

                # Преобразуем дату
                if isinstance(trans_date, str):
                    trans_dt = datetime.strptime(trans_date.split()[0], '%Y-%m-%d')
                else:
                    trans_dt = trans_date

                # Проверяем месяц
                if trans_dt.strftime('%Y-%m') != month:
                    continue

                # Получаем сумму операции
                amount = float(transaction.get('Сумма операции', 0))

                # Округляем только расходы (отрицательные суммы)
                if amount < 0:
                    abs_amount = abs(amount)
                    rounded = ((abs_amount + limit - 1) // limit) * limit
                    investment = rounded - abs_amount

                    if investment > 0:
                        total_investment += investment

                        rounded_transactions.append({
                            'original_amount': round(abs_amount, 2),
                            'rounded_amount': rounded,
                            'investment': round(investment, 2),
                            'date': trans_date,
                            'description': transaction.get('Описание', ''),
                            'category': transaction.get('Категория', '')
                        })

            except (ValueError, TypeError) as e:
                logger.warning(f"Ошибка обработки транзакции: {e}")
                continue

        # Сортируем транзакции по сумме инвестирования
        rounded_transactions.sort(key=lambda x: x['investment'], reverse=True)

        response = {
            'status': 'success',
            'month': month,
            'rounding_limit': limit,
            'total_investment': round(total_investment, 2),
            'transactions_count': len(rounded_transactions),
            'transactions': rounded_transactions[:10],  # Только топ-10
            'statistics': {
                'avg_investment_per_transaction': round(
                    total_investment / len(rounded_transactions) if rounded_transactions else 0,
                    2
                ),
                'max_investment': max(
                    [t['investment'] for t in rounded_transactions],
                    default=0
                )
            }
        }

        logger.info(
            f"Рассчитано для инвесткопилки: {total_investment:.2f} руб. "
            f"из {len(rounded_transactions)} транзакций"
        )

        return response

    except Exception as e:
        logger.error(f"Ошибка в функции investment_bank: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'total_investment': 0.0
        }


def simple_search(
        query: str,
        transactions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Простой поиск транзакций по запросу.

    Args:
        query: Строка для поиска
        transactions: Список транзакций

    Returns:
        Словарь с результатами поиска
    """
    try:
        logger.info(f"Поиск транзакций по запросу: '{query}'")

        if not query or not query.strip():
            logger.warning("Пустой запрос поиска")
            return {
                'status': 'error',
                'error': 'Пустой поисковый запрос',
                'results': [],
                'count': 0
            }

        if not transactions:
            logger.warning("Нет данных о транзакциях")
            return {
                'status': 'error',
                'error': 'Нет данных о транзакциях',
                'results': [],
                'count': 0
            }

        search_query = query.lower().strip()
        results = []

        for transaction in transactions:
            try:
                # Ищем в описании
                description = str(transaction.get('Описание', '')).lower()
                # Ищем в категории
                category = str(transaction.get('Категория', '')).lower()

                if (search_query in description or
                        search_query in category or
                        search_query in str(transaction.get('MCC', '')).lower()):

                    # Форматируем результат
                    result_item = {
                        'date': transaction.get('Дата операции'),
                        'amount': float(transaction.get('Сумма операции', 0)),
                        'category': transaction.get('Категория', 'Неизвестно'),
                        'description': transaction.get('Описание', ''),
                        'card': transaction.get('Номер карты', ''),
                        'status': transaction.get('Статус', '')
                    }

                    # Добавляем поля совпадения
                    matches = []
                    if search_query in description:
                        matches.append('description')
                    if search_query in category:
                        matches.append('category')

                    result_item['matches'] = matches
                    results.append(result_item)

            except (ValueError, TypeError) as e:
                logger.warning(f"Ошибка обработки транзакции при поиске: {e}")
                continue

        # Сортируем по дате (новые сначала)
        results.sort(
            key=lambda x: x['date'] if x['date'] else '',
            reverse=True
        )

        response = {
            'status': 'success',
            'query': query,
            'count': len(results),
            'results': results[:50],  # Ограничиваем 50 результатами
            'search_info': {
                'search_fields': ['description', 'category', 'mcc'],
                'case_sensitive': False,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }

        logger.info(f"Найдено {len(results)} транзакций по запросу '{query}'")
        return response

    except Exception as e:
        logger.error(f"Ошибка в функции simple_search: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'results': [],
            'count': 0
        }
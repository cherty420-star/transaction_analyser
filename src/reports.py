"""
Модуль для генерации отчетов.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
import pandas as pd
from . import utils

logger = logging.getLogger(__name__)


def report_decorator(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для сохранения результатов отчета в файл.

    Args:
        filename: Имя файла для сохранения. Если None - генерируется автоматически.

    Returns:
        Декорированная функция
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            try:
                # Выполняем функцию
                result = func(*args, **kwargs)

                # Генерируем имя файла если не указано
                if filename is None:
                    report_filename = (
                        f"report_{func.__name__}_"
                        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    )
                else:
                    report_filename = filename

                # Сохраняем результат в файл
                with open(report_filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                logger.info(f"Отчет сохранен в файл: {report_filename}")

                # Добавляем информацию о файле в результат
                if isinstance(result, dict):
                    result['report_file'] = report_filename
                    result['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                return result

            except Exception as e:
                logger.error(f"Ошибка в декораторе отчета для функции {func.__name__}: {e}")
                return {
                    'status': 'error',
                    'error': str(e),
                    'function': func.__name__
                }

        return wrapper

    return decorator


@report_decorator()
def spending_by_weekday(
        df: pd.DataFrame,
        reference_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Анализ средних трат по дням недели за последние 3 месяца.

    Args:
        df: DataFrame с транзакциями
        reference_date: Опорная дата в формате 'YYYY-MM-DD'

    Returns:
        Словарь с анализом трат по дням недели
    """
    try:
        logger.info("Генерация отчета 'Траты по дням недели'")

        if df.empty:
            logger.warning("Нет данных для анализа")
            return {
                'status': 'error',
                'error': 'Нет данных для анализа',
                'spending_by_weekday': {}
            }

        # Определяем опорную дату
        if reference_date:
            ref_dt = datetime.strptime(reference_date, '%Y-%m-%d')
        else:
            ref_dt = datetime.now()

        # Вычисляем дату 3 месяца назад
        three_months_ago = ref_dt - timedelta(days=90)

        # Фильтруем данные
        mask = (df['Дата операции'] >= three_months_ago) & (df['Дата операции'] <= ref_dt)
        filtered_df = df[mask].copy()

        if filtered_df.empty:
            logger.warning(f"Нет данных за период {three_months_ago.date()} - {ref_dt.date()}")
            return {
                'status': 'error',
                'error': f'Нет данных за период {three_months_ago.date()} - {ref_dt.date()}',
                'spending_by_weekday': {}
            }

        # Оставляем только расходы (отрицательные суммы)
        expenses_df = filtered_df[filtered_df['Сумма операции'] < 0].copy()

        if expenses_df.empty:
            logger.warning("Нет данных о расходах за указанный период")
            return {
                'status': 'error',
                'error': 'Нет данных о расходах за указанный период',
                'spending_by_weekday': {}
            }

        # Добавляем день недели
        expenses_df['weekday'] = expenses_df['Дата операции'].dt.day_name()
        expenses_df['weekday_number'] = expenses_df['Дата операции'].dt.weekday
        expenses_df['abs_amount'] = expenses_df['Сумма операции'].abs()

        # Агрегируем по дням недели
        weekday_stats = []

        # Порядок дней недели
        weekday_order = [
            'Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday', 'Sunday'
        ]

        weekday_names_ru = {
            'Monday': 'Понедельник',
            'Tuesday': 'Вторник',
            'Wednesday': 'Среда',
            'Thursday': 'Четверг',
            'Friday': 'Пятница',
            'Saturday': 'Суббота',
            'Sunday': 'Воскресенье'
        }

        for weekday in weekday_order:
            weekday_df = expenses_df[expenses_df['weekday'] == weekday]

            if not weekday_df.empty:
                stats = {
                    'weekday_eng': weekday,
                    'weekday_ru': weekday_names_ru.get(weekday, weekday),
                    'weekday_number': weekday_order.index(weekday),
                    'total_spent': float(weekday_df['abs_amount'].sum()),
                    'average_spent': float(weekday_df['abs_amount'].mean()),
                    'median_spent': float(weekday_df['abs_amount'].median()),
                    'transaction_count': len(weekday_df),
                    'transactions_per_day': len(weekday_df) / max(len(weekday_df['Дата операции'].dt.date.unique()), 1)
                }
            else:
                stats = {
                    'weekday_eng': weekday,
                    'weekday_ru': weekday_names_ru.get(weekday, weekday),
                    'weekday_number': weekday_order.index(weekday),
                    'total_spent': 0.0,
                    'average_spent': 0.0,
                    'median_spent': 0.0,
                    'transaction_count': 0,
                    'transactions_per_day': 0.0
                }

            weekday_stats.append(stats)

        # Общая статистика
        total_spent = expenses_df['abs_amount'].sum()
        avg_spent = expenses_df['abs_amount'].mean()
        total_transactions = len(expenses_df)

        # Находим самый дорогой и самый дешевый день
        weekday_stats_sorted = sorted(
            [s for s in weekday_stats if s['transaction_count'] > 0],
            key=lambda x: x['average_spent'],
            reverse=True
        )

        most_expensive_day = weekday_stats_sorted[0] if weekday_stats_sorted else None
        least_expensive_day = weekday_stats_sorted[-1] if weekday_stats_sorted else None

        response = {
            'status': 'success',
            'report_type': 'spending_by_weekday',
            'period': {
                'start': three_months_ago.strftime('%Y-%m-%d'),
                'end': ref_dt.strftime('%Y-%m-%d'),
                'days': (ref_dt - three_months_ago).days
            },
            'summary': {
                'total_spent': float(total_spent),
                'average_daily_spent': float(avg_spent),
                'total_transactions': total_transactions,
                'most_expensive_day': most_expensive_day,
                'least_expensive_day': least_expensive_day
            },
            'weekday_stats': weekday_stats,
            'insights': {
                'busiest_day': max(
                    weekday_stats,
                    key=lambda x: x['transaction_count']
                ) if weekday_stats else None,
                'most_expensive_weekday': most_expensive_day,
                'total_days_analyzed': len(expenses_df['Дата операции'].dt.date.unique()),
                'average_transaction_value': float(avg_spent)
            }
        }

        logger.info(
            f"Отчет 'Траты по дням недели' сгенерирован. "
            f"Всего расходов: {total_spent:.2f} руб. за {total_transactions} транзакций"
        )

        return response

    except ValueError as e:
        logger.error(f"Ошибка формата даты: {e}")
        return {
            'status': 'error',
            'error': f'Неверный формат даты: {str(e)}',
            'expected_format': 'YYYY-MM-DD'
        }
    except Exception as e:
        logger.error(f"Ошибка при генерации отчета: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }
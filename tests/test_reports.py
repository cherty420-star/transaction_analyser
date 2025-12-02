"""
Тесты для модуля reports.py
"""
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta
from src import reports


@pytest.fixture
def sample_expenses_data():
    """Фикстура с тестовыми данными о расходах."""
    dates = pd.date_range('2023-09-01', '2023-12-01', freq='D')

    data = {
        'Дата операции': [],
        'Сумма операции': [],
        'Категория': []
    }

    # Создаем данные с разными днями недели
    for i, date in enumerate(dates[:30]):  # Только 30 дней
        data['Дата операции'].append(date)

        # Разные суммы для разных дней недели
        weekday = date.weekday()
        if weekday in [0, 1, 2, 3]:  # Пн-Чт
            amount = -500.0
        elif weekday == 4:  # Пт
            amount = -1000.0
        elif weekday == 5:  # Сб
            amount = -1500.0
        else:  # Вс
            amount = -800.0

        data['Сумма операции'].append(amount)
        data['Категория'].append('Супермаркет')

    return pd.DataFrame(data)


class TestSpendingByWeekday:
    """Тесты для функции spending_by_weekday."""

    @patch('src.reports.report_decorator')
    def test_spending_by_weekday_success(self, mock_decorator, sample_expenses_data):
        """Тест успешной генерации отчета."""
        # Мокаем декоратор чтобы он не сохранял файл
        mock_decorator.return_value = lambda func: func

        result = reports.spending_by_weekday(sample_expenses_data, '2023-12-01')

        assert result['status'] == 'success'
        assert result['report_type'] == 'spending_by_weekday'
        assert 'weekday_stats' in result
        assert len(result['weekday_stats']) == 7  # 7 дней недели

        # Проверяем что есть статистика
        assert 'summary' in result
        assert 'total_spent' in result['summary']

    def test_spending_by_weekday_empty_data(self):
        """Тест с пустыми данными."""
        empty_df = pd.DataFrame()
        result = reports.spending_by_weekday(empty_df)

        assert result['status'] == 'error'
        assert 'данных' in result['error'].lower() or 'data' in result['error'].lower()

    @patch('src.reports.report_decorator')
    def test_spending_by_weekday_with_income_only(self, mock_decorator):
        """Тест когда нет расходов (только доходы)."""
        mock_decorator.return_value = lambda func: func

        dates = pd.date_range('2023-12-01', '2023-12-10', freq='D')  # Декабрь 2023
        df = pd.DataFrame({
            'Дата операции': dates,
            'Сумма операции': [1000] * len(dates),  # Только положительные
            'Категория': ['Зарплата'] * len(dates)
        })

        result = reports.spending_by_weekday(df, '2023-12-10')  # Передаем дату декабря

        assert result['status'] == 'error'
        # Проверяем что есть сообщение об ошибке (любое)
        assert 'error' in result
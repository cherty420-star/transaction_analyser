"""
Тесты для модуля views.py
"""
import json
from unittest.mock import patch, MagicMock, mock_open
import pytest
import pandas as pd
from datetime import datetime
from src import views


@pytest.fixture
def mock_transactions():
    """Фикстура с тестовыми транзакциями."""
    df = pd.DataFrame({
        'Дата операции': pd.to_datetime(['2023-12-01', '2023-12-02', '2023-12-03',
                                        '2023-12-04', '2023-12-05', '2023-12-06',
                                        '2023-12-07', '2023-12-08', '2023-12-09', '2023-12-10']),
        'Номер карты': ['1234'] * 5 + ['5678'] * 5,
        'Сумма операции': [-1000, -2000, 5000, -1500, -800,
                          -1200, -3000, 7000, -900, -1100],
        'Сумма платежа': [-1000, -2000, 5000, -1500, -800,
                         -1200, -3000, 7000, -900, -1100],
        'Категория': ['Супермаркеты'] * 3 + ['Кафе'] * 3 + ['Транспорт'] * 4,
        'Описание': ['Покупка в магазине'] * 10,
        'Статус': ['OK'] * 10
    })
    return df


class TestGetTimeBasedGreeting:
    """Тесты для функции get_time_based_greeting."""

    @pytest.mark.parametrize('hour,expected', [
        (5, 'Доброе утро'),
        (11, 'Доброе утро'),
        (12, 'Добрый день'),
        (17, 'Добрый день'),
        (18, 'Добрый вечер'),
        (22, 'Добрый вечер'),
        (23, 'Доброй ночи'),
        (4, 'Доброй ночи'),
        (0, 'Доброй ночи'),
    ])
    def test_greeting_at_different_hours(self, hour, expected):
        """Параметризованный тест приветствий в разное время."""
        test_time = datetime(2023, 12, 15, hour, 0, 0)
        result = views.get_time_based_greeting(test_time)
        assert result == expected


class TestMainPage:
    """Тесты для функции main_page."""

    @patch('src.views.utils.load_excel_data')
    @patch('src.views.utils.filter_by_date_range')
    def test_main_page_success(self, mock_filter, mock_load, mock_transactions):
        """Тест успешного выполнения функции main_page."""
        # Настраиваем моки
        mock_load.return_value = mock_transactions
        # Возвращаем отфильтрованные данные
        filtered_data = mock_transactions[mock_transactions['Дата операции'] <= '2023-12-15']
        mock_filter.return_value = filtered_data

        # Мокаем чтение JSON файла
        mock_settings = {
            'user_currencies': ['USD'],
            'user_stocks': ['AAPL']
        }

        with patch('builtins.open', mock_open(read_data=json.dumps(mock_settings))):
            with patch('src.views.utils.get_currency_rates') as mock_currencies:
                with patch('src.views.utils.get_stock_prices') as mock_stocks:
                    # Настраиваем возвращаемые значения
                    mock_currencies.return_value = {'USD': 90.5}
                    mock_stocks.return_value = {'AAPL': 185.6}

                    # Вызываем функцию
                    result = views.main_page('2023-12-15 14:30:00')

                    # Проверяем результат
                    assert result['status'] == 'success'
                    assert 'greeting' in result['data']
                    assert isinstance(result['data']['greeting'], str)
                    assert 'cards' in result['data']
                    assert 'transactions' in result['data']

    @patch('src.views.utils.load_excel_data')
    def test_main_page_invalid_date_format(self, mock_load):
        """Тест с неверным форматом даты."""
        # Мокаем загрузку данных чтобы избежать ошибок
        mock_load.return_value = pd.DataFrame()

        result = views.main_page('invalid-date')
        # Проверяем что возвращается словарь с ошибкой
        assert isinstance(result, dict)
        # Может содержать 'status' или сразу 'error'
        if 'status' in result:
            assert result['status'] == 'error'
        else:
            # Или просто содержит 'error'
            assert 'error' in result
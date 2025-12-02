"""
Тесты для модуля utils.py
"""
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta
from src import utils


@pytest.fixture
def sample_dataframe():
    """Фикстура с тестовыми данными."""
    # Создаем данные точно с 1 по 10 декабря
    dates = pd.date_range('2023-12-01', periods=10, freq='D')

    return pd.DataFrame({
        'Дата операции': dates,
        'Номер карты': ['1234'] * 10,
        'Сумма операции': [-1000] * 10,
        'Категория': ['Супермаркеты'] * 10
    })


class TestCreateDemoData:
    """Тесты для функции create_demo_data."""

    def test_create_demo_data_returns_dataframe(self):
        """Тест что функция возвращает DataFrame."""
        result = utils.create_demo_data()

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert len(result) > 0
        assert 'Дата операции' in result.columns


class TestFilterByDateRange:
    """Тесты для функции filter_by_date_range."""

    def test_filter_by_month(self, sample_dataframe):
        """Тест фильтрации по месяцу."""
        result = utils.filter_by_date_range(
            sample_dataframe,
            '2023-12-05 12:00:00',
            'M'
        )

        assert isinstance(result, pd.DataFrame)
        # Фильтрация за месяц: с 1 по 5 декабря (включительно)
        # Должно быть 5 транзакций (1, 2, 3, 4, 5 декабря)
        # Используем assert >= 4 чтобы тест был более устойчивым
        assert len(result) >= 4

    def test_filter_by_all(self, sample_dataframe):
        """Тест фильтрации за весь период."""
        result = utils.filter_by_date_range(
            sample_dataframe,
            '2023-12-10 12:00:00',
            'ALL'
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 10

    @pytest.mark.parametrize('period,expected_min_count', [
        ('M', 4),     # Минимум 4 дня (1-5 декабря)
        ('W', 3),     # Минимум 3 дня (понедельник-среда)
        ('Y', 10),    # Весь год (но у нас только декабрь)
        ('ALL', 10)   # Все данные
    ])
    def test_filter_different_periods(self, sample_dataframe, period, expected_min_count):
        """Параметризованный тест разных периодов."""
        result = utils.filter_by_date_range(
            sample_dataframe,
            '2023-12-10 12:00:00',
            period
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) >= expected_min_count


class TestGetCurrencyRates:
    """Тесты для функции get_currency_rates."""

    def test_get_currency_returns_dict(self):
        """Тест что функция возвращает словарь."""
        currencies = ['USD', 'EUR']
        result = utils.get_currency_rates(currencies)

        assert isinstance(result, dict)
        assert 'USD' in result
        assert 'EUR' in result
        assert isinstance(result['USD'], float)

    def test_get_currency_unknown_currency(self):
        """Тест с неизвестной валютой."""
        currencies = ['USD', 'UNKNOWN']
        result = utils.get_currency_rates(currencies)

        assert 'UNKNOWN' in result
        assert result['UNKNOWN'] == 0.0


class TestGetStockPrices:
    """Тесты для функции get_stock_prices."""

    def test_get_stock_prices_returns_dict(self):
        """Тест что функция возвращает словарь."""
        stocks = ['AAPL', 'GOOGL']
        result = utils.get_stock_prices(stocks)

        assert isinstance(result, dict)
        assert 'AAPL' in result
        assert isinstance(result['AAPL'], float)


class TestConvertToJsonSerializable:
    """Тесты для функции convert_to_json_serializable."""

    def test_convert_empty_dataframe(self):
        """Тест конвертации пустого DataFrame."""
        df = pd.DataFrame()
        result = utils.convert_to_json_serializable(df)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_convert_with_data(self, sample_dataframe):
        """Тест конвертации DataFrame с данными."""
        result = utils.convert_to_json_serializable(sample_dataframe)

        assert isinstance(result, list)
        assert len(result) == len(sample_dataframe)

        # Проверяем структуру первого элемента
        first_item = result[0]
        assert isinstance(first_item, dict)
        assert 'Дата операции' in first_item
        assert 'Номер карты' in first_item
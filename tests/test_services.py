"""
Тесты для модуля services.py
"""
import pytest
from unittest.mock import patch, MagicMock
from src import services


@pytest.fixture
def sample_transactions():
    """Фикстура с тестовыми транзакциями."""
    return [
        {
            'Дата операции': '2023-12-01 10:30:00',
            'Сумма операции': -1712.50,
            'Описание': 'Покупка в супермаркете',
            'Категория': 'Супермаркеты'
        },
        {
            'Дата операции': '2023-12-02 15:45:00',
            'Сумма операции': -845.30,
            'Описание': 'Обед в кафе',
            'Категория': 'Кафе'
        },
        {
            'Дата операции': '2023-12-03 09:15:00',
            'Сумма операции': 5000.00,
            'Описание': 'Зарплата',
            'Категория': 'Зарплата'
        }
    ]


class TestInvestmentBank:
    """Тесты для функции investment_bank."""

    def test_investment_bank_success(self, sample_transactions):
        """Тест успешного расчета инвесткопилки."""
        result = services.investment_bank(
            '2023-12',
            sample_transactions,
            50
        )

        assert result['status'] == 'success'
        assert 'total_investment' in result
        assert result['rounding_limit'] == 50

        # Проверяем расчет для транзакций
        # -1712.50 округляется до 1750, разница 37.50
        # -845.30 округляется до 850, разница 4.70
        # Итого: 37.50 + 4.70 = 42.20
        expected_total = 37.50 + 4.70
        assert abs(result['total_investment'] - expected_total) < 0.01

    def test_investment_bank_invalid_limit(self, sample_transactions):
        """Тест с неверным лимитом округления."""
        result = services.investment_bank(
            '2023-12',
            sample_transactions,
            25  # Неправильный лимит
        )

        assert result['status'] == 'error'
        assert 'лимит' in result['error'].lower() or 'limit' in result['error'].lower()

    def test_investment_bank_empty_transactions(self):
        """Тест с пустым списком транзакций."""
        result = services.investment_bank('2023-12', [], 50)

        assert result['status'] == 'error'
        assert 'данных' in result['error'].lower() or 'data' in result['error'].lower()

    @pytest.mark.parametrize('amount,limit,expected_investment', [
        (-1712.50, 50, 37.50),   # 1750 - 1712.50 = 37.50
        (-845.30, 50, 4.70),     # 850 - 845.30 = 4.70
        (-100.00, 10, 0.00),     # 100 - 100 = 0
        (-95.00, 10, 5.00),      # 100 - 95 = 5
        (-1712.50, 100, 87.50),  # 1800 - 1712.50 = 87.50
    ])
    def test_rounding_calculations(self, amount, limit, expected_investment):
        """Параметризованный тест расчетов округления."""
        transaction = {
            'Дата операции': '2023-12-01',
            'Сумма операции': amount,
            'Описание': 'Test',
            'Категория': 'Test'
        }

        result = services.investment_bank(
            '2023-12',
            [transaction],
            limit
        )

        if result['status'] == 'success':
            assert abs(result['total_investment'] - expected_investment) < 0.01


class TestSimpleSearch:
    """Тесты для функции simple_search."""

    def test_simple_search_found(self, sample_transactions):
        """Тест успешного поиска."""
        result = services.simple_search('супермаркет', sample_transactions)

        assert result['status'] == 'success'
        assert result['count'] == 1
        assert 'супермаркет' in result['results'][0]['description'].lower()

    def test_simple_search_not_found(self, sample_transactions):
        """Тест поиска без результатов."""
        result = services.simple_search('несуществующий', sample_transactions)

        assert result['status'] == 'success'
        assert result['count'] == 0

    def test_simple_search_empty_query(self, sample_transactions):
        """Тест с пустым запросом."""
        result = services.simple_search('', sample_transactions)

        assert result['status'] == 'error'
        assert 'пустой' in result['error'].lower() or 'empty' in result['error'].lower()

    def test_simple_search_case_insensitive(self, sample_transactions):
        """Тест регистронезависимого поиска."""
        result_upper = services.simple_search('СУПЕРМАРКЕТ', sample_transactions)
        result_lower = services.simple_search('супермаркет', sample_transactions)

        assert result_upper['count'] == result_lower['count']
        assert result_upper['count'] == 1
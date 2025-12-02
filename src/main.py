"""
Главный модуль приложения для анализа транзакций.
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any
import pandas as pd
from src import utils, views, services, reports

logger = logging.getLogger(__name__)


def run_all_demonstrations() -> None:
    """Запуск всех демонстраций."""
    print("🚀 ЗАПУСК АНАЛИЗАТОРА ТРАНЗАКЦИЙ")
    print("="*60)

    try:
        # 1. Загружаем данные
        print("\n1. Загрузка данных...")
        df = utils.load_excel_data()
        print(f"✅ Загружено {len(df)} транзакций")
        print(f"📅 Период данных: {df['Дата операции'].min().date()} - {df['Дата операции'].max().date()}")

        # 2. Главная страница
        print("\n2. Главная страница...")
        # Используем дату из данных (декабрь 2023)
        result_date = "2023-12-15 14:30:00"
        result = views.main_page(result_date)
        if result.get('status') == 'success':
            data = result['data']
            print(f"✅ Приветствие: {data['greeting']}")
            print(f"✅ Карт: {len(data.get('cards', {}))}")
            print(f"✅ Транзакций за период: {data['transactions']['total_count']}")
            print(f"✅ Топ транзакция: {data['transactions']['top_5'][0]['amount']:.2f} руб.")
        else:
            print(f"❌ Ошибка: {result.get('error', 'Unknown error')}")

        # 3. Инвесткопилка
        print("\n3. Инвесткопилка...")
        transactions = utils.convert_to_json_serializable(df)

        # Тестируем с разными лимитами
        for limit in [10, 50, 100]:
            result = services.investment_bank("2023-12", transactions, limit)
            if result.get('status') == 'success':
                print(f"  Лимит {limit} руб.: {result['total_investment']:.2f} руб. "
                      f"({result['transactions_count']} транзакций)")
            else:
                print(f"❌ Ошибка при лимите {limit}: {result.get('error', 'Unknown error')}")

        # 4. Простой поиск
        print("\n4. Простой поиск...")
        search_queries = ['Супермаркеты', 'Кафе', 'Зарплата']
        for query in search_queries:
            result = services.simple_search(query, transactions)
            if result.get('status') == 'success':
                print(f"  '{query}': {result['count']} транзакций")
            else:
                print(f"❌ Ошибка при поиске '{query}': {result.get('error', 'Unknown error')}")

        # 5. Отчет по дням недели
        print("\n5. Отчет по дням недели...")
        # Используем дату из данных (15 декабря 2023)
        result = reports.spending_by_weekday(df, "2023-12-15")
        if result.get('status') == 'success':
            print(f"✅ Отчет создан: {result.get('report_file', 'report.json')}")
            print(f"📊 Проанализировано: {result['summary']['total_transactions']} транзакций")
            print(f"💰 Всего расходов: {result['summary']['total_spent']:.2f} руб.")

            # Показываем самый дорогой день
            if result['insights']['most_expensive_weekday']:
                day = result['insights']['most_expensive_weekday']
                print(f"💸 Самый дорогой день: {day['weekday_ru']} "
                      f"({day['average_spent']:.2f} руб.)")
        else:
            print(f"❌ Ошибка: {result.get('error', 'Unknown error')}")

        print("\n" + "="*60)
        print("✅ ВСЕ ДЕМОНСТРАЦИИ УСПЕШНО ВЫПОЛНЕНЫ")
        print("="*60)

        # Сохраняем результаты в файл
        all_results = {
            'main_page': views.main_page("2023-12-15 14:30:00"),
            'investment_bank': services.investment_bank("2023-12", transactions, 50),
            'simple_search': services.simple_search("Супермаркеты", transactions),
            'weekday_report': reports.spending_by_weekday(df, "2023-12-15"),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        with open('all_demonstrations.json', 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        print(f"📁 Полные результаты сохранены в: all_demonstrations.json")

    except Exception as e:
        logger.error(f"Ошибка при выполнении демонстраций: {e}")
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Запуск всех демонстраций
    run_all_demonstrations()
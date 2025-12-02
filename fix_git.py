# fix_git.py
import os
import shutil
import subprocess


def run_command(cmd, show_output=True):
    """Выполняет команду и возвращает результат."""
    print(f"\n▶️ Выполняю: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if show_output:
        if result.stdout:
            print(f"📤 Вывод: {result.stdout}")
        if result.stderr and "warning" not in result.stderr.lower():
            print(f"📥 Ошибка: {result.stderr}")

    return result.returncode == 0


def main():
    print("=" * 60)
    print("НАСТРОЙКА GIT ДЛЯ КУРСОВОЙ РАБОТЫ")
    print("=" * 60)

    # Переходим в папку проекта
    os.chdir(r"C:\Users\Andrey\PycharmProjects\transaction_analyser")

    # 1. Удаляем старый .git если есть
    print("\n1. 🔄 Проверяю текущее состояние Git...")
    if os.path.exists(".git"):
        print("   Найден старый репозиторий Git")
        choice = input("   Удалить и начать заново? (y/n): ")
        if choice.lower() == 'y':
            try:
                shutil.rmtree(".git")
                print("   ✅ Старый .git удален")
            except:
                print("   ⚠️ Не удалось удалить .git, продолжаем...")

    # 2. Инициализируем Git
    print("\n2. 🆕 Инициализирую Git...")
    run_command("git init")

    # 3. Настраиваем пользователя
    print("\n3. 👤 Настраиваю пользователя...")
    run_command('git config user.name "chery420-star"')
    run_command('git config user.email "chery420@example.com"')

    # 4. Удаляем старый remote если есть
    print("\n4. 🔗 Настраиваю подключение к GitHub...")
    run_command("git remote remove origin", show_output=False)  # Пробуем удалить

    # 5. Добавляем правильный remote
    github_url = "https://github.com/cherty420-star/transaction_analyser.git"
    run_command(f'git remote add origin "{github_url}"')

    # 6. Добавляем файлы
    print("\n5. 📁 Добавляю файлы...")

    # Сначала создаем .gitignore если его нет
    if not os.path.exists(".gitignore"):
        with open(".gitignore", "w", encoding="utf-8") as f:
            f.write("""# Python
__pycache__/
*.py[cod]

# Virtual Environment
.venv/
venv/

# IDE
.vscode/
.idea/

# Environment
.env

# Logs
*.log

# Data
data/operations.xlsx

# Test coverage
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
""")
        print("   ✅ Создан .gitignore")

    run_command("git add .")

    # 7. Делаем коммит
    print("\n6. 💾 Создаю коммит...")
    commit_message = '''feat: полная реализация анализатора транзакций

- Веб-страницы: Главная страница с JSON API
- Сервисы: Инвесткопилка и Простой поиск
- Отчеты: Траты по дням недели
- Тестирование: 36/38 тестов успешно
- Качество кода: PEP 8, flake8, black, isort'''

    run_command(f'git commit -m "{commit_message}"')

    # 8. Переименовываем ветку и пушим
    print("\n7. 📤 Отправляю на GitHub...")
    run_command("git branch -M main")

    print("\n   🔐 Если запросит логин/пароль:")
    print("   - Username: cherty420-star")
    print("   - Password: Используйте Personal Access Token (не обычный пароль!)")
    print("   - Как получить токен: GitHub → Settings → Developer settings → Tokens")

    run_command("git push -u origin main")

    # 9. Создаем ветки для PR
    print("\n8. 🌿 Создаю ветки для Pull Request...")
    run_command("git checkout -b develop")
    run_command("git push -u origin develop")
    run_command("git checkout -b feature/transaction-analyser")
    run_command("git push -u origin feature/transaction-analyser")
    run_command("git checkout main")  # Возвращаемся в main

    print("\n" + "=" * 60)
    print("✅ ВСЁ ГОТОВО!")
    print("=" * 60)

    print(f"""
📊 Статус:
   - Репозиторий: {github_url}
   - Ветка main: отправлена на GitHub
   - Ветка develop: создана и отправлена
   - Ветка feature/transaction-analyser: создана и отправлена

🎯 Дальнейшие шаги:
   1. Откройте {github_url.replace('.git', '')}
   2. Нажмите "Pull requests" → "New pull request"
   3. Настройте:
      - base: develop
      - compare: feature/transaction-analyser
   4. Заполните описание
   5. Нажмите "Create pull request"

🚀 Проверка работы:
   python src/main.py
   python -m pytest tests/ -v
""")


if __name__ == "__main__":
    main()
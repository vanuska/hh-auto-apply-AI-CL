#!/usr/bin/env python3
"""
Модуль для отображения меню
"""

import os
import sys
from pathlib import Path

def show_main_menu(tool):
    """Показывает главное меню"""
    
    # Очищаем экран
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("="*70)
    print("🚀 HH-AUTO-APPLY SETUP TOOL")
    print("="*70)
    print()
    print("📋 Доступные шаги:")
    print()
    print("  1. 📦 Установка всех зависимостей")
    print("  2. 🔧 Создание .env с выбором модели")
    print("  3. 🔍 Проверка доступных моделей")
    print("  4. 👤 Создание profile.md (PDF, DOCX, TXT или через LLM)")
    print("  5. ⚙️ Настройка config.yaml")
    print("  6. 📝 Настройка cover_letter_prompt.md")
    print("  7. 🔐 Авторизация на HH.ru")
    print("  8. 🧪 Тест генерации письма")
    print("  9. 🧹 Очистка базы данных")
    print("  10. 🚀 Запуск auto_apply.py")
    print("  11. 👋 Выход")
    print()
    print("-"*70)
    print("💡 Рекомендуется выполнять шаги по порядку")
    print("="*70)
    
    # Проверяем наличие файлов
    check_files_status(tool.root_dir)

def check_files_status(root_dir: Path):
    """Проверяет статус файлов"""
    
    files_status = [
        (".env", "🔑"),
        ("my/profile.md", "👤"),
        ("my/config.yaml", "⚙️"),
        ("my/cover_letter_prompt.md", "📝"),
        ("data/hh_auto_apply.sqlite3", "🗄️")
    ]
    
    print("\n📊 Статус файлов:")
    for file_path, icon in files_status:
        full_path = root_dir / file_path
        status = "✅" if full_path.exists() else "❌"
        print(f"  {icon} {file_path}: {status}")
    print()
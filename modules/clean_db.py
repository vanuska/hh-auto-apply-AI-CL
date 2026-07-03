#!/usr/bin/env python3
"""
Скрипт для очистки базы данных hh_auto_apply.sqlite3
Создает бэкап перед очисткой.
"""

import sqlite3
import shutil
from pathlib import Path
from datetime import datetime


def clean_database():
    """Очищает таблицу vacancy_runs в базе данных."""
    
    # Пути к файлам
    db_path = Path("data/hh_auto_apply.sqlite3")
    backup_dir = Path("data/backups")
    
    # Проверяем, существует ли база данных
    if not db_path.exists():
        print(f"❌ База данных не найдена: {db_path}")
        return False
    
    # Создаем папку для бэкапов
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Создаем бэкап с датой и временем
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"hh_auto_apply_{timestamp}.sqlite3"
    
    print(f"📦 Создание бэкапа: {backup_path}")
    shutil.copy2(db_path, backup_path)
    print(f"✅ Бэкап создан: {backup_path}")
    
    # Подключаемся к базе и очищаем таблицу
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем, сколько записей до очистки
        cursor.execute("SELECT COUNT(*) FROM vacancy_runs")
        count_before = cursor.fetchone()[0]
        print(f"📊 Записей до очистки: {count_before}")
        
        # Очищаем таблицу
        cursor.execute("DELETE FROM vacancy_runs")
        conn.commit()
        
        # Проверяем после очистки
        cursor.execute("SELECT COUNT(*) FROM vacancy_runs")
        count_after = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ База данных очищена! Удалено записей: {count_before - count_after}")
        print(f"📊 Записей после очистки: {count_after}")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка при очистке базы данных: {e}")
        return False


def show_stats():
    """Показывает статистику базы данных."""
    db_path = Path("data/hh_auto_apply.sqlite3")
    
    if not db_path.exists():
        print("❌ База данных не найдена")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Общее количество записей
        cursor.execute("SELECT COUNT(*) FROM vacancy_runs")
        total = cursor.fetchone()[0]
        
        # Статистика по статусам
        cursor.execute("SELECT status, COUNT(*) FROM vacancy_runs GROUP BY status")
        stats = cursor.fetchall()
        
        print("\n" + "="*50)
        print("📊 СТАТИСТИКА БАЗЫ ДАННЫХ")
        print("="*50)
        print(f"📋 Всего записей: {total}")
        print("\n📌 По статусам:")
        for status, count in stats:
            print(f"  - {status}: {count}")
        print("="*50)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка: {e}")


def main():
    """Главная функция."""
    print("\n" + "="*50)
    print("🧹 ОЧИСТКА БАЗЫ ДАННЫХ")
    print("="*50)
    
    # Показываем текущую статистику
    show_stats()
    
    # Спрашиваем подтверждение
    print("\n⚠️ ВНИМАНИЕ: Это действие удалит все записи из базы данных!")
    confirm = input("Продолжить? (Y/N): ").strip().upper()
    
    if confirm in ['Y', 'ДА']:
        print("\n🔄 Начинаем очистку...")
        if clean_database():
            print("\n✅ Очистка завершена успешно!")
            show_stats()
        else:
            print("\n❌ Очистка не удалась.")
    else:
        print("\n⏹️ Очистка отменена.")


if __name__ == "__main__":
    main()
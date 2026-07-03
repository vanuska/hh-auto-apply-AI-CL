#!/usr/bin/env python3
"""
Модуль для установки зависимостей и проверки моделей
"""

import os
import sys
import subprocess
from pathlib import Path
import importlib

def install_dependencies(root_dir: Path):
    """Устанавливает все необходимые зависимости"""
    print("\n" + "="*60)
    print("📦 ШАГ 1: УСТАНОВКА ЗАВИСИМОСТЕЙ")
    print("="*60)
    
    requirements_file = root_dir / "requirements.txt"
    if not requirements_file.exists():
        print("❌ Файл requirements.txt не найден")
        return
    
    print("📋 Устанавливаем зависимости из requirements.txt...")
    
    # Проверяем наличие pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ pip не найден. Установите pip")
        return
    
    # Устанавливаем зависимости
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            check=True
        )
        print("✅ Зависимости успешно установлены")
        
        # Устанавливаем playwright браузеры
        print("\n🌐 Устанавливаем браузеры для Playwright...")
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True
        )
        print("✅ Playwright браузеры установлены")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки: {e}")

def check_models(root_dir: Path):
    """Проверяет доступные модели через check_models.py"""
    print("\n" + "="*60)
    print("🔍 ШАГ 3: ПРОВЕРКА МОДЕЛЕЙ")
    print("="*60)
    
    check_script = root_dir / "check_models.py"
    if not check_script.exists():
        print("❌ check_models.py не найден")
        return
    
    print("📋 Проверяем доступные модели на OpenRouter...")
    
    try:
        subprocess.run(
            [sys.executable, str(check_script)],
            check=True
        )
        print("✅ Проверка моделей завершена")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при проверке моделей: {e}")
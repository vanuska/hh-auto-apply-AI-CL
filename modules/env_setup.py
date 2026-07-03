#!/usr/bin/env python3
"""
Модуль для настройки .env файла
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional

def setup_env(root_dir: Path):
    """Интерактивная настройка .env файла"""
    print("\n" + "="*60)
    print("🔧 ШАГ 2: НАСТРОЙКА .ENV")
    print("="*60)
    
    env_example = root_dir / ".env.example"
    env_file = root_dir / ".env"
    
    # Если .env уже существует, спрашиваем о перезаписи
    if env_file.exists():
        overwrite = input("⚠️ .env уже существует. Перезаписать? (Y/N): ").strip().upper()
        if overwrite not in ['Y', 'ДА']:
            print("✅ Используем существующий .env файл")
            return
    
    if not env_example.exists():
        print("❌ .env.example не найден")
        return
    
    print("\n📋 Настройка параметров:")
    
    # Читаем пример .env
    with open(env_example, 'r') as f:
        env_content = f.read()
    
    # Создаем новый .env файл
    env_lines = []
    env_lines.append("# Настройки HH.ru")
    env_lines.append(f"HH_USER_AGENT=hh-auto-apply/1.0 (your-email@example.com)")
    env_lines.append("")
    
    # Настройка LLM провайдера
    print("\n🤖 Выбор LLM провайдера:")
    print("1. OpenRouter (рекомендуется, бесплатные модели)")
    print("2. OpenAI (платные модели)")
    print("3. Anthropic (платные модели)")
    
    provider_choice = input("Выберите провайдер (1-3): ").strip()
    
    if provider_choice == "1":
        env_lines.append("# OpenRouter настройки")
        env_lines.append("LLM_PROVIDER=openrouter")
        api_key = input("Введите ваш OpenRouter API ключ (или нажмите Enter для пропуска): ").strip()
        if api_key:
            env_lines.append(f"OPENROUTER_API_KEY={api_key}")
        else:
            env_lines.append("OPENROUTER_API_KEY=your_openrouter_key")
        env_lines.append("OPENROUTER_MODEL=auto  # auto для автоматического выбора")
        
    elif provider_choice == "2":
        env_lines.append("# OpenAI настройки")
        env_lines.append("LLM_PROVIDER=openai")
        api_key = input("Введите ваш OpenAI API ключ: ").strip()
        if api_key:
            env_lines.append(f"OPENAI_API_KEY={api_key}")
        else:
            env_lines.append("OPENAI_API_KEY=your_openai_key")
        env_lines.append("OPENAI_MODEL=gpt-4o-mini")
        
    elif provider_choice == "3":
        env_lines.append("# Anthropic настройки")
        env_lines.append("LLM_PROVIDER=anthropic")
        api_key = input("Введите ваш Anthropic API ключ: ").strip()
        if api_key:
            env_lines.append(f"ANTHROPIC_API_KEY={api_key}")
        else:
            env_lines.append("ANTHROPIC_API_KEY=your_anthropic_key")
        env_lines.append("ANTHROPIC_MODEL=claude-sonnet-4-6")
    else:
        print("❌ Неверный выбор. Используем OpenRouter по умолчанию")
        env_lines.append("LLM_PROVIDER=openrouter")
        env_lines.append("OPENROUTER_API_KEY=your_openrouter_key")
        env_lines.append("OPENROUTER_MODEL=auto")
    
    env_lines.append("")
    env_lines.append("# Пути к файлам")
    env_lines.append("N8N_FILES_DIR=")
    env_lines.append("HH_CONFIG_PATH=my/config.yaml")
    env_lines.append("HH_STATE_DB=data/hh_auto_apply.sqlite3")
    
    # Записываем .env
    with open(env_file, 'w') as f:
        f.write('\n'.join(env_lines))
    
    print("✅ .env файл создан")
    
    # Загружаем .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env загружен в окружение")
    except ImportError:
        print("⚠️ python-dotenv не установлен. Установите его для работы с .env")
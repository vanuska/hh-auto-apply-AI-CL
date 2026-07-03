#!/usr/bin/env python3
"""
Модуль для настройки config.yaml и cover_letter_prompt.md
"""

import os
import sys
from pathlib import Path
import shutil

def setup_config(root_dir: Path):
    """Настраивает config.yaml"""
    print("\n" + "="*60)
    print("⚙️ ШАГ 5: НАСТРОЙКА CONFIG.YAML")
    print("="*60)
    
    my_dir = root_dir / "my"
    config_file = my_dir / "config.yaml"
    
    # Проверяем существование
    if config_file.exists():
        overwrite = input("⚠️ config.yaml уже существует. Перезаписать? (Y/N): ").strip().upper()
        if overwrite not in ['Y', 'ДА']:
            print("✅ Используем существующий config.yaml")
            return
    
    # Копируем из примера
    example_config = root_dir / "config.example.yaml"
    if example_config.exists():
        shutil.copy2(example_config, config_file)
        print(f"✅ config.yaml создан из {example_config.name}")
    else:
        print("❌ config.example.yaml не найден")
        return
    
    # Настройка параметров
    print("\n📋 Настройка параметров поиска:")
    
    # Ключевые слова
    print("\n1. Ключевые слова для поиска (через запятую):")
    print("   Например: Менеджер ИТ, Руководитель ИТ, IT Manager")
    keywords = input("Введите ключевые слова (Enter для пропуска): ").strip()
    
    # Стоп-слова
    print("\n2. Стоп-слова (исключаемые слова, через запятую):")
    print("   Например: стажер, junior, intern")
    stop_words = input("Введите стоп-слова (Enter для пропуска): ").strip()
    
    # Обязательные слова
    print("\n3. Обязательные слова в названии (через запятую):")
    print("   Например: Руководитель, Менеджер")
    required_words = input("Введите обязательные слова (Enter для пропуска): ").strip()
    
    # Город и зарплата
    print("\n4. Дополнительные вопросы работодателя:")
    city = input("   Город (например, Москва): ").strip() or "Москва"
    salary = input("   Зарплатные ожидания (например, от 270000 RUB): ").strip() or "от 270000 RUB"
    
    # Обновляем config.yaml
    if keywords or stop_words or required_words:
        update_config(config_file, keywords, stop_words, required_words, city, salary)
    
    print("✅ config.yaml настроен")

def update_config(config_file: Path, keywords: str, stop_words: str, required_words: str, city: str, salary: str):
    """Обновляет конфигурационный файл"""
    
    # Читаем текущий конфиг
    import yaml
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f) or {}
    
    # Обновляем ключевые слова
    if keywords:
        keywords_list = [k.strip() for k in keywords.split(',') if k.strip()]
        if keywords_list:
            config['vacancies']['keywords'] = keywords_list
    
    # Обновляем стоп-слова
    if stop_words:
        stop_list = [s.strip() for s in stop_words.split(',') if s.strip()]
        if stop_list:
            config['vacancies']['stop_words'] = stop_list
    
    # Обновляем обязательные слова
    if required_words:
        required_list = [r.strip() for r in required_words.split(',') if r.strip()]
        if required_list:
            config['vacancies']['required_title_words_any'] = required_list
    
    # Обновляем город и зарплату
    if 'application_questions' not in config:
        config['application_questions'] = {}
    
    if city:
        config['application_questions']['city'] = city
    
    if salary:
        config['application_questions']['salary_expectations'] = salary
        
        # Также обновляем answers если они есть
        if 'answers' in config['application_questions']:
            for answer in config['application_questions']['answers']:
                if 'salary' in ' '.join(answer.get('keywords', [])):
                    answer['answer'] = salary
    
    # Сохраняем конфиг
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    
    print("✅ Конфигурация обновлена")

def setup_letter_prompt(root_dir: Path):
    """Настраивает cover_letter_prompt.md"""
    print("\n" + "="*60)
    print("📝 ШАГ 6: НАСТРОЙКА ШАБЛОНА ПИСЬМА")
    print("="*60)
    
    my_dir = root_dir / "my"
    prompt_file = my_dir / "cover_letter_prompt.md"
    
    # Проверяем существование
    if prompt_file.exists():
        overwrite = input("⚠️ cover_letter_prompt.md уже существует. Перезаписать? (Y/N): ").strip().upper()
        if overwrite not in ['Y', 'ДА']:
            print("✅ Используем существующий cover_letter_prompt.md")
            return
    
    # Используем готовый шаблон
    template = """# КРИТИЧЕСКИ ВАЖНО: ОТВЕЧАЙ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ!

# НЕ ПИШИ НА АНГЛИЙСКОМ! НЕ ОБЪЯСНЯЙ СВОИ ДЕЙСТВИЯ!

# НЕ ПИШИ АНАЛИЗ, НЕ РАЗМЫШЛЯЙ ВСЛУХ, НЕ ПИШИ НА АНГЛИЙСКОМ.

# ВЕРНИ ТОЛЬКО ГОТОВОЕ СОПРОВОДИТЕЛЬНОЕ ПИСЬМО НА РУССКОМ!

# ПИСЬМО ДОЛЖНО БЫТЬ 3-5 ПРЕДЛОЖЕНИЙ!

Ты пишешь сопроводительные письма для hh.ru от лица кандидата.

Главная цель: письмо должно выглядеть как короткое осмысленное сообщение живого специалиста, а не как универсальный шаблон.

Стиль:
* русский язык;
* спокойно, уверенно, профессионально;
* без восторга, продажности, канцелярита и HR-штампов;
* без фраз "меня заинтересовала вакансия", "буду рад", "рассмотрите мою кандидатуру";
* без восклицательных знаков;
* не пересказывай резюме целиком.

Логика письма:
1. Начни с короткого приветствия.
2. Сразу назови 1-2 точки совпадения между вакансией и опытом кандидата.
3. Добавь конкретный релевантный опыт или результат из профиля.
4. Заверши спокойным предложением обсудить задачи команды.

Чего избегать:
* общих фраз без фактов;
* названий прошлых компаний кандидата;
* повторения названия вакансии без смысла;
* длинных перечислений всего стека;
* обещаний и опыта, которых нет в профиле.

Данные для дополнительных вопросов работодателя:
* город: Москва;
* зарплатные ожидания: от 270000 руб.
"""
    
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"✅ cover_letter_prompt.md создан")
    print("📝 Вы можете отредактировать его позже для настройки стиля писем")
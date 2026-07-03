#!/usr/bin/env python3
"""
Модуль для создания профиля кандидата из различных источников
"""

import os
import sys
from pathlib import Path
from typing import Optional
import importlib

def create_profile(root_dir: Path):
    """Создает profile.md из различных источников"""
    print("\n" + "="*60)
    print("👤 ШАГ 4: СОЗДАНИЕ ПРОФИЛЯ")
    print("="*60)
    
    my_dir = root_dir / "my"
    profile_file = my_dir / "profile.md"
    
    # Проверяем существование профиля
    if profile_file.exists():
        overwrite = input("⚠️ profile.md уже существует. Перезаписать? (Y/N): ").strip().upper()
        if overwrite not in ['Y', 'ДА']:
            print("✅ Используем существующий profile.md")
            return
    
    print("\n📋 Выберите способ создания профиля:")
    print("1. Создать вручную с помощью текстового редактора")
    print("2. Извлечь из PDF файла")
    print("3. Извлечь из DOC/DOCX файла")
    print("4. Извлечь из TXT файла")
    print("5. Сгенерировать с помощью LLM (введите данные через консоль)")
    
    choice = input("Выберите способ (1-5): ").strip()
    
    if choice == "1":
        create_manual_profile(my_dir)
    elif choice == "2":
        extract_from_pdf(my_dir)
    elif choice == "3":
        extract_from_docx(my_dir)
    elif choice == "4":
        extract_from_txt(my_dir)
    elif choice == "5":
        generate_with_llm(my_dir)
    else:
        print("❌ Неверный выбор. Создаем пустой профиль")
        create_manual_profile(my_dir)

def create_manual_profile(my_dir: Path):
    """Создает профиль вручную"""
    print("\n📝 Открываем редактор для создания profile.md")
    print("Введите данные о себе (затем нажмите Ctrl+D для сохранения):")
    
    lines = []
    try:
        while True:
            line = input()
            if line == "":
                continue
            lines.append(line)
    except EOFError:
        pass
    
    if lines:
        profile_content = "\n".join(lines)
        save_profile(my_dir, profile_content)
        print("✅ Профиль создан вручную")
    else:
        print("⚠️ Профиль не создан (пустой ввод)")

def extract_from_pdf(my_dir: Path):
    """Извлекает текст из PDF файла"""
    print("\n📄 Извлечение из PDF файла")
    
    # Ищем PDF файлы в my директории
    pdf_files = list(my_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("⚠️ PDF файлы не найдены в папке my/")
        print("Пожалуйста, скопируйте ваш PDF файл в папку my/ и попробуйте снова")
        return
    
    print("\nНайденные PDF файлы:")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"{i}. {pdf_file.name}")
    
    choice = input("Выберите файл (номер) или нажмите Enter для использования первого: ").strip()
    
    try:
        if choice:
            idx = int(choice) - 1
            pdf_path = pdf_files[idx] if 0 <= idx < len(pdf_files) else pdf_files[0]
        else:
            pdf_path = pdf_files[0]
        
        print(f"📖 Извлечение текста из: {pdf_path.name}")
        
        # Пытаемся импортировать pypdf
        try:
            from pypdf import PdfReader
        except ImportError:
            print("❌ pypdf не установлен. Установите его: pip install pypdf")
            return
        
        # Извлекаем текст
        reader = PdfReader(str(pdf_path))
        text_parts = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                text_parts.append(text)
        
        profile_content = "\n\n".join(text_parts)
        save_profile(my_dir, profile_content)
        print(f"✅ Профиль создан из {pdf_path.name}")
        print(f"📊 Извлечено {len(profile_content)} символов")
        
    except Exception as e:
        print(f"❌ Ошибка при извлечении из PDF: {e}")

def extract_from_docx(my_dir: Path):
    """Извлекает текст из DOC/DOCX файла"""
    print("\n📄 Извлечение из DOC/DOCX файла")
    
    # Ищем файлы
    doc_files = list(my_dir.glob("*.docx")) + list(my_dir.glob("*.doc"))
    
    if not doc_files:
        print("⚠️ DOC/DOCX файлы не найдены в папке my/")
        print("Пожалуйста, скопируйте ваш файл в папку my/ и попробуйте снова")
        return
    
    print("\nНайденные DOC/DOCX файлы:")
    for i, doc_file in enumerate(doc_files, 1):
        print(f"{i}. {doc_file.name}")
    
    choice = input("Выберите файл (номер) или нажмите Enter для использования первого: ").strip()
    
    try:
        if choice:
            idx = int(choice) - 1
            doc_path = doc_files[idx] if 0 <= idx < len(doc_files) else doc_files[0]
        else:
            doc_path = doc_files[0]
        
        print(f"📖 Извлечение текста из: {doc_path.name}")
        
        # Пытаемся извлечь текст из DOCX
        try:
            import docx
        except ImportError:
            print("❌ python-docx не установлен. Установите его: pip install python-docx")
            return
        
        doc = docx.Document(str(doc_path))
        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        profile_content = "\n\n".join(text_parts)
        save_profile(my_dir, profile_content)
        print(f"✅ Профиль создан из {doc_path.name}")
        print(f"📊 Извлечено {len(profile_content)} символов")
        
    except Exception as e:
        print(f"❌ Ошибка при извлечении из DOC/DOCX: {e}")

def extract_from_txt(my_dir: Path):
    """Извлекает текст из TXT файла"""
    print("\n📄 Извлечение из TXT файла")
    
    # Ищем TXT файлы
    txt_files = list(my_dir.glob("*.txt"))
    
    if not txt_files:
        print("⚠️ TXT файлы не найдены в папке my/")
        print("Пожалуйста, скопируйте ваш TXT файл в папку my/ и попробуйте снова")
        return
    
    print("\nНайденные TXT файлы:")
    for i, txt_file in enumerate(txt_files, 1):
        print(f"{i}. {txt_file.name}")
    
    choice = input("Выберите файл (номер) или нажмите Enter для использования первого: ").strip()
    
    try:
        if choice:
            idx = int(choice) - 1
            txt_path = txt_files[idx] if 0 <= idx < len(txt_files) else txt_files[0]
        else:
            txt_path = txt_files[0]
        
        profile_content = txt_path.read_text(encoding='utf-8')
        save_profile(my_dir, profile_content)
        print(f"✅ Профиль создан из {txt_path.name}")
        print(f"📊 Извлечено {len(profile_content)} символов")
        
    except Exception as e:
        print(f"❌ Ошибка при извлечении из TXT: {e}")

def generate_with_llm(my_dir: Path):
    """Генерирует профиль с помощью LLM"""
    print("\n🤖 Генерация профиля с помощью LLM")
    print("Введите информацию о себе в формате:")
    print("- Имя и контактные данные")
    print("- Ключевые навыки")
    print("- Опыт работы (компании, должности, обязанности)")
    print("- Образование")
    print("- Сертификаты")
    print("(Затем нажмите Ctrl+D для завершения ввода)")
    
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    if not lines:
        print("⚠️ Данные не введены")
        return
    
    raw_data = "\n".join(lines)
    
    # Используем LLM для форматирования
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Определяем провайдера
        provider = os.getenv("LLM_PROVIDER", "openrouter")
        
        if provider == "openrouter":
            formatted = format_with_openrouter(raw_data)
        elif provider == "openai":
            formatted = format_with_openai(raw_data)
        elif provider == "anthropic":
            formatted = format_with_anthropic(raw_data)
        else:
            print(f"⚠️ Неизвестный провайдер: {provider}")
            formatted = raw_data
        
        if formatted:
            save_profile(my_dir, formatted)
            print("✅ Профиль сгенерирован с помощью LLM")
        else:
            print("⚠️ Используем сырые данные")
            save_profile(my_dir, raw_data)
            
    except Exception as e:
        print(f"❌ Ошибка при генерации профиля: {e}")
        print("Сохраняем сырые данные")
        save_profile(my_dir, raw_data)

def format_with_openrouter(raw_data: str) -> str:
    """Форматирует данные с помощью OpenRouter"""
    try:
        from openai import OpenAI
        import os
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("⚠️ OPENROUTER_API_KEY не найден")
            return ""
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        prompt = f"""
Преобразуй следующие данные в структурированный профиль для hh.ru.
Используй формат markdown с разделами:
# Имя
Email, Telegram, LinkedIn, Телефон

## Желаемая роль
...

## Ключевые навыки
...

## Опыт работы
...

## Образование
...

Данные:
{raw_data}
"""
        
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.3
        )
        
        return response.choices[0].message.content or ""
        
    except Exception as e:
        print(f"❌ Ошибка OpenRouter: {e}")
        return ""

def format_with_openai(raw_data: str) -> str:
    """Форматирует данные с помощью OpenAI"""
    # Аналогично format_with_openrouter
    print("⚠️ Функция временно не реализована")
    return ""

def format_with_anthropic(raw_data: str) -> str:
    """Форматирует данные с помощью Anthropic"""
    print("⚠️ Функция временно не реализована")
    return ""

def save_profile(my_dir: Path, content: str):
    """Сохраняет профиль в profile.md"""
    profile_file = my_dir / "profile.md"
    
    with open(profile_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Профиль сохранен: {profile_file}")
    print(f"📊 Размер: {len(content)} символов")
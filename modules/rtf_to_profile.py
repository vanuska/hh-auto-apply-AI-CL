#!/usr/bin/env python3
"""
Конвертер RTF в profile.md
"""

import os
import re

def read_rtf(file_path):
    """Читает RTF файл и извлекает текст."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Убираем RTF команды (все, что начинается с \)
        # Простой способ: удаляем все \ и то, что после них до пробела или {
        text = re.sub(r'\\.*?[ {]', ' ', content)
        # Убираем фигурные скобки
        text = re.sub(r'[{}]', '', text)
        # Убираем лишние пробелы
        text = re.sub(r'\s+', ' ', text)
        # Разбиваем на строки
        lines = text.split('. ')
        result = '.\n'.join(lines)
        return result
    except Exception as e:
        print(f"❌ Ошибка при чтении RTF: {e}")
        return ""

def create_profile_from_rtf():
    """Создает profile.md из RTF файла."""
    
    print("="*60)
    print("📄 СОЗДАНИЕ PROFILE.MD ИЗ RTF")
    print("="*60)
    
    rtf_path = input("Путь к RTF файлу: ").strip()
    
    if not os.path.exists(rtf_path):
        print(f"❌ Файл не найден: {rtf_path}")
        return
    
    print("\n📖 Читаем RTF файл...")
    text = read_rtf(rtf_path)
    
    if not text:
        print("❌ Не удалось извлечь текст из RTF")
        return
    
    print(f"✅ Извлечено {len(text)} символов")
    
    # --- ПОКАЗЫВАЕМ ТЕКСТ ---
    print("\n" + "="*70)
    print("📄 ИЗВЛЕЧЕННЫЙ ТЕКСТ ИЗ RTF:")
    print("="*70)
    print(text)
    print("="*70)
    
    print("\n💡 Скопируйте нужные данные из текста выше и вставьте их ниже.")
    print("   Нажимайте Enter, чтобы пропустить поле.\n")
    
    # --- ЗАПРАШИВАЕМ ДАННЫЕ ---
    name = input("Имя: ").strip()
    email = input("Email: ").strip()
    phone = input("Телефон: ").strip()
    telegram = input("Telegram: ").strip()
    linkedin = input("LinkedIn: ").strip()
    
    print("\n📌 Желаемая роль (скопируйте из текста выше):")
    role = input("Желаемая роль: ").strip()
    
    print("\n📌 Ключевые навыки (скопируйте из текста выше):")
    skills = input("Ключевые навыки: ").strip()
    
    print("\n📌 Опыт работы (скопируйте из текста выше):")
    experience = input("Опыт работы: ").strip()
    
    print("\n📌 Образование (скопируйте из текста выше):")
    education = input("Образование: ").strip()
    
    print("\n📌 Языки (скопируйте из текста выше):")
    languages = input("Языки: ").strip()
    
    print("\n📌 Сертификаты (скопируйте из текста выше):")
    certs = input("Сертификаты: ").strip()
    
    # --- ФОРМИРУЕМ PROFILE.MD ---
    profile_content = f"""# {name if name else "Имя"}
Email: {email if email else ""}
Telegram: {telegram if telegram else ""}
LinkedIn: {linkedin if linkedin else ""}
Телефон: {phone if phone else ""}

## Желаемая роль
{role if role else ""}

## Ключевые навыки
{skills if skills else ""}

## Опыт работы

{experience if experience else ""}

## Образование
{education if education else ""}

## Языки
{languages if languages else ""}

## Сертификаты
{certs if certs else ""}
"""
    
    # Сохраняем
    os.makedirs("my", exist_ok=True)
    with open("my/profile.md", "w", encoding="utf-8") as f:
        f.write(profile_content)
    
    print(f"\n✅ profile.md создан в my/profile.md")
    print(f"📊 Размер файла: {len(profile_content)} символов")

if __name__ == "__main__":
    create_profile_from_rtf()
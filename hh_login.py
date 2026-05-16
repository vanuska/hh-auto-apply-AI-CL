#!/usr/bin/env python3
"""
HH.ru Авторизация
Сохраняет сессию браузера для автооткликатора
"""

import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

N8N_FILES_DIR = os.getenv("N8N_FILES_DIR") or os.path.expanduser("~/.n8n-files")
SESSION_FILE = os.path.join(N8N_FILES_DIR, "hh_session.json")

def ensure_dir():
    if not os.path.exists(N8N_FILES_DIR):
        print(f"📁 Создаю папку: {N8N_FILES_DIR}")
        os.makedirs(N8N_FILES_DIR)

def login():
    ensure_dir()
    
    print("\n" + "="*50)
    print("🔐 HH.ru Авторизация")
    print("="*50)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        page = context.new_page()
        page.goto("https://hh.ru/login")
        
        print("\n📌 Инструкция:")
        print("1. В открывшемся браузере войди в свой аккаунт HH.ru")
        print("2. Дождись загрузки личного кабинета")
        print("3. Вернись сюда и нажми Enter")
        print("\n⏳ Жду пока ты залогинишься...")
        
        input("\n✅ Нажми Enter когда залогинился...")
        
        context.storage_state(path=SESSION_FILE)
        
        print(f"\n✅ Сессия сохранена в {SESSION_FILE}")
        print("🎉 Теперь можешь запускать auto_apply.py!")
        
        browser.close()

if __name__ == "__main__":
    login()

#!/usr/bin/env python3
"""
Инструмент для настройки и управления hh-auto-apply
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Any, Optional

ROOT_DIR = Path(__file__).resolve().parent
MODULES_DIR = ROOT_DIR / "modules"
EXAMPLES_DIR = ROOT_DIR / "examples"
MY_DIR = ROOT_DIR / "my"
DATA_DIR = ROOT_DIR / "data"

CORE_SCRIPTS = [
    "auto_apply.py",
    "hh_login.py",
    "check_models.py",
    "clean_db.py",
    "test_letter.py",
    "requirements.txt",
]
CONFIG_EXAMPLE = "config.example.yaml"


class SetupTool:
    """Инструмент для настройки проекта"""

    def __init__(self):
        self.root_dir = ROOT_DIR
        self.is_linux = platform.system() == "Linux"
        self.has_gui = self._check_gui()
        self._ensure_directories()
        self._copy_missing_files()

    def _check_gui(self):
        """Проверяет наличие графического интерфейса"""
        if not self.is_linux:
            return True
        if os.environ.get("DISPLAY"):
            return True
        try:
            subprocess.run(["xdpyinfo"], capture_output=True, check=True)
            return True
        except:
            return False

    def _ensure_directories(self):
        for d in [MY_DIR, DATA_DIR]:
            d.mkdir(exist_ok=True, parents=True)
            print(f"Проверена/создана директория: {d}")

    def _copy_missing_files(self):
        for fname in CORE_SCRIPTS:
            src = MODULES_DIR / fname
            dst = self.root_dir / fname
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)
                print(f"Скопирован {fname} из modules в корень")
        src = EXAMPLES_DIR / CONFIG_EXAMPLE
        dst = self.root_dir / CONFIG_EXAMPLE
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            print(f"Скопирован {CONFIG_EXAMPLE} из examples в корень")

    def show_menu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 70)
        print("HH-AUTO-APPLY SETUP TOOL")
        print("=" * 70)
        print()
        print("Доступные шаги:")
        print()
        print("  1. Начальная установка (обязательно)")
        print("  2. Выбор AI-модели")
        print("  3. Проверка доступных AI-моделей")
        print("  4. Создание файла резюме")
        print("  5. Настройка конфигурации запросов")
        print("  6. Настройка промта сопроводительного письма")
        print("  7. Авторизация на HH.ru")
        print("  8. Тест генерации сопроводительного письма")
        print("  9. Работа с базой данных")
        print("  10. Поиск работы")
        print("  11. Выход")
        print()
        print("-" * 70)
        print("Рекомендуется выполнять шаги по порядку")
        print("=" * 70)
        self._check_files_status()
        print(f"\nОС: {'Linux' if self.is_linux else 'Windows/Mac'}")
        print(f"Графический интерфейс: {'Есть' if self.has_gui else 'Отсутствует (сервер)'}")
        if self.is_linux and not self.has_gui:
            print("Будет использован xvfb-run для видимого режима браузера")
        print()

    def _check_files_status(self):
        files_status = [
            (".env", "[ENV]"),
            ("my/profile.md", "[PROF]"),
            ("my/config.yaml", "[CONF]"),
            ("my/cover_letter_prompt.md", "[PROMPT]"),
            ("data/hh_auto_apply.sqlite3", "[DB]"),
        ]
        print("\nСтатус файлов:")
        for path, label in files_status:
            full = self.root_dir / path
            status = "OK" if full.exists() else "MISSING"
            print(f"  {label} {path}: {status}")
        print()

    def run_step(self, step_number: int):
        steps = {
            1: self._step_install_deps,
            2: self._step_setup_env,
            3: self._step_check_models,
            4: self._step_create_profile,
            5: self._step_setup_config,
            6: self._step_setup_prompt,
            7: self._step_hh_login,
            8: self._step_test_letter,
            9: self._step_clean_db,
            10: self._step_run_apply,
            11: self._exit,
        }
        if step_number in steps:
            try:
                steps[step_number]()
                input("\nНажмите Enter для продолжения...")
            except Exception as e:
                print(f"\nОшибка при выполнении шага {step_number}: {e}")
                input("\nНажмите Enter для продолжения...")
        else:
            print("Неверный номер шага")
            input("\nНажмите Enter для продолжения...")

    # ---------- ШАГ 1 ----------
    def _step_install_deps(self):
        print("\n" + "=" * 60)
        print("ШАГ 1: НАЧАЛЬНАЯ УСТАНОВКА")
        print("=" * 60)

        if self.is_linux:
            print("\nОбнаружена система Linux. Установка системных зависимостей...")
            self._install_system_deps()

        req_file = self.root_dir / "requirements.txt"
        if not req_file.exists():
            print("Файл requirements.txt не найден в корне. Проверьте modules.")
            return

        print("\nУстановка Python-зависимостей из requirements.txt...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
                check=True,
            )
            print("Python-зависимости установлены")
            print("  - ruamel.yaml установлен для сохранения форматирования конфига")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка установки Python-пакетов: {e}")
            return

        print("\nУстановка браузеров Playwright...")
        try:
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                check=True,
            )
            print("Playwright браузеры установлены")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка установки Playwright: {e}")

        if self.is_linux:
            print("\nУстановка системных зависимостей для Playwright...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "playwright", "install-deps", "chromium"],
                    check=True,
                )
                print("Системные зависимости Playwright установлены")
            except subprocess.CalledProcessError as e:
                print(f"Ошибка установки зависимостей Playwright: {e}")
                self._install_playwright_deps_manual()

        if self.is_linux and not self.has_gui:
            print("\nОбнаружена система Linux без графического интерфейса.")
            self._ensure_xvfb()

        print("\nНачальная установка завершена!")

    def _install_system_deps(self):
        deps = [
            "libnspr4", "libnss3", "libx11-6", "libx11-xcb1", "libxcb1",
            "libxcomposite1", "libxcursor1", "libxdamage1", "libxext6",
            "libxfixes3", "libxi6", "libxrandr2", "libxrender1", "libxss1",
            "libxtst6", "libgbm1", "libasound2", "libpango-1.0-0", "libcairo2",
            "libatk1.0-0", "libatk-bridge2.0-0", "libgtk-3-0", "libdrm2",
            "libxshmfence1", "fonts-liberation", "libappindicator3-1",
            "libnss3-tools", "xdg-utils",
        ]
        print("Установка системных пакетов (может потребоваться sudo):")
        try:
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(
                ["sudo", "apt", "install", "-y"] + deps,
                check=True,
            )
            print("Системные пакеты установлены")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка установки системных пакетов: {e}")

    def _install_playwright_deps_manual(self):
        try:
            subprocess.run(
                ["sudo", "apt", "install", "-y",
                 "libnspr4", "libnss3", "libx11-6", "libx11-xcb1",
                 "libxcb1", "libxcomposite1", "libxcursor1", "libxdamage1",
                 "libxext6", "libxfixes3", "libxi6", "libxrandr2",
                 "libxrender1", "libxss1", "libxtst6", "libgbm1",
                 "libasound2", "libpango-1.0-0", "libcairo2", "libatk1.0-0",
                 "libatk-bridge2.0-0", "libgtk-3-0", "libdrm2", "libxshmfence1"],
                check=True,
            )
            print("Системные зависимости установлены вручную")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка ручной установки: {e}")

    def _ensure_xvfb(self):
        try:
            subprocess.run(["which", "xvfb-run"], capture_output=True, check=True)
            print("xvfb-run уже установлен")
            return
        except:
            pass
        print("Установка xvfb для виртуального дисплея...")
        try:
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "xvfb"], check=True)
            print("xvfb успешно установлен")
        except subprocess.CalledProcessError as e:
            print(f"Не удалось установить xvfb: {e}")

    # ---------- ШАГ 2 ----------
    def _step_setup_env(self):
        print("\n" + "=" * 60)
        print("ШАГ 2: ВЫБОР AI-МОДЕЛИ")
        print("=" * 60)
        env_file = self.root_dir / ".env"
        if env_file.exists():
            overwrite = input(".env уже существует. Перезаписать? (Y/N): ").strip().upper()
            if overwrite not in ["Y", "ДА"]:
                print("Используем существующий .env")
                return
        
        email = input("\nВведите ваш email для HH_USER_AGENT: ").strip()
        if not email:
            email = "your-email@example.com"
            print(f"Используем заглушку: {email}")
        
        print("\nВыбор LLM провайдера:")
        print("1. OpenRouter (рекомендуется, бесплатные модели)")
        print("2. OpenAI (платные модели)")
        print("3. Anthropic (платные модели)")
        print("4. Пропустить (буду использовать позже)")
        
        provider_choice = input("Выберите (1-4): ").strip()
        
        lines = []
        lines.append("# HH.ru настройки")
        lines.append(f"HH_USER_AGENT=hh-auto-apply/1.0 ({email})")
        lines.append("")
        
        if provider_choice == "1":
            lines.append("# OpenRouter настройки")
            lines.append("LLM_PROVIDER=openrouter")
            api_key = input("Введите ваш OpenRouter API ключ (или Enter для пропуска): ").strip()
            if api_key:
                lines.append(f"OPENROUTER_API_KEY={api_key}")
            else:
                lines.append("OPENROUTER_API_KEY=none")
            print("\nВыбор модели OpenRouter:")
            print("1. auto (автоматический выбор, рекомендуется)")
            print("2. openrouter/free (бесплатная)")
            print("3. openai/gpt-4o-mini")
            print("4. anthropic/claude-3.5-sonnet")
            print("5. Своя модель")
            model_choice = input("Выберите (1-5): ").strip()
            if model_choice == "1":
                model = "auto"
            elif model_choice == "2":
                model = "openrouter/free"
            elif model_choice == "3":
                model = "openai/gpt-4o-mini"
            elif model_choice == "4":
                model = "anthropic/claude-3.5-sonnet"
            elif model_choice == "5":
                custom = input("Введите название модели: ").strip()
                model = custom if custom else "auto"
            else:
                model = "auto"
            lines.append(f"OPENROUTER_MODEL={model}")
            print(f"Выбрана модель: {model}")
            
        elif provider_choice == "2":
            lines.append("# OpenAI настройки")
            lines.append("LLM_PROVIDER=openai")
            api_key = input("Введите ваш OpenAI API ключ (или Enter для пропуска): ").strip()
            if api_key:
                lines.append(f"OPENAI_API_KEY={api_key}")
            else:
                lines.append("OPENAI_API_KEY=none")
            lines.append("OPENAI_MODEL=gpt-4o-mini")
            
        elif provider_choice == "3":
            lines.append("# Anthropic настройки")
            lines.append("LLM_PROVIDER=anthropic")
            api_key = input("Введите ваш Anthropic API ключ (или Enter для пропуска): ").strip()
            if api_key:
                lines.append(f"ANTHROPIC_API_KEY={api_key}")
            else:
                lines.append("ANTHROPIC_API_KEY=none")
            lines.append("ANTHROPIC_MODEL=claude-sonnet-4-6")
            
        elif provider_choice == "4":
            print("Пропускаем настройку AI-модели")
            lines.append("# LLM провайдер не выбран")
            lines.append("LLM_PROVIDER=none")
            lines.append("OPENROUTER_API_KEY=none")
            lines.append("OPENROUTER_MODEL=none")
            
        else:
            print("Неверный выбор. Используем OpenRouter с auto")
            lines.append("LLM_PROVIDER=openrouter")
            lines.append("OPENROUTER_API_KEY=none")
            lines.append("OPENROUTER_MODEL=auto")
        
        lines.append("")
        lines.append("# Пути к файлам")
        lines.append("N8N_FILES_DIR=")
        lines.append("HH_CONFIG_PATH=my/config.yaml")
        lines.append("HH_STATE_DB=data/hh_auto_apply.sqlite3")
        
        try:
            env_file.write_text("\n".join(lines), encoding="utf-8")
            print(".env файл создан в кодировке UTF-8")
            print("\nЕсли вы пропустили ввод API ключа, отредактируйте файл .env позже")
        except Exception as e:
            print(f"Ошибка записи: {e}, пробуем с BOM")
            env_file.write_text("\n".join(lines), encoding="utf-8-sig")
            print(".env файл создан с BOM")

    # ---------- ШАГ 3 ----------
    def _step_check_models(self):
        print("\n" + "=" * 60)
        print("ШАГ 3: ПРОВЕРКА ДОСТУПНЫХ AI-МОДЕЛЕЙ")
        print("=" * 60)
        self._run_script("check_models.py")

    # ---------- ШАГ 4 ----------
    def _step_create_profile(self):
        print("\n" + "=" * 60)
        print("ШАГ 4: СОЗДАНИЕ ФАЙЛА РЕЗЮМЕ")
        print("=" * 60)
        
        profile_file = MY_DIR / "profile.md"
        
        if profile_file.exists():
            overwrite = input("profile.md уже существует. Перезаписать? (Y/N): ").strip().upper()
            if overwrite not in ["Y", "ДА"]:
                print("Используем существующий profile.md")
                return
        
        print("\nВыберите способ создания профиля:")
        print("1. Вручную (ввод в консоли)")
        print("2. Извлечь из PDF файла")
        print("3. Извлечь из DOC/DOCX файла")
        print("4. Извлечь из TXT файла")
        print("5. Сгенерировать с помощью LLM (требуется API ключ)")
        
        choice = input("Выберите способ (1-5): ").strip()
        
        if choice == "1":
            self._create_manual_profile()
        elif choice == "2":
            self._extract_from_pdf_with_dialog()
        elif choice == "3":
            self._extract_from_docx_with_dialog()
        elif choice == "4":
            self._extract_from_txt_with_dialog()
        elif choice == "5":
            self._generate_with_llm()
        else:
            print("Неверный выбор. Создаём вручную.")
            self._create_manual_profile()

    def _create_manual_profile(self):
        print("\nВведите данные о себе (затем Ctrl+D для сохранения):")
        print("Пример формата:")
        print("# Имя Фамилия")
        print("Email: example@mail.ru")
        print("Telegram: @username")
        print("## Опыт работы")
        print("Компания, должность, период...")
        print("## Ключевые навыки")
        print("- Навык 1")
        print("- Навык 2")
        print("\nНачинайте ввод:")
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        if lines and any(l.strip() for l in lines):
            content = "\n".join(lines)
            (MY_DIR / "profile.md").write_text(content, encoding="utf-8")
            print(f"Профиль сохранён в my/profile.md ({len(content)} символов)")
        else:
            print("Пустой ввод, профиль не создан")

    def _extract_from_pdf_with_dialog(self):
        print("\n" + "=" * 60)
        print("ИЗВЛЕЧЕНИЕ ИЗ PDF")
        print("=" * 60)
        
        pdf_files = list(MY_DIR.glob("*.pdf"))
        
        print("\nОткуда взять PDF файл?")
        print("1. Из папки my/ (уже скопированы)")
        print("2. Указать путь к файлу вручную")
        print("3. Скопировать из домашней папки")
        
        source_choice = input("Выберите (1-3): ").strip()
        pdf_path = None
        
        if source_choice == "1":
            if not pdf_files:
                print("В папке my/ нет PDF файлов.")
                print("Скопируйте PDF в папку my/ и попробуйте снова")
                return
            
            print("\nНайденные PDF файлы:")
            for i, f in enumerate(pdf_files, 1):
                size = f.stat().st_size / 1024
                print(f"  {i}. {f.name} ({size:.1f} КБ)")
            
            choice = input("Выберите номер файла (или Enter для первого): ").strip()
            
            try:
                if choice:
                    idx = int(choice) - 1
                    pdf_path = pdf_files[idx] if 0 <= idx < len(pdf_files) else pdf_files[0]
                else:
                    pdf_path = pdf_files[0]
            except (ValueError, IndexError):
                pdf_path = pdf_files[0]
        
        elif source_choice == "2":
            file_path = input("Введите полный путь к PDF файлу: ").strip()
            if not file_path:
                print("Путь не указан")
                return
            
            pdf_path = Path(file_path)
            if not pdf_path.exists():
                print(f"Файл не найден: {pdf_path}")
                return
            
            import shutil
            dest = MY_DIR / pdf_path.name
            shutil.copy2(pdf_path, dest)
            print(f"Файл скопирован в {dest}")
            pdf_path = dest
        
        elif source_choice == "3":
            home = Path.home()
            print(f"\nПоиск PDF в домашней папке: {home}")
            
            home_pdfs = list(home.glob("*.pdf"))
            
            if not home_pdfs:
                print("PDF файлы не найдены в домашней папке")
                return
            
            print("\nНайденные PDF в домашней папке:")
            for i, f in enumerate(home_pdfs[:10], 1):
                size = f.stat().st_size / 1024
                print(f"  {i}. {f.name} ({size:.1f} КБ)")
            
            if len(home_pdfs) > 10:
                print(f"  ... и еще {len(home_pdfs) - 10} файлов")
            
            choice = input("Выберите номер файла: ").strip()
            
            try:
                idx = int(choice) - 1
                pdf_path = home_pdfs[idx] if 0 <= idx < len(home_pdfs) else None
                if not pdf_path:
                    print("Неверный выбор")
                    return
            except ValueError:
                print("Неверный ввод")
                return
            
            import shutil
            dest = MY_DIR / pdf_path.name
            shutil.copy2(pdf_path, dest)
            print(f"Файл скопирован в {dest}")
            pdf_path = dest
        
        else:
            print("Неверный выбор")
            return
        
        if pdf_path and pdf_path.exists():
            self._extract_pdf_text(pdf_path)

    def _extract_pdf_text(self, pdf_path: Path):
        try:
            from pypdf import PdfReader
        except ImportError:
            print("pypdf не установлен. Установите: pip install pypdf")
            return
        
        print(f"\nИзвлечение текста из: {pdf_path.name}")
        
        try:
            reader = PdfReader(str(pdf_path))
            text_parts = []
            
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text() or ""
                if text.strip():
                    text_parts.append(f"--- Страница {page_num} ---\n{text}")
                    print(f"  Страница {page_num}: {len(text)} символов")
            
            if not text_parts:
                print("Не удалось извлечь текст из PDF")
                return
            
            content = "\n\n".join(text_parts)
            
            profile_file = MY_DIR / "profile.md"
            profile_file.write_text(content, encoding="utf-8")
            
            print(f"\nПрофиль создан из {pdf_path.name}")
            print(f"Размер: {len(content)} символов")
            print(f"Сохранен: {profile_file}")
            
        except Exception as e:
            print(f"Ошибка при извлечении из PDF: {e}")

    def _extract_from_docx_with_dialog(self):
        print("\n" + "=" * 60)
        print("ИЗВЛЕЧЕНИЕ ИЗ DOC/DOCX")
        print("=" * 60)
        
        doc_files = list(MY_DIR.glob("*.docx")) + list(MY_DIR.glob("*.doc"))
        
        print("\nОткуда взять DOC/DOCX файл?")
        print("1. Из папки my/ (уже скопированы)")
        print("2. Указать путь к файлу вручную")
        print("3. Скопировать из домашней папки")
        
        source_choice = input("Выберите (1-3): ").strip()
        doc_path = None
        
        if source_choice == "1":
            if not doc_files:
                print("В папке my/ нет DOC/DOCX файлов")
                return
            
            print("\nНайденные DOC/DOCX файлы:")
            for i, f in enumerate(doc_files, 1):
                size = f.stat().st_size / 1024
                print(f"  {i}. {f.name} ({size:.1f} КБ)")
            
            choice = input("Выберите номер файла (или Enter для первого): ").strip()
            
            try:
                if choice:
                    idx = int(choice) - 1
                    doc_path = doc_files[idx] if 0 <= idx < len(doc_files) else doc_files[0]
                else:
                    doc_path = doc_files[0]
            except (ValueError, IndexError):
                doc_path = doc_files[0]
        
        elif source_choice == "2":
            file_path = input("Введите полный путь к DOC/DOCX файлу: ").strip()
            if not file_path:
                print("Путь не указан")
                return
            
            doc_path = Path(file_path)
            if not doc_path.exists():
                print(f"Файл не найден: {doc_path}")
                return
            
            import shutil
            dest = MY_DIR / doc_path.name
            shutil.copy2(doc_path, dest)
            print(f"Файл скопирован в {dest}")
            doc_path = dest
        
        elif source_choice == "3":
            home = Path.home()
            print(f"\nПоиск DOC/DOCX в домашней папке: {home}")
            
            home_docs = list(home.glob("*.docx")) + list(home.glob("*.doc"))
            
            if not home_docs:
                print("DOC/DOCX файлы не найдены в домашней папке")
                return
            
            print("\nНайденные DOC/DOCX в домашней папке:")
            for i, f in enumerate(home_docs[:10], 1):
                size = f.stat().st_size / 1024
                print(f"  {i}. {f.name} ({size:.1f} КБ)")
            
            choice = input("Выберите номер файла: ").strip()
            
            try:
                idx = int(choice) - 1
                doc_path = home_docs[idx] if 0 <= idx < len(home_docs) else None
                if not doc_path:
                    print("Неверный выбор")
                    return
            except ValueError:
                print("Неверный ввод")
                return
            
            import shutil
            dest = MY_DIR / doc_path.name
            shutil.copy2(doc_path, dest)
            print(f"Файл скопирован в {dest}")
            doc_path = dest
        
        else:
            print("Неверный выбор")
            return
        
        if doc_path and doc_path.exists():
            self._extract_docx_text(doc_path)

    def _extract_docx_text(self, doc_path: Path):
        if doc_path.suffix.lower() == '.doc':
            print(f"\nФайл {doc_path.name} имеет старый формат .doc")
            print("Рекомендации:")
            print("  1. Откройте файл в Microsoft Word и сохраните как .docx")
            print("  2. Или сохраните как .txt и используйте способ 4")
            return
        
        try:
            import docx
        except ImportError:
            print("python-docx не установлен. Установите: pip install python-docx")
            return
        
        print(f"\nИзвлечение текста из: {doc_path.name}")
        
        try:
            doc = docx.Document(str(doc_path))
            text_parts = [p.text for p in doc.paragraphs if p.text.strip()]
            
            if not text_parts:
                print("Не удалось извлечь текст (пустой результат)")
                return
            
            content = "\n\n".join(text_parts)
            
            profile_file = MY_DIR / "profile.md"
            profile_file.write_text(content, encoding="utf-8")
            
            print(f"\nПрофиль создан из {doc_path.name}")
            print(f"Размер: {len(content)} символов")
            print(f"Сохранен: {profile_file}")
            
        except Exception as e:
            print(f"Не удалось открыть файл: {e}")

    def _extract_from_txt_with_dialog(self):
        print("\n" + "=" * 60)
        print("ИЗВЛЕЧЕНИЕ ИЗ TXT")
        print("=" * 60)
        
        txt_files = list(MY_DIR.glob("*.txt"))
        
        print("\nОткуда взять TXT файл?")
        print("1. Из папки my/ (уже скопированы)")
        print("2. Указать путь к файлу вручную")
        print("3. Скопировать из домашней папки")
        
        source_choice = input("Выберите (1-3): ").strip()
        txt_path = None
        
        if source_choice == "1":
            if not txt_files:
                print("В папке my/ нет TXT файлов")
                return
            
            print("\nНайденные TXT файлы:")
            for i, f in enumerate(txt_files, 1):
                size = f.stat().st_size / 1024
                print(f"  {i}. {f.name} ({size:.1f} КБ)")
            
            choice = input("Выберите номер файла (или Enter для первого): ").strip()
            
            try:
                if choice:
                    idx = int(choice) - 1
                    txt_path = txt_files[idx] if 0 <= idx < len(txt_files) else txt_files[0]
                else:
                    txt_path = txt_files[0]
            except (ValueError, IndexError):
                txt_path = txt_files[0]
        
        elif source_choice == "2":
            file_path = input("Введите полный путь к TXT файлу: ").strip()
            if not file_path:
                print("Путь не указан")
                return
            
            txt_path = Path(file_path)
            if not txt_path.exists():
                print(f"Файл не найден: {txt_path}")
                return
            
            import shutil
            dest = MY_DIR / txt_path.name
            shutil.copy2(txt_path, dest)
            print(f"Файл скопирован в {dest}")
            txt_path = dest
        
        elif source_choice == "3":
            home = Path.home()
            print(f"\nПоиск TXT в домашней папке: {home}")
            
            home_txts = list(home.glob("*.txt"))
            
            if not home_txts:
                print("TXT файлы не найдены в домашней папке")
                return
            
            print("\nНайденные TXT в домашней папке:")
            for i, f in enumerate(home_txts[:10], 1):
                size = f.stat().st_size / 1024
                print(f"  {i}. {f.name} ({size:.1f} КБ)")
            
            choice = input("Выберите номер файла: ").strip()
            
            try:
                idx = int(choice) - 1
                txt_path = home_txts[idx] if 0 <= idx < len(home_txts) else None
                if not txt_path:
                    print("Неверный выбор")
                    return
            except ValueError:
                print("Неверный ввод")
                return
            
            import shutil
            dest = MY_DIR / txt_path.name
            shutil.copy2(txt_path, dest)
            print(f"Файл скопирован в {dest}")
            txt_path = dest
        
        else:
            print("Неверный выбор")
            return
        
        if txt_path and txt_path.exists():
            try:
                content = txt_path.read_text(encoding="utf-8", errors="ignore")
                
                if content.strip():
                    profile_file = MY_DIR / "profile.md"
                    profile_file.write_text(content, encoding="utf-8")
                    
                    print(f"\nПрофиль создан из {txt_path.name}")
                    print(f"Размер: {len(content)} символов")
                    print(f"Сохранен: {profile_file}")
                else:
                    print("Файл пуст")
                    
            except Exception as e:
                print(f"Ошибка при чтении файла: {e}")

    def _generate_with_llm(self):
        print("\n" + "=" * 60)
        print("ГЕНЕРАЦИЯ ПРОФИЛЯ С ПОМОЩЬЮ LLM")
        print("=" * 60)
        
        try:
            from dotenv import load_dotenv
            load_dotenv()
            provider = os.getenv("LLM_PROVIDER", "openrouter")
            model = os.getenv("OPENROUTER_MODEL", "openrouter/free")
            if model == "auto":
                model = "openrouter/free"
            print(f"Провайдер: {provider}")
            print(f"Модель: {model}")
            print()
        except:
            pass
        
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
        
        if not lines or not any(line.strip() for line in lines):
            print("Данные не введены")
            return
        
        raw_data = "\n".join(lines)
        
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            provider = os.getenv("LLM_PROVIDER", "openrouter")
            
            if provider == "openrouter":
                formatted = self._format_with_openrouter(raw_data)
            elif provider == "openai":
                formatted = self._format_with_openai(raw_data)
            elif provider == "anthropic":
                formatted = self._format_with_anthropic(raw_data)
            else:
                print(f"Неизвестный провайдер: {provider}")
                formatted = raw_data
            
            if formatted:
                (MY_DIR / "profile.md").write_text(formatted, encoding="utf-8")
                print("\nПрофиль сгенерирован с помощью LLM")
                print(f"Размер: {len(formatted)} символов")
            else:
                print("Используем сырые данные")
                (MY_DIR / "profile.md").write_text(raw_data, encoding="utf-8")
                
        except Exception as e:
            print(f"Ошибка при генерации профиля: {e}")
            print("Сохраняем сырые данные")
            (MY_DIR / "profile.md").write_text(raw_data, encoding="utf-8")

    def _format_with_openrouter(self, raw_data: str) -> str:
        try:
            from openai import OpenAI
            import os
            
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key or api_key == "none":
                print("OPENROUTER_API_KEY не найден или равен none")
                print("Пожалуйста, укажите API ключ в файле .env")
                return ""
            
            model = os.getenv("OPENROUTER_MODEL", "openrouter/free")
            if model == "auto":
                model = "openrouter/free"
                print(f"Используем модель по умолчанию: {model}")
            else:
                print(f"Используем модель из .env: {model}")
            
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
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            
            return response.choices[0].message.content or ""
            
        except Exception as e:
            print(f"Ошибка OpenRouter: {e}")
            return ""

    def _format_with_openai(self, raw_data: str) -> str:
        print("Функция временно не реализована")
        return ""

    def _format_with_anthropic(self, raw_data: str) -> str:
        print("Функция временно не реализована")
        return ""

    # ---------- ШАГ 5 ----------
    def _step_setup_config(self):
        print("\n" + "=" * 60)
        print("ШАГ 5: НАСТРОЙКА КОНФИГУРАЦИИ ЗАПРОСОВ")
        print("=" * 60)
        config_file = MY_DIR / "config.yaml"
        if config_file.exists():
            overwrite = input("config.yaml уже существует. Перезаписать? (Y/N): ").strip().upper()
            if overwrite not in ["Y", "ДА"]:
                print("Используем существующий config.yaml")
                return

        src = self.root_dir / CONFIG_EXAMPLE
        if not src.exists():
            src = EXAMPLES_DIR / CONFIG_EXAMPLE
        if src.exists():
            shutil.copy2(src, config_file)
            print(f"config.yaml создан из {src.name}")
        else:
            base = """vacancies:
  keywords:
    - Менеджер ИТ
    - Руководитель ИТ
  required_title_words_any:
    - Руководитель
    - Менеджер
  stop_words:
    - стажер
    - junior
  remote_only: false
  skip_already_applied: true

search:
  area: 113
  per_page: 20
  max_pages: 1
  title_only: true

limits:
  max_applications_per_run: 5
  delay_between_applications_seconds: 20

application_questions:
  city: "Москва"
  salary_expectations: "от 270000 RUB"

letter:
  language: ru
  max_chars: 1200
  portfolio_url: ""
  prompt_path: my/cover_letter_prompt.md

schedule:
  run_times:
    - "09:30"
    - "18:30"
"""
            config_file.write_text(base, encoding="utf-8")
            print("config.yaml создан (базовый)")

        self._update_config_interactive(config_file)

    def _update_config_interactive(self, config_file: Path):
        import yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f) or {}

        print("\nДополнительная настройка (можно пропустить Enter):")
        print("Введите новые значения или нажмите Enter для пропуска")

        keywords = input("Ключевые слова для поиска (через запятую): ").strip()
        if keywords:
            cfg["vacancies"]["keywords"] = [k.strip() for k in keywords.split(",") if k.strip()]
            print("Ключевые слова обновлены")

        city = input("Город: ").strip()
        if city:
            if "application_questions" not in cfg:
                cfg["application_questions"] = {}
            cfg["application_questions"]["city"] = city
            print("Город обновлён")

        salary = input("Зарплатные ожидания: ").strip()
        if salary:
            if "application_questions" not in cfg:
                cfg["application_questions"] = {}
            cfg["application_questions"]["salary_expectations"] = salary
            print("Зарплата обновлена")

        limit = input("Максимум откликов за запуск: ").strip()
        if limit:
            try:
                if "limits" not in cfg:
                    cfg["limits"] = {}
                cfg["limits"]["max_applications_per_run"] = int(limit)
                print("Лимит обновлён")
            except ValueError:
                print("Неверное число, пропускаем")

        schedule = input("Расписание (через запятую, например: 09:30, 18:30): ").strip()
        if schedule:
            times = [t.strip() for t in schedule.split(",") if t.strip()]
            if times:
                if "schedule" not in cfg:
                    cfg["schedule"] = {}
                cfg["schedule"]["run_times"] = times
                print("Расписание обновлено")

        self._save_yaml_preserve_format(config_file, cfg)

    def _save_yaml_preserve_format(self, file_path: Path, data: Dict[str, Any]):
        try:
            from ruamel.yaml import YAML
            yaml_ruamel = YAML()
            yaml_ruamel.preserve_quotes = True
            yaml_ruamel.indent(mapping=2, sequence=4, offset=2)
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml_ruamel.dump(data, f)
            print("Конфиг сохранён с сохранением форматирования")
        except ImportError:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            print("Конфиг сохранён (стандартный YAML)")
            print("Для сохранения комментариев установите: pip install ruamel.yaml")

    # ---------- ШАГ 6 ----------
    def _step_setup_prompt(self):
        print("\n" + "=" * 60)
        print("ШАГ 6: НАСТРОЙКА ПРОМТА СОПРОВОДИТЕЛЬНОГО ПИСЬМА")
        print("=" * 60)
        prompt_file = MY_DIR / "cover_letter_prompt.md"
        if prompt_file.exists():
            overwrite = input("Файл уже существует. Перезаписать? (Y/N): ").strip().upper()
            if overwrite not in ["Y", "ДА"]:
                print("Используем существующий")
                return
        template = """# ВАЖНО: ОТВЕЧАЙ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ
# ВЕРНИ ТОЛЬКО ГОТОВОЕ ПИСЬМО, 3-5 ПРЕДЛОЖЕНИЙ

Ты пишешь сопроводительные письма для hh.ru от лица кандидата.

Стиль: профессионально, спокойно, без штампов.
Без фраз "меня заинтересовала", "буду рад", "рассмотрите".
Без восклицательных знаков.

Логика письма:
1. Приветствие
2. 1-2 точки совпадения с вакансией
3. Конкретный опыт из профиля
4. Предложение обсудить задачи

Не пересказывай резюме целиком.
Не используй названия прошлых компаний.
"""
        prompt_file.write_text(template, encoding="utf-8")
        print("cover_letter_prompt.md создан")

    # ---------- ШАГ 7 ----------
    def _step_hh_login(self):
        print("\n" + "=" * 60)
        print("ШАГ 7: АВТОРИЗАЦИЯ НА HH.RU")
        print("=" * 60)
        self._run_script("hh_login.py")

    # ---------- ШАГ 8 ----------
    def _step_test_letter(self):
        print("\n" + "=" * 60)
        print("ШАГ 8: ТЕСТ ГЕНЕРАЦИИ СОПРОВОДИТЕЛЬНОГО ПИСЬМА")
        print("=" * 60)
        self._run_script("test_letter.py")

    # ---------- ШАГ 9 ----------
    def _step_clean_db(self):
        print("\n" + "=" * 60)
        print("ШАГ 9: РАБОТА С БАЗОЙ ДАННЫХ")
        print("=" * 60)
        self._run_script("clean_db.py")

    # ---------- ШАГ 10 ----------
    def _step_run_apply(self):
        print("\n" + "=" * 60)
        print("ШАГ 10: ПОИСК РАБОТЫ")
        print("=" * 60)

        config_file = MY_DIR / "config.yaml"

        current_limit = 5
        current_schedule = ["09:30", "18:30"]
        if config_file.exists():
            try:
                import yaml
                with open(config_file, 'r', encoding='utf-8') as f:
                    cfg = yaml.safe_load(f) or {}
                current_limit = cfg.get("limits", {}).get("max_applications_per_run", 5)
                raw_schedule = cfg.get("schedule", {}).get("run_times", ["09:30", "18:30"])
                current_schedule = [str(t) for t in raw_schedule]
            except Exception as e:
                print(f"Ошибка чтения конфига: {e}")

        print("\nВыберите режим запуска:")
        print("1. Dry-run (только поиск и генерация, без отправки)")
        print("2. Prod-run (отклики, браузер видимый)")
        print("3. Prod-run (отклики, браузер в фоне)")
        print("4. Prod-run (расписание, отклики, браузер видимый)")
        print("5. Prod-run (расписание, отклики, браузер в фоне)")
        print("-" * 50)
        print(f"Текущий лимит откликов за запуск: {current_limit}")
        schedule_str = ", ".join(current_schedule)
        print(f"Текущее расписание: {schedule_str}")
        print()

        mode = input("Выберите режим (1-5): ").strip()

        updated = False
        max_apps = input(f"Количество откликов за запуск (Enter для {current_limit}): ").strip()

        new_schedule = None
        if mode in ["4", "5"]:
            schedule_input = input(f"Новое расписание (Enter для {schedule_str}): ").strip()
            if schedule_input:
                new_schedule = [t.strip() for t in schedule_input.split(",") if t.strip()]
                if new_schedule:
                    updated = True

        if max_apps or new_schedule:
            try:
                import yaml
                with open(config_file, 'r', encoding='utf-8') as f:
                    cfg = yaml.safe_load(f) or {}

                if max_apps:
                    try:
                        max_apps_int = int(max_apps)
                        if "limits" not in cfg:
                            cfg["limits"] = {}
                        cfg["limits"]["max_applications_per_run"] = max_apps_int
                        print(f"Лимит обновлён: {max_apps_int} откликов за запуск")
                        updated = True
                    except ValueError:
                        print(f"Используем текущий лимит: {current_limit}")

                if new_schedule:
                    if "schedule" not in cfg:
                        cfg["schedule"] = {}
                    cfg["schedule"]["run_times"] = [str(t) for t in new_schedule]
                    print(f"Расписание обновлено: {', '.join(cfg['schedule']['run_times'])}")
                    updated = True

                if updated:
                    self._save_yaml_preserve_format(config_file, cfg)

            except Exception as e:
                print(f"Ошибка обновления конфига: {e}")

        args = []
        use_xvfb = False

        if mode == "1":
            args = ["--once"]
            print("\nЗапуск в режиме DRY-RUN (без отправки)")
        elif mode == "2":
            args = ["--once", "--apply"]
            print("\nЗапуск PROD-RUN (отклики, браузер видимый)")
        elif mode == "3":
            args = ["--once", "--apply", "--headless"]
            print("\nЗапуск PROD-RUN (отклики, браузер в фоне)")
        elif mode == "4":
            args = ["--schedule", "--apply"]
            print("\nЗапуск ПО РАСПИСАНИЮ (отклики, браузер видимый)")
        elif mode == "5":
            args = ["--schedule", "--apply", "--headless"]
            print("\nЗапуск ПО РАСПИСАНИЮ (отклики, браузер в фоне)")
        else:
            print("Неверный выбор. Запуск в dry-run режиме.")
            args = ["--once"]

        if self.is_linux and not self.has_gui:
            if mode in ["2", "4"]:
                xvfb_choice = input("Использовать xvfb-run? (Y/N, Enter=Y): ").strip().upper()
                if xvfb_choice != "N":
                    use_xvfb = True
                    if "--headless" in args:
                        args.remove("--headless")
                    print("Будет использован xvfb-run")
                else:
                    if "--headless" not in args:
                        args.append("--headless")
                    print("Добавлен флаг --headless (браузер будет невидимым)")

        self._run_script("auto_apply.py", args, use_xvfb=use_xvfb)

    # ---------- ВСПОМОГАТЕЛЬНЫЕ ----------
    def _run_script(self, script_name: str, args: List[str] = None, use_xvfb: bool = False):
        script_path = self.root_dir / script_name
        if not script_path.exists():
            print(f"Скрипт {script_name} не найден в корне. Проверьте папку modules.")
            return

        cmd = []
        if use_xvfb:
            try:
                subprocess.run(["which", "xvfb-run"], capture_output=True, check=True)
                cmd = ["xvfb-run", "-a", sys.executable, str(script_path)]
            except:
                print("xvfb-run не найден. Запуск без xvfb.")
                cmd = [sys.executable, str(script_path)]
        else:
            cmd = [sys.executable, str(script_path)]

        if args:
            cmd.extend(args)

        print(f"\nЗапуск: {' '.join(cmd)}")
        print("-" * 60)
        try:
            subprocess.run(cmd, check=True)
            print("-" * 60)
            print(f"{script_name} выполнен успешно")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при выполнении {script_name}: {e}")
        except KeyboardInterrupt:
            print("\nПрервано пользователем")

    def _exit(self):
        print("\nДо свидания!")
        sys.exit(0)


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 70)
    print("HH-AUTO-APPLY SETUP TOOL")
    print("=" * 70)
    print("\nИнструмент для настройки проекта")
    print("Все шаги можно выполнять последовательно или выборочно\n")
    tool = SetupTool()
    while True:
        tool.show_menu()
        try:
            choice = input("\nВыберите шаг (1-11): ").strip()
            if not choice:
                continue
            step = int(choice)
            if 1 <= step <= 11:
                tool.run_step(step)
            else:
                print("Введите число от 1 до 11")
                input("Нажмите Enter...")
        except ValueError:
            print("Введите число")
            input("Нажмите Enter...")
        except KeyboardInterrupt:
            print("\nДо свидания!")
            sys.exit(0)


if __name__ == "__main__":
    main()

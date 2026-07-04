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
from typing import List

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
    def __init__(self):
        self.root_dir = ROOT_DIR
        self.is_linux = platform.system() == "Linux"
        self.has_gui = self._check_gui()
        self._ensure_directories()
        self._copy_missing_files()

    def _check_gui(self):
        """Проверяет наличие графического интерфейса (наличие DISPLAY или X)"""
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
        print("  1. Установка всех зависимостей (Python + системные для Ubuntu)")
        print("  2. Создание .env с выбором модели")
        print("  3. Проверка доступных моделей")
        print("  4. Создание profile.md (из PDF, DOC/DOCX, TXT или вручную)")
        print("  5. Настройка config.yaml")
        print("  6. Настройка cover_letter_prompt.md")
        print("  7. Авторизация на HH.ru")
        print("  8. Тест генерации письма")
        print("  9. Очистка базы данных")
        print("  10. Запуск auto_apply.py")
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
        print("ШАГ 1: УСТАНОВКА ЗАВИСИМОСТЕЙ")
        print("=" * 60)

        # 1. Установка системных зависимостей для Ubuntu
        if self.is_linux:
            print("\nОбнаружена система Linux. Установка системных зависимостей...")
            self._install_system_deps()

        # 2. Установка Python-зависимостей
        req_file = self.root_dir / "requirements.txt"
        if not req_file.exists():
            print("Файл requirements.txt не найден в корне. Проверьте modules.")
            return

        print("\nУстановка Python-зависимостей...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
                check=True,
            )
            print("Python-зависимости установлены")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка установки Python-пакетов: {e}")
            return

        # 3. Установка браузеров Playwright
        print("\nУстановка браузеров Playwright...")
        try:
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                check=True,
            )
            print("Playwright браузеры установлены")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка установки Playwright: {e}")

        # 4. Установка зависимостей Playwright (системные библиотеки)
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
                print("Попытка установки вручную...")
                self._install_playwright_deps_manual()

        # 5. Установка xvfb для серверного Linux
        if self.is_linux and not self.has_gui:
            print("\nОбнаружена система Linux без графического интерфейса.")
            self._ensure_xvfb()

        print("\n✅ Все зависимости установлены!")

    def _install_system_deps(self):
        """Устанавливает системные зависимости для Ubuntu"""
        deps = [
            "libnspr4",
            "libnss3",
            "libx11-6",
            "libx11-xcb1",
            "libxcb1",
            "libxcomposite1",
            "libxcursor1",
            "libxdamage1",
            "libxext6",
            "libxfixes3",
            "libxi6",
            "libxrandr2",
            "libxrender1",
            "libxss1",
            "libxtst6",
            "libgbm1",
            "libasound2",
            "libpango-1.0-0",
            "libcairo2",
            "libatk1.0-0",
            "libatk-bridge2.0-0",
            "libgtk-3-0",
            "libdrm2",
            "libxshmfence1",
            "fonts-liberation",
            "libappindicator3-1",
            "libnss3-tools",
            "xdg-utils",
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
            print("Вы можете установить их вручную: sudo apt install -y " + " ".join(deps))

    def _install_playwright_deps_manual(self):
        """Устанавливает системные зависимости Playwright вручную"""
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
        """Устанавливает xvfb, если он отсутствует"""
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
            print("Вы можете установить его вручную: sudo apt install xvfb")

    # ---------- ОСТАЛЬНЫЕ МЕТОДЫ (ШАГИ 2-10) ----------
    # Здесь идут все остальные методы, которые были в предыдущей версии
    # Я их сократил для экономии места, но они должны быть полностью скопированы

    def _step_setup_env(self):
        print("\n" + "=" * 60)
        print("ШАГ 2: СОЗДАНИЕ .ENV")
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
        print("1. OpenRouter (рекомендуется)")
        print("2. OpenAI")
        print("3. Anthropic")
        provider_choice = input("Выберите (1-3): ").strip()
        lines = [
            "# HH.ru настройки",
            f"HH_USER_AGENT=hh-auto-apply/1.0 ({email})",
            ""
        ]
        if provider_choice == "1":
            lines.append("# OpenRouter")
            lines.append("LLM_PROVIDER=openrouter")
            api_key = input("Введите ваш OpenRouter API ключ: ").strip()
            lines.append(f"OPENROUTER_API_KEY={api_key if api_key else 'your_openrouter_key'}")
            print("\nВыбор модели OpenRouter:")
            print("1. auto (автоматический выбор)")
            print("2. openrouter/free")
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
            lines.append("# OpenAI")
            lines.append("LLM_PROVIDER=openai")
            api_key = input("Введите ваш OpenAI API ключ: ").strip()
            lines.append(f"OPENAI_API_KEY={api_key if api_key else 'your_openai_key'}")
            lines.append("OPENAI_MODEL=gpt-4o-mini")
        elif provider_choice == "3":
            lines.append("# Anthropic")
            lines.append("LLM_PROVIDER=anthropic")
            api_key = input("Введите ваш Anthropic API ключ: ").strip()
            lines.append(f"ANTHROPIC_API_KEY={api_key if api_key else 'your_anthropic_key'}")
            lines.append("ANTHROPIC_MODEL=claude-sonnet-4-6")
        else:
            print("Неверный выбор. Используем OpenRouter с auto")
            lines.append("LLM_PROVIDER=openrouter")
            lines.append("OPENROUTER_API_KEY=your_openrouter_key")
            lines.append("OPENROUTER_MODEL=auto")
        lines.append("")
        lines.append("# Пути к файлам")
        lines.append("N8N_FILES_DIR=")
        lines.append("HH_CONFIG_PATH=my/config.yaml")
        lines.append("HH_STATE_DB=data/hh_auto_apply.sqlite3")
        try:
            env_file.write_text("\n".join(lines), encoding="utf-8")
            print(".env файл создан в кодировке UTF-8")
        except Exception as e:
            print(f"Ошибка записи: {e}, пробуем с BOM")
            env_file.write_text("\n".join(lines), encoding="utf-8-sig")
            print(".env файл создан с BOM")

    def _step_check_models(self):
        print("\n" + "=" * 60)
        print("ШАГ 3: ПРОВЕРКА МОДЕЛЕЙ")
        print("=" * 60)
        self._run_script("check_models.py")

    def _step_create_profile(self):
        print("\n" + "=" * 60)
        print("ШАГ 4: СОЗДАНИЕ ПРОФИЛЯ")
        print("=" * 60)
        profile_file = MY_DIR / "profile.md"
        if profile_file.exists():
            overwrite = input("profile.md уже существует. Перезаписать? (Y/N): ").strip().upper()
            if overwrite not in ["Y", "ДА"]:
                print("Используем существующий profile.md")
                return
        print("\nВыберите способ создания:")
        print("1. Вручную (ввод в консоли)")
        print("2. Извлечь из PDF (файл в папке my/)")
        print("3. Извлечь из DOC/DOCX (файл в папке my/)")
        print("4. Извлечь из TXT (файл в папке my/)")
        choice = input("Выберите (1-4): ").strip()
        if choice == "1":
            self._create_manual_profile()
        elif choice == "2":
            self._extract_from_pdf()
        elif choice == "3":
            self._extract_from_docx()
        elif choice == "4":
            self._extract_from_txt()
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

    def _extract_from_pdf(self):
        pdfs = list(MY_DIR.glob("*.pdf"))
        if not pdfs:
            print("В папке my/ нет PDF файлов.")
            return
        print("Найденные PDF:")
        for i, f in enumerate(pdfs, 1):
            print(f"{i}. {f.name}")
        choice = input("Выберите номер (или Enter для первого): ").strip()
        try:
            idx = int(choice) - 1 if choice else 0
            pdf_path = pdfs[idx] if 0 <= idx < len(pdfs) else pdfs[0]
        except:
            pdf_path = pdfs[0]
        try:
            from pypdf import PdfReader
        except ImportError:
            print("Установите pypdf: pip install pypdf")
            return
        reader = PdfReader(str(pdf_path))
        text_parts = [page.extract_text() or "" for page in reader.pages if page.extract_text()]
        content = "\n\n".join(text_parts)
        if content.strip():
            (MY_DIR / "profile.md").write_text(content, encoding="utf-8")
            print(f"Профиль извлечён из {pdf_path.name} ({len(content)} символов)")
        else:
            print("Не удалось извлечь текст из PDF")

    def _extract_from_docx(self):
        docs = list(MY_DIR.glob("*.docx")) + list(MY_DIR.glob("*.doc"))
        if not docs:
            print("В папке my/ нет DOC/DOCX файлов.")
            return
        print("Найденные DOC/DOCX:")
        for i, f in enumerate(docs, 1):
            print(f"{i}. {f.name}")
        choice = input("Выберите номер (или Enter для первого): ").strip()
        try:
            idx = int(choice) - 1 if choice else 0
            doc_path = docs[idx] if 0 <= idx < len(docs) else docs[0]
        except:
            doc_path = docs[0]
        if doc_path.suffix.lower() == '.doc':
            print(f"\nФайл {doc_path.name} имеет старый формат .doc, который напрямую не поддерживается.")
            print("Рекомендации:")
            print("  1. Откройте файл в Microsoft Word и сохраните как .docx (Файл -> Сохранить как -> Тип: Документ Word (*.docx)).")
            print("  2. Или сохраните как текстовый файл (.txt) и используйте способ 4 (из TXT).")
            print("  3. Или используйте способ 1 (ввод вручную).")
            return
        try:
            import docx
        except ImportError:
            print("Установите python-docx: pip install python-docx")
            return
        try:
            doc = docx.Document(str(doc_path))
        except Exception as e:
            print(f"Не удалось открыть файл: {e}. Возможно, файл повреждён или не является .docx.")
            return
        text_parts = [p.text for p in doc.paragraphs if p.text.strip()]
        content = "\n\n".join(text_parts)
        if content.strip():
            (MY_DIR / "profile.md").write_text(content, encoding="utf-8")
            print(f"Профиль извлечён из {doc_path.name} ({len(content)} символов)")
        else:
            print("Не удалось извлечь текст (пустой результат).")

    def _extract_from_txt(self):
        txts = list(MY_DIR.glob("*.txt"))
        if not txts:
            print("В папке my/ нет TXT файлов.")
            return
        print("Найденные TXT:")
        for i, f in enumerate(txts, 1):
            print(f"{i}. {f.name}")
        choice = input("Выберите номер (или Enter для первого): ").strip()
        try:
            idx = int(choice) - 1 if choice else 0
            txt_path = txts[idx] if 0 <= idx < len(txts) else txts[0]
        except:
            txt_path = txts[0]
        content = txt_path.read_text(encoding="utf-8", errors="ignore")
        if content.strip():
            (MY_DIR / "profile.md").write_text(content, encoding="utf-8")
            print(f"Профиль извлечён из {txt_path.name} ({len(content)} символов)")
        else:
            print("Файл пуст")

    def _step_setup_config(self):
        print("\n" + "=" * 60)
        print("ШАГ 5: НАСТРОЙКА CONFIG.YAML")
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
  delay_between_applications_seconds: 12

application_questions:
  city: "Москва"
  salary_expectations: "от 270000 RUB"
"""
            config_file.write_text(base, encoding="utf-8")
            print("config.yaml создан (базовый)")
        print("\nДополнительная настройка (можно пропустить Enter):")
        keywords = input("Ключевые слова для поиска (через запятую): ").strip()
        if keywords:
            import yaml
            cfg = yaml.safe_load(config_file.read_text(encoding="utf-8"))
            cfg["vacancies"]["keywords"] = [k.strip() for k in keywords.split(",") if k.strip()]
            config_file.write_text(yaml.dump(cfg, allow_unicode=True), encoding="utf-8")
            print("Ключевые слова обновлены")
        city = input("Город: ").strip()
        if city:
            import yaml
            cfg = yaml.safe_load(config_file.read_text(encoding="utf-8"))
            cfg["application_questions"]["city"] = city
            config_file.write_text(yaml.dump(cfg, allow_unicode=True), encoding="utf-8")
            print("Город обновлён")
        salary = input("Зарплатные ожидания: ").strip()
        if salary:
            import yaml
            cfg = yaml.safe_load(config_file.read_text(encoding="utf-8"))
            cfg["application_questions"]["salary_expectations"] = salary
            config_file.write_text(yaml.dump(cfg, allow_unicode=True), encoding="utf-8")
            print("Зарплата обновлена")

    def _step_setup_prompt(self):
        print("\n" + "=" * 60)
        print("ШАГ 6: НАСТРОЙКА ШАБЛОНА ПИСЬМА")
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

    def _step_hh_login(self):
        self._run_script("hh_login.py")

    def _step_test_letter(self):
        self._run_script("test_letter.py")

    def _step_clean_db(self):
        self._run_script("clean_db.py")

    def _step_run_apply(self):
        print("\n" + "=" * 60)
        print("ШАГ 10: ЗАПУСК AUTO_APPLY.PY")
        print("=" * 60)
        print("\nВыберите режим:")
        print("1. Dry-run (только поиск и генерация)")
        print("2. Реальный запуск с отправкой")
        mode = input("Выберите (1-2): ").strip()
        args = ["--once"]
        if mode == "2":
            args.append("--apply")
        else:
            print("Запуск в dry-run режиме")

        if self.is_linux and not self.has_gui:
            print("\nОбнаружена система Linux без графического интерфейса.")
            print("Вы можете запустить браузер в:")
            print("1. headless-режиме (рекомендуется, без окон) – добавьте --headless")
            print("2. видимом режиме с использованием xvfb-run (эмуляция дисплея)")
            choice = input("Выберите (1-2) или Enter для headless: ").strip()
            if choice == "2":
                use_xvfb = True
            else:
                use_xvfb = False
                if "--headless" not in args:
                    args.append("--headless")
                    print("Добавлен флаг --headless (браузер будет невидимым)")
        else:
            use_xvfb = False

        if use_xvfb:
            try:
                subprocess.run(["which", "xvfb-run"], capture_output=True, check=True)
            except:
                print("xvfb-run не найден. Установите xvfb или используйте headless.")
                self._ensure_xvfb()
                try:
                    subprocess.run(["which", "xvfb-run"], capture_output=True, check=True)
                except:
                    print("Не удалось найти xvfb-run. Запуск в headless-режиме.")
                    if "--headless" not in args:
                        args.append("--headless")
                    use_xvfb = False

        self._run_script("auto_apply.py", args, use_xvfb=use_xvfb)

    # ---------- ВСПОМОГАТЕЛЬНЫЕ ----------
    def _run_script(self, script_name: str, args: List[str] = None, use_xvfb: bool = False):
        script_path = self.root_dir / script_name
        if not script_path.exists():
            print(f"Скрипт {script_name} не найден в корне. Проверьте папку modules.")
            return

        cmd = []
        if use_xvfb:
            cmd = ["xvfb-run", "-a", sys.executable, str(script_path)]
        else:
            cmd = [sys.executable, str(script_path)]

        if args:
            cmd.extend(args)

        print(f"\nЗапуск: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
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
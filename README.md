# Telegram Chat Analysis Script

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![JSON](https://img.shields.io/badge/JSON-Compatible-orange.svg)

## Navigation / Навигация

- [English](#english)
  - [Features](#features)
  - [Usage](#usage)
  - [Configuration Options](#configuration-options)
- [Русский](#русский)
  - [Возможности](#возможности)
  - [Использование](#использование)
  - [Параметры конфигурации](#параметры-конфигурации)

## English

Telegram Chat Statistics based on JSON export

### Features

- Analyzes Telegram chat exports in JSON format.
- Detailed chat activity statistics, including message counts, word frequencies, and participant rankings.
- Customizable parameters via `config.py`, allowing modification of stop words, profanity detection, and more.
- Merging multiple JSON files into one.
- Generation of reports in TXT and JSON formats.
- Support for Russian and English languages.

### Usage

1. **Preparing the chat export**
   - Export your Telegram chat using the built-in export feature in the chat menu.
   - Select JSON format when exporting.
   - Place the exported `result.json` file in the same directory as the script.
   - If you have multiple exports, name them `result1.json`, `result2.json`, ...

2. **Configuring the script (optional)**
   - Open `config.py` to customize parameters such as stop words, emojis, profanity words, and others.
   - Modify settings like `input_file`, `merge_folder`, and `output_filename_pattern` as needed.

3. **Running the script**
   - Terminal in the script directory.
   - `python start.py`

4. **Then — user-friendly interface**

5. **View the results**
```
Chat Statistics for "Name" for the period: X – Y

✉️ Messages: [] ([] non-consecutive)
🔣 Characters: [] ([] non-consecutive)
💬 Characters per message: []

🖼 Images: []
📹 Videos: []
📑 Files: []
🎧 Audio: []
🔗 Links: []
🎵 Voice messages: []
🎬 GIFs: []
💌 Stickers: []
🥵 Emojis: []
📊 Polls: []
❗ Commands: []
💢 Messages with profanity: []

👥 Top participants:
[]

🔠 Top words:
[]

📊 Activity:
Hours
Days of the week
Months of years
Years

📊 Most active days:
[]
```

### Configuration Options

See `config.py` for detailed configuration options, including:
- Input and output file settings
- Analysis parameters (top participants, words, days, etc.)
- Language and emoji settings
- Bot and profanity detection options

## Русский

Статистика чата Telegram на основе JSON-экспорта

### Возможности

- Анализирует экспорт чата Telegram в формате JSON.
- Детальная статистика активности чата, включая количество сообщений, частоту слов и рейтинг участников.
- Настраиваемые параметры через `config.py`, позволяющие изменять стоп-слова, определять нежелательные слова и многое другое.
- Объединение нескольких JSON файлов в один.
- Генерация отчётов в TXT и JSON.
- Поддержка русского и английского языков.

### Использование

1. **Подготовка экспорта чата**
   - Экспортируйте ваш чат Telegram, используя встроенную функцию экспорта в меню чата.
   - Выберите формат JSON при экспорте.
   - Поместите экспортированный файл `result.json` в ту же директорию, что и скрипт.
   - Если экспортов несколько, назовите их `result1.json`, `result2.json`, …

2. **Настройка скрипта (опционально)**
   - Откройте `config.py` для настройки параметров, таких как стоп-слова, эмодзи, нежелательные слова и другие.
   - Измените настройки, такие как `input_file`, `merge_folder` и `output_filename_pattern`, по необходимости.

3. **Запуск скрипта**
   - Терминал в директории скрипта.
   - `python start.py`

4. **Далее — понятный интерфейс**

5. **Просмотрите результаты**
```
Статистика чата "Название" за период: X – Y

✉️ Сообщений: [] ([] не подряд)
🔣 Символов: [] ([] не подряд)
💬 Символов в сообщении: []

🖼 Изображений: []
📹 Видео: []
📑 Файлы: []
🎧 Аудио: []
🔗 Ссылки: []
🎵 Голосовых: []
🎬 GIF: []
💌 Стикеров: []
🥵 Эмодзи: []
📊 Опросов: []
❗ Команд: []
💢 Сообщений с матом: []

👥 Топ участников:
[]

🔠 Топ слов:
[]

📊 Активность:
Часы
Дни недели
Месяцы годов
Года

📊 Самые активные дни:
[]
```

### Параметры конфигурации

См. `config.py` для детальных параметров конфигурации, включая:
- Настройки входных и выходных файлов
- Параметры анализа (топ участников, слов, дней и т.д.)
- Настройки языка и эмодзи
- Опции обнаружения ботов и нежелательной лексики
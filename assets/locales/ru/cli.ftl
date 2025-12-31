# --- App Meta ---
app-title = Версия { $version }
description = Статистика персональных и публичных чатов и каналов из JSON-файла
link-github = ⚡️ Обновления на ГитХабе: { $url }
link-telegram = ⚡️ Телеграм-канал: { $url }

# --- Loader Messages ---
analyzing-file = 📂 Чтение метаданных из { $file }...
analyzing = ⏳ Анализ сообщений...
status-generating-report = 📝 Генерация текстового отчета...
status-saving-json = 💾 Сохранение JSON данных...
status-visualizing = 🎨 Генерация графиков активности...
status-visualizing-heatmap = 🎨 Генерация тепловой карты...
status-visualizing-cloud = ☁️ Генерация облака слов...
analysis-complete = Сообщения проанализированы: { $count } шт.
op-cancelled = 🛑 Операция отменена пользователем.
press-enter = Нажмите Enter для продолжения...
time-elapsed = ⏱  Общее время: { $time }s

# --- File Status & Warnings ---
file-not-found = ❌ Ошибка: Файл '{ $file }' не найден.
file-instruction =    Переименуйте экспорт в '{ $default }' или обновите config.py.
file-size-warning = ⚠️ Размер файла: { $size } МБ. Обработка может занять время (включен потоковый режим).
warn-lemmatization-slow = Включена лемматизация. Скорость анализа будет значительно снижена (в 5-10 раз).

found-default = Найден файл, указанный в настройках.
found-auto = Автоматически найден файл.
auto-detected-file = Обнаружен файл: { $file }
err-ambiguous-files = Найдено несколько JSON файлов. Автовыбор невозможен.
err-no-files = JSON файлы не найдены в текущей папке.
hint-ambiguous = Пожалуйста, переименуйте файл в 'result.json' или укажите путь в настройках.
confirm-analysis = Анализировать этот файл? [Д/н]
multi-file-detected = Обнаружен многотомный архив: { $count } файлов.

menu-merged = ✅ Успешно объединено! Новый файл: { $file }
menu-merge-fail = ❌ Не удалось объединить файлы.
menu-search = 🔍 Поиск файлов result*.json...

# --- Interactive Menu ---
select-action = Действия
menu-prompt = Номер или Enter:
menu-0-lang = Язык / Language
menu-1-analyze = Анализировать файл
menu-2-json = Анализировать и сохранить результат в JSON
menu-3-merge = Объединить файлы 'resultNUMBER.json'
menu-4-config = Настройки
menu-5-exit = Выход

# --- Config Wizard ---
cli-config-title = --- КОНФИГУРАЦИЯ ---
cli-date-prompt = 📅 Введите диапазон дат (ДД.ММ.ГГГГ-ДД.ММ.ГГГГ)
cli-date-hint = Оставьте пустым для анализа всего периода
cli-range-set = ✅ Установлен период: { $start } — { $end }
cli-invalid-format = ⚠️ Неверный формат. Будет использован весь период.
cli-lang-prompt = 🌐 Язык анализа [ru/en]
cli-offset-prompt = ⏰ Часовой пояс (смещение в часах)
cli-threshold-prompt = ⏱ Порог нового диалога (часов)
cli-bots-prompt = 🤖 Исключать ботов из статистики?
cli-lemmatize-prompt = 🧠 Включить лемматизацию? (Медленно!)
cli-cloud-prompt = ☁️ Генерировать облако слов?
cli-full-json-prompt = 💾 Полный JSON экспорт (вся история)?
cli-show-links-prompt = 🔗 Показывать ссылки на профили в отчете?
cli-save-prompt = Сохранить эти настройки в 'settings.json'?
cli-saved = Настройки успешно сохранены.
cli-save-error = Ошибка сохранения настроек: { $error }
cli-invalid-choice = ❌ Неверный выбор. Использую по умолчанию: { $default }
cli-config-applied = ✅ Настройки применены.

cli-sw-title = 🛑 Выбор списка стоп-слов:
cli-sw-minimal = Минимальный (рекомендуется)
cli-sw-extended = Расширенный (агрессивный)
cli-choice-input = Ваш выбор
cli-sw-selected = Выбран тип: { $type }

cli-sort-prompt = 🗂 Сортировка участников по
cli-sort-1 = 1. Количеству сообщений (Default)
cli-sort-2 = 2. Объему текста (символы)
cli-sort-3 = 3. Активным дням
cli-sort-4 = 4. Количеству медиа
cli-sort-5 = 5. Алфавиту

# --- JSON Output ---
report-saved = ✨ Успех! Отчет сохранен: { $file }
json-done = ✅ JSON сохранен (Full: { $full })

# --- Update System ---
update-available-title = Доступно обновление: { $version }
update-critical-title = Требуется обновление
update-critical-desc = Протокол обновлений изменился. Пожалуйста, скачайте новую версию вручную.
update-alert-prefix = СИСТЕМНОЕ СООБЩЕНИЕ:
update-error-generic = Ошибка проверки обновлений: { $error }
update-manual-link = Скачать: { $url }
update-req-pip = Требует обновления библиотек
update-req-config = Рекомендуется сброс настроек
update-more-items = ... и еще { $count } обновлений

# --- General CLI ---
invalid-choice = Неверный выбор
goodbye = До свидания!
error-prefix = Ошибка
cli-merge-en-prompt = Исключить английские слова-паразиты (the, is, etc)?
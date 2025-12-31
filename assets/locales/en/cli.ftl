# --- App Meta ---
app-title = Version { $version }
description = Statistics for personal/public chats and channels based on JSON export
link-github = ⚡️ GitHub updates: { $url }
link-telegram = ⚡️ Telegram channel: { $url }

# --- Loader Messages ---
analyzing-file = 📂 Reading metadata from { $file }...
analyzing = ⏳ Analyzing messages...
status-generating-report = 📝 Generating text report...
status-saving-json = 💾 Saving JSON data...
status-visualizing = 🎨 Generating activity charts...
status-visualizing-heatmap = 🎨 Generating heatmap...
status-visualizing-cloud = ☁️ Generating word cloud...
analysis-complete = Messages processed: { $count }
op-cancelled = 🛑 Operation cancelled by user.
press-enter = Press Enter to continue...
time-elapsed = ⏱  Total time: { $time }s

# --- File Status & Warnings ---
file-not-found = ❌ Error: File '{ $file }' not found.
file-instruction =    Rename export to '{ $default }' or update config.py.
file-size-warning = ⚠️ File size: { $size } MB. Processing might take time (Streaming mode).
warn-lemmatization-slow = Lemmatization is enabled. Analysis speed will be significantly reduced (5-10x).

found-default = Found configured input file.
found-auto = Auto-detected input file.
auto-detected-file = Auto-detected file: { $file }
err-ambiguous-files = Multiple JSON files found. Cannot auto-select.
err-no-files = No JSON files found in the current directory.
hint-ambiguous = Please rename the target file to 'result.json' or configure the path in settings.
confirm-analysis = Analyze this file? [Y/n]
multi-file-detected = Multi-part archive detected: { $count } files.

menu-merged = ✅ Successfully merged! New file: { $file }
menu-merge-fail = ❌ Failed to merge files.
menu-search = 🔍 Searching for result*.json...

# --- Interactive Menu ---
select-action = Actions
menu-prompt = Choice or Enter:
menu-0-lang = Language / Язык
menu-1-analyze = Analyze file
menu-2-json = Analyze + JSON export
menu-3-merge = Merge 'resultNUMBER.json' files
menu-4-config = Configure Settings
menu-5-exit = Exit

# --- Config Wizard ---
cli-config-title = --- CONFIGURATION ---
cli-date-prompt = 📅 Enter date range (DD.MM.YYYY-DD.MM.YYYY)
cli-date-hint = Leave empty for full history
cli-range-set = ✅ Range set: { $start } — { $end }
cli-invalid-format = ⚠️ Invalid format. Using full period.
cli-lang-prompt = 🌐 Analysis Language [ru/en]
cli-offset-prompt = ⏰ Timezone offset (hours)
cli-threshold-prompt = ⏱ New dialog threshold (hours)
cli-bots-prompt = 🤖 Exclude bots from stats?
cli-lemmatize-prompt = 🧠 Enable lemmatization? (Slow!)
cli-cloud-prompt = ☁️ Generate word cloud?
cli-full-json-prompt = 💾 Full JSON export (all history)?
cli-show-links-prompt = 🔗 Show profile links in report?
cli-save-prompt = Save these settings to 'settings.json'?
cli-saved = Settings successfully saved.
cli-save-error = Failed to save settings: { $error }
cli-invalid-choice = ❌ Invalid choice. Using default: { $default }
cli-config-applied = ✅ Settings applied.

cli-sw-title = 🛑 Stop-words list:
cli-sw-minimal = Minimal (recommended)
cli-sw-extended = Extended (aggressive)
cli-choice-input = Your choice
cli-sw-selected = Selected type: { $type }

cli-sort-prompt = 🗂 Sort participants by
cli-sort-1 = 1. Message count (Default)
cli-sort-2 = 2. Text volume (symbols)
cli-sort-3 = 3. Active days
cli-sort-4 = 4. Media count
cli-sort-5 = 5. Alphabetical

# --- JSON Output ---
report-saved = ✨ Success! Report saved: { $file }
json-done = ✅ JSON saved (Full: { $full })

# --- Update System ---
update-available-title = Update available: { $version }
update-critical-title = Update required
update-critical-desc = The update protocol has changed. Please download the latest version manually.
update-alert-prefix = SYSTEM ALERT:
update-error-generic = Update check failed: { $error }
update-manual-link = Download: { $url }
update-req-pip = Dependencies update required
update-req-config = Config reset recommended
update-more-items = ... and { $count } more updates

# --- General CLI ---
invalid-choice = Invalid choice
goodbye = Goodbye!
error-prefix = Error
cli-merge-en-prompt = Remove English stopwords/noise?
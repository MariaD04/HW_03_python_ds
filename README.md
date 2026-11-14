# Books Scraper

## Цель

Автоматический сбор данных о книгах с сайта
[Books to Scrape](http://books.toscrape.com)

Проект содержит следующие функции:

* `get_book_data` — извлекает данные одной книги: название, категорию,
  цену, рейтинг (1–5), количество в наличии, описание и все поля таблицы
  Product Information (UPC, Tax и т. д.);
* `scrape_books` — обходит все страницы каталога (1000 книг) и при
  необходимости сохраняет результат в `books_data.txt`;
* `run_scheduler` — запускает сбор данных автоматически каждый день
  в 19:00 с помощью библиотеки `schedule`;
* автотесты на `pytest` (`tests/test_scraper.py`).

## Инструкции по запуску

1. Клонировать репозиторий и перейти в папку проекта:

   ```bash
   git clone git@github.com:MariaD04/HW_03_python_ds.git
   cd books_scraper
   ```

2. Создать виртуальное окружение и установить зависимости:

   ```bash
   python -m venv venv
   source venv/bin/activate        
   pip install -r requirements.txt
   ```

3. Запустить сбор данных:

     ```bash
     python scraper.py
     ```

4. Запустить тесты:

   ```bash
   pytest tests/test_scraper.py -v   
   pytest                  
   ```

Ноутбук с выполненными заданиями: `notebooks/HW_03_python_ds.ipynb`.
Результат сбора данных: `artifacts/books_data.txt`.

## Используемые библиотеки

* `requests` — HTTP-запросы к сайту;
* `beautifulsoup4` — разбор HTML;
* `schedule` — ежедневный запуск по расписанию;
* `pytest` — автотесты.

Также используются модули стандартной библиотеки: `json`, `re`, `time`.

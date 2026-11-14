import os
import time
import re
import requests
import schedule
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def get_book_data(book_url: str) -> dict:
    """
    Собирает данные о книге со страницы товара.

    Args:
        book_url (str): ссылка на страницу книги.

    Returns:
        dict: словарь с полями title, category, price, rating,
            availability (число штук в наличии), description, url, а также
            все характеристики из таблицы Product Information.
    """
    response = requests.get(book_url, timeout=10)
    response.raise_for_status()

    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    product = soup.find('article', class_='product_page')

    title = product.find('h1').get_text(strip=True)
    price = product.find('p', class_='price_color').get_text(strip=True)

    rating_class = product.find('p', class_='star-rating')['class'][1]
    rating = ['One', 'Two', 'Three', 'Four', 'Five'].index(rating_class) + 1

    availability_text = product.find(
        'p', class_='availability').get_text(strip=True)
    match = re.search(r'\((\d+) available\)', availability_text)
    availability = int(match.group(1)) if match else 0

    description = ''
    description_block = product.find('div', id='product_description')
    if description_block is not None:
        description = description_block.find_next_sibling(
            'p').get_text(strip=True)

    category = soup.select('ul.breadcrumb li')[2].get_text(strip=True)

    data = {
        'title': title,
        'category': category,
        'price': price,
        'rating': rating,
        'availability': availability,
        'description': description,
        'url': book_url,
    }

    for row in product.select('table.table-striped tr'):
        data[row.find('th').get_text(strip=True)] = row.find(
            'td').get_text(strip=True)

    return data

def scrape_books(is_save: bool = True, max_pages: int = None) -> list:
    """Обходит все страницы каталога и собирает данные о каждой книге.

    Args:
        is_save (bool): если True, результат сохраняется в
            artifacts/books_data.txt (одна книга — одна JSON-строка).
        max_pages (int | None): ограничение числа страниц для отладки; None —
            обойти весь каталог.

    Returns:
        list[dict]: список словарей с данными о книгах.
    """
    books = []
    page = 1
    while max_pages is None or page <= max_pages:
        response = requests.get(
            f'http://books.toscrape.com/catalogue/page-{page}.html', timeout=10
        )
        if response.status_code == 404:
            break
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.select('article.product_pod h3 a'):
            book_url = 'http://books.toscrape.com/catalogue/' + link['href']
            books.append(get_book_data(book_url))
        page += 1

    if is_save:
        if os.path.basename(os.getcwd()) == 'notebooks':
            output_dir = os.path.join('..', 'artifacts')
        else:
            output_dir = 'artifacts'
            
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, 'books_data.txt')
        with open(file_path, 'w', encoding='utf-8') as file:
            for book in books:
                file.write(json.dumps(book, ensure_ascii=False) + '\n')

    return books

def run_scheduler(run_time: str = '19:00', max_seconds: int = None) -> None:
  """Запускает сбор данных о книгах каждый день в заданное время.

  Args:
      run_time (str): время запуска в формате 'ЧЧ:ММ'.
      max_seconds (int | None): через сколько секунд остановить цикл (для
          проверки); None — работать бесконечно.
  """
  schedule.clear()
  schedule.every().day.at(run_time).do(
      scrape_books, is_save=True, max_pages=1
  )

  start = time.time()
  while max_seconds is None or time.time() - start < max_seconds:
    schedule.run_pending()
    time.sleep(10) 


if __name__ == '__main__':
  print('Запуск планировщика в тестовом режиме на 60 секунд...')
  current_time_str = (datetime.now() + timedelta(minutes=1)).strftime('%H:%M')
  run_scheduler(current_time_str, max_seconds=60)
  print('Тест планировщика успешно завершен!')
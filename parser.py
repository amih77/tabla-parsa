import os
import re

from bs4 import BeautifulSoup


def parse_html_document(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract title (using caption as title)
    title = soup.caption.text.strip() if soup.caption else 'No Caption'

    # Extract header (column names)
    headers = [th.get_text(strip=True) for th in soup.thead.find_all('th')]
    header = ', '.join(headers)

    # Extract body (all rows of the table)
    body_rows = [[td.get_text(strip=True) for td in tr.find_all('td')] for tr in soup.tbody.find_all('tr')]
    body = ['; '.join(row) for row in body_rows]
    body_content = ' | '.join(body)

    # Extract footer (and country, date of creation)
    footer = soup.tfoot.tr.td.get_text(strip=True) if soup.tfoot else 'No Footer'
    country_of_creation = "Unknown"
    date_of_creation = "Unknown"
    footer_match = re.search(r'Creation: (\d{2}[a-zA-Z]{3}\d{4}) (.+)', footer)
    if footer_match:
        date_of_creation, country_of_creation = footer_match.groups()


    a = 5
    # document_id = documents_col.insert_one({
    #     'title': title,
    #     'header': header,
    #     'body': body,
    #     'footer': footer,
    #     'country_of_creation': country_of_creation,
    #     'date_of_creation': date_of_creation
    # }).inserted_id
    #
    # return document_id

dir = "documents"
for filename in os.listdir("documents"):
    if os.path.isfile(os.path.join(dir, filename)):
        print(filename)
    parse_html_document(os.path.join(dir, filename))
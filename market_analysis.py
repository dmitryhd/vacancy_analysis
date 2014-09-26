import bs4
import requests
import re

def get_url(url):
    """ Get HTML page by its URL """
    s = requests.Session()
    page = s.get(url).text
    return page

def get_vacancies_on_page(url):
    page = get_url(url)
    soup = bs4.BeautifulSoup(page)
    for vacancy in soup.find_all('div', class_='searchresult__name'):
        name = vacancy.string
        if name is not None:
            print(name)
            link = vacancy.find_all('a')[0].attrs["href"]
            print(link)
            #new_page = get_url(link)
            #print(new_page)
    next_link = 'http://hh.ru' + soup.find_all('a', class_='b-pager__next-text')[1].attrs["href"]
    print('next = ', next_link)
    return next_link

if __name__ == '__main__':
    # all for programmer
    base_url = 'http://hh.ru/search/vacancy?source=&text=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82&specialization=1&specialization=8&specialization=12&specialization=14&area=1&salary=&currency_code=RUR&only_with_salary=true&experience=&employment=full&order_by=relevance&search_period=&items_on_page=100&no_magic=true&page=1'
    next_link = base_url
    for i in range(200):
        next_link = get_vacancies_on_page(next_link)

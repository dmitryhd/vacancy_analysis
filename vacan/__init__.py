from vacan.web_interface import web
from vacan.processor import vacancy_processor

def start_web_server():
    web.start_server()

def start_processor():
    vacancy_processor.main()

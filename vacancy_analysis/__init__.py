from vacancy_analysis.web_interface import web
from vacancy_analysis.processor import vacancy_processor

def main():
    """ Entry point for the application script. """
    print("Omg, vac an installed")

def start_web_server():
    print('Starting web interface.')
    web.start_server()

def start_processor():
    print('Starting processor.')
    vacancy_processor.main()

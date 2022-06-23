import dns.resolver
from itertools import product


class SimilarDomains:
    DOMAIN_ZONES = ['com', 'ru', 'net', 'org', 'info', 'cn', 'es', 'top', 'au', 'pl', 'it', 'uk', 'tk', 'ml', 'ga',
                    'cf',
                    'us', 'xyz', 'top', 'site', 'win', 'bid']

    def __init__(self, primary_set_of_words):
        """Инициализирует объект класса SimilarDomains.

        :param primary_set_of_words: Набор первичных ключевых слов
        :type primary_set_of_words: list
        """
        self.primary_set_of_words = primary_set_of_words
        self.domains = self.get_domains_list()
        self.existing_domains = []

    def get_domains_list(self):
        """Генерирует доменные имена.

        :return: Список доменных имен
        :rtype: list
        """
        return ['.'.join(item) for item in product(self.primary_set_of_words, self.DOMAIN_ZONES)]

    def request_domain(self, domain):
        """Получает ip запросом к днс по доменному имени.

        :param domain: Доменное имя
        :type domain: str
        :return: None
        """
        try:
            response = dns.resolver.resolve(domain, 'A')
            ip = response[0]
            self.existing_domains.append((domain, ip))
        except dns.resolver.NXDOMAIN:
            print(f'Имя запроса {domain} не существует')


# request_domain(domain=primary_set_of_words)

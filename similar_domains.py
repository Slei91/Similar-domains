import string
import dns.resolver
from itertools import product
import homoglyphs as hg
import concurrent.futures


class SimilarDomains:
    DOMAIN_ZONES = [
        'com', 'ru', 'net', 'org', 'info', 'cn', 'es', 'top', 'au', 'pl', 'it', 'uk', 'tk', 'ml', 'ga',
        'cf', 'us', 'xyz', 'top', 'site', 'win', 'bid'
    ]

    def __init__(self, primary_set_of_words):
        """Инициализирует объект класса SimilarDomains.

        :param primary_set_of_words: Набор первичных ключевых слов
        :type primary_set_of_words: list
        """
        self.primary_set_of_words = primary_set_of_words
        self.words_after_applying_strategies = []
        self.existing_domains = []

    def get_domains_list(self, words_list):
        """Генерирует доменные имена подставлением доменных зон.

        :param words_list: Список слов
        :type words_list: list
        :return: Список доменных имен
        :rtype: list
        """
        return ['.'.join(item) for item in product(words_list, self.DOMAIN_ZONES)]

    def run(self):
        """Запускает логику подбора похожих доменов.

        Выполняется применение стратегий формирования ключевых слов доменного имени,
        добавляются доменные зоны, осуществляется запрос к днс по доменному имени.

        :return: None
        """
        self.apply_strategies()
        domains = self.get_domains_list(self.words_after_applying_strategies)

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            for d_name in domains:
                executor.submit(self.request_domain, d_name)
        print(self.existing_domains)

    def request_domain(self, domain):
        """Получает ip запросом к днс по доменному имени.

        :param domain: Доменное имя
        :type domain: str
        :return: None
        """
        try:
            ip = dns.resolver.resolve(domain, 'A', lifetime=1)[0].to_text()
            self.existing_domains.append((domain, ip))
        except dns.resolver.NXDOMAIN:
            print(f'Домена {domain} не существует')
        except Exception:
            pass

    @staticmethod
    def _strategy_adding_one_character_to_end(word):
        """Формирует список добавлением одного символа в конец слова.

        :param word: Ключевое слово доменного имени
        :type word: str
        :return: Список сформированых доменных имен
        :rtype: list
        """
        return [word + i for i in string.ascii_letters]

    @staticmethod
    def _strategy_homoglyph(word):
        """Формирует список стратегией замены похожих символов.

        :param word: Ключевое слово доменного имени
        :type word: str
        :return: Список сформированых доменных имен
        :rtype: list
        """
        homoglyphs = hg.Homoglyphs(categories=('LATIN', 'CYRILLIC'), strategy=hg.STRATEGY_LOAD)
        result = homoglyphs.get_combinations(word)
        return result

    @staticmethod
    def _strategy_subdomain_selection(word):
        """Формирует список добавлением точки.

        :param word: Ключевое слово доменного имени
        :type word: str
        :return: Список сформированых доменных имен
        :rtype: list
        """
        result = []
        for i in range(1, len(word)):
            result.append(word[:i] + '.' + word[i:])
        return result

    @staticmethod
    def _strategy_delete_one_character(word):
        """Формирует список удалением символа.

        :param word: Ключевое слово доменного имени
        :type word: str
        :return: Список сформированых доменных имен
        :rtype: list
        """
        result = []
        for i in range(len(word)):
            result.append(word[:i] + word[i + 1:])
        return result

    def apply_strategies(self):
        """Применяет стратегии к ключевым словам.

        :return: None
        """
        for word in self.primary_set_of_words:
            self.words_after_applying_strategies.extend(self._strategy_adding_one_character_to_end(word))
            self.words_after_applying_strategies.extend(self._strategy_homoglyph(word))
            self.words_after_applying_strategies.extend(self._strategy_subdomain_selection(word))
            self.words_after_applying_strategies.extend(self._strategy_delete_one_character(word))


test = SimilarDomains(['ozon'])
test.run()

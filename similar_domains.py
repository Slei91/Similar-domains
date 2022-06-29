import string
import dns.asyncresolver
from itertools import product
import homoglyphs as hg
import click
import asyncio


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

    async def run(self):
        """Запускает логику подбора похожих доменов.

        Выполняется применение стратегий формирования ключевых слов доменного имени,
        добавляются доменные зоны, осуществляется запрос к днс по доменному имени.

        :return: None
        """
        self.apply_strategies()
        domains = self.get_domains_list(self.words_after_applying_strategies)

        tasks = []
        for domain in domains:
            task = asyncio.create_task(self.request_domain(domain))
            tasks.append(task)
        await asyncio.gather(*tasks)

        print(self.existing_domains)

    async def request_domain(self, domain):
        """Получает ip запросом к днс по доменному имени.

        :param domain: Доменное имя
        :type domain: str
        :return: None
        """
        try:
            coro = await dns.asyncresolver.resolve(domain, 'A', lifetime=1)
            ip = coro[0].to_text()
            self.existing_domains.append((domain, ip))
        except dns.asyncresolver.NXDOMAIN:
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


@click.command()
@click.argument('words', nargs=-1)
def similar_domains_run(words):
    """Скрипт подбора похожих доменов.

    WORDS - ключевые слова.
    """
    obj = SimilarDomains(words)
    asyncio.run(obj.run())


if __name__ == '__main__':
    similar_domains_run()

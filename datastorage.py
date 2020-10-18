import sqlite3

from abc import abstractmethod, ABC
from typing import Iterable
import datetime


def bot_logging(fn):
    """
    Логирует ошибки с базой данных (создание и изменение записей)
    *надо придумать чего получше*
    """
    def wrapper(*args, **kwargs):
        """
        Пытаемся выполнить функцию, и ловим любое исключение
        Если поймали, то записываем в файл bot_logs.txt
        """
        try:
            fn(*args, **kwargs)
        except Exception as error:
            time = datetime.datetime.now()
            try:
                log = f"{time} Error:<{error}>, module: <{error.__module__}>, doc: <{error.__doc__}>\n"
            except AttributeError:
                log = f"{time} Error:<{error}>, module: <None>, doc: <{error.__doc__}>\n"
            print(log)
            with open('bot_logs.txt', 'a') as logfile:
                logfile.writelines(f"{log}\targs:{args}, kwargs:{kwargs}\n")
    return wrapper


class DataStorage(object):
    """
    Абстрактный класс для работы с базами данных
    """
    @abstractmethod
    def get_objects(self, table_name: str) -> Iterable[dict]:
        pass

    @abstractmethod
    def get_object(self, key: str) -> dict:
        pass

    @abstractmethod
    def get_any_object(self, ) -> dict:
        pass


class SqliteDataStorage(DataStorage, ABC):
    """
    Класс для работы с базой данных (sqlite)
    """
    def __init__(self, collection: str):
        """
        Создаём таблицы для игровых серверов (BoB, TheIsle)
        :param collection: Имя базы данных
        """
        self._connection = sqlite3.connect(f'{collection}.db')
        self._cursor = self._connection.cursor()
        self._cursor.execute("""
                                CREATE TABLE IF NOT EXISTS BoB_Users 
                                (
                                Dis_ID          BIGINT UNIQUE NOT NULL,
                                Steam_ID        BIGINT,
                                t_coins         INT DEFAULT 0,
                                t_coins_history INT DEFAULT 0
                                )
                            """
                             )
        self._cursor.execute("""
                                CREATE TABLE IF NOT EXISTS TheIsle_Users 
                                (
                                Dis_ID          BIGINT UNIQUE NOT NULL,
                                Steam_ID        BIGINT,
                                t_coins         INT DEFAULT 0,
                                t_coins_history INT DEFAULT 0
                                )
                            """
                             )
        # """Для системы слотов на серверах TheIsle (не реализовано)"""
        # for N in range(1, 5, 1):
        #     self._cursor.execute("""
        #                             CREATE TABLE IF NOT EXISTS Slot_{}
        #                             (
        #                                 Steam_ID                      BIGINT  PRIMARY KEY,
        #                                 CharacterClass                TEXT,
        #                                 Location_Thenyaw_Island       TEXT,
        #                                 Rotation_Thenyaw_Island       TEXT,
        #                                 Growth                        TEXT,
        #                                 Hunger                        TEXT,
        #                                 Thirst                        TEXT,
        #                                 Stamina                       TEXT,
        #                                 Health                        TEXT,
        #                                 BleedingRate                  TEXT,
        #                                 Oxygen                        TEXT,
        #                                 bGender                       BOOLEAN,
        #                                 bIsResting                    BOOLEAN,
        #                                 bBrokenLegs                   BOOLEAN,
        #                                 ProgressionPoints             TEXT,
        #                                 ProgressionTier               TEXT,
        #                                 UnlockedCharacters            TEXT,
        #                                 CameraRotation_Thenyaw_Island TEXT,
        #                                 CameraDistance_Thenyaw_Island TEXT,
        #                                 SkinPaletteSection1           INT,
        #                                 SkinPaletteSection2           INT,
        #                                 SkinPaletteSection3           INT,
        #                                 SkinPaletteSection4           INT,
        #                                 SkinPaletteSection5           INT,
        #                                 SkinPaletteSection6           INT,
        #                                 SkinPaletteVariation          TEXT
        #                             )
        #                         """.format(N)
        #                          )

    @bot_logging
    def create_account(self, table: str, user_id: int) -> True or None:
        """
        Создание записи об игроке
        """
        print("Создаю запись об игроке:", user_id)
        self._cursor.execute("INSERT INTO {} (Dis_ID) VALUES({})".format(table, user_id))
        self._connection.commit()
        return True

    @bot_logging
    def set_balance(self, table: str, user_id, coins: int, coins_history: int) -> True or None:
        """
        Установка баланнса игровой валюты для пользователя
        :param table: Имя таблицы (название сервера)
        :param user_id: Айди юзера
        :param coins: текущий баланс
        :param coins_history: сумма всей заработанной игровой валюты (аналог "опыта" пользователя)
        :return: True or None
        """
        self._cursor.execute(
            """
            UPDATE {}
            SET t_coins = {}, t_coins_history = {} 
            WHERE Dis_ID={}
            """.format(table, coins, coins_history, user_id)
        )
        self._connection.commit()
        return True

    @bot_logging
    def create_marriage_tabel(self, server_name: str):
        """
        создаём таблицы браков (для хранения данных о "браках" пользователей
        :param server_name: Название сервера без пробелов и '|' (лучше вообще все знаки менять на '_')
        :return:
        """
        self._cursor.execute("""
                                CREATE TABLE IF NOT EXISTS marriage_{}
                                (
                                Dis_ID              BIGINT UNIQUE NOT NULL,
                                spouse              BIGINT DEFAULT NULL,
                                date_of_marriage    TEXT,
                                marriage_history    TEXT,
                                marriage_count      INT DEFAULT 0,
                                sex_count           INT DEFAULT 0,
                                sex_history         TEXT
                                )
                            """.format(server_name)
                             )
        self._connection.commit()
        return True

    def get_accounts(self, table: str) -> Iterable:
        """
        Получение записей о балансе игровой валюты всех пользователей
        :param table: имя таблицы (название сервера)
        :return: Итерируемый объект содержащий все записи о пользователях
        """
        self._cursor.execute(f'SELECT * FROM {table}')

        for row in self._cursor:
            yield self.__extract_object(row)

    def get_marriage_accounts(self, table: str) -> Iterable:
        """
        Получение записей о всех "браках" пользователей
        :param table: имя таблицы (название сервера)
        :return: Итерируемый объект содержащий все записи о текущих браках пользователей
        """
        self._cursor.execute(f'SELECT * FROM {table}')

        for row in self._cursor:
            yield self.__extract_marriage_object(row)

    def get_account(self, table: str, user_id: int) -> dict:
        """
        Получение записи о балансе игровой валюты выбранного пользователя
        :param table: имя таблицы (название сервера)
        :param user_id: айди пользователя
        :return: запись о пользователе в виде словаря
        """
        self._cursor.execute(f'SELECT * FROM {table} WHERE Dis_ID={user_id}')
        return self.__extract_object(self._cursor.fetchone())

    def get_any_account(self, table: str) -> dict:
        """
        Получение данных о балансе игровой валюты случайного пользователя
        :param table: имя таблицы (название сервера)
        :return: запись о пользователе в виде словаря
        """
        self._cursor.execute(f'SELECT * FROM {table} ORDER BY RANDOM() LIMIT 1')
        return self.__extract_object(self._cursor.fetchone())

    def get_marriage_account(self, table: str, discord_id: int) -> dict:
        """
        Получение данных о браках выбранного пользователя
        :param table: имя таблицы (название сервера)
        :param discord_id: айди пользователя
        :return: запись о пользователе в виде словаря
        """
        self._cursor.execute(f'SELECT * FROM {table} WHERE Dis_ID={discord_id}')
        return self.__extract_marriage_object(self._cursor.fetchone())

    def _create_marriage_account(self, table: str, discord_id: int) -> True or None:
        """
        Создание записи о браках пользователя
        :param table: имя таблицы (название сервера)
        :param discord_id: айди пользователя
        :return: True or None
        """
        self._cursor.execute("INSERT INTO {} (Dis_ID) VALUES({})".format(f'marriage_{table}', discord_id))
        self._connection.commit()
        return True

    def divorce(self, table: str, discord_id: int) -> True or None:
        """
        Удаление брака у пользователя
        :param table: имя таблицы (название сервера)
        :param discord_id: айди пользователя
        :return: True or None
        """
        self._cursor.execute(
            """
            UPDATE {}
            SET spouse = {}, date_of_marriage = {}
            WHERE Dis_ID={}
            """.format(f'marriage_{table}', 'NULL', 'NULL', discord_id)
        )
        self._connection.commit()
        return True

    @bot_logging
    def set_marriage_account(self, table, discord_id: int, spouse: int) -> True or None:
        """
        Создание записи о "браке" пользователя и добавление нового брака в историю
        :param table: Имя базы данных (название сервера)
        :param discord_id: айди пользователя
        :param spouse: айди "супруга" пользователя
        :return: True or None
        """
        date = datetime.date.today()
        date = f'{date.year}:{date.month}:{date.day}'
        old_data = self.get_marriage_account(f'marriage_{table}', discord_id)
        if old_data is None:
            self._create_marriage_account(table, discord_id)
            history = f'{str(date)}_{spouse} '
            count = 1
        else:
            try:
                history = old_data['marriage_history'] + f'{str(date)}_{spouse} '
                count = int(old_data['marriage_count']) + 1
            except (AttributeError, TypeError):
                history = f'{str(date)}_{spouse} '
                count = 1
        self._cursor.execute(
            """
            UPDATE {}
            SET spouse = {}, date_of_marriage = '{}', marriage_history = '{}', marriage_count = {}
            WHERE Dis_ID={}
            """.format(f'marriage_{table}', spouse, date, history, count, discord_id)
        )
        self._connection.commit()
        return True

    @bot_logging
    def set_sex_in_marriage_account(self, table, discord_id: int, sex_partner: int) -> True or None:
        """
        Всё аналогично бракам, только без дат, зато со счётчиком
        """
        old_data = self.get_marriage_account(f'marriage_{table}', discord_id)
        if old_data is None:
            self._cursor.execute("INSERT INTO {} (Dis_ID) VALUES({})".format(f'marriage_{table}', discord_id))
            self._connection.commit()
            new_history = f'{sex_partner}:1 '
            count = 1
        else:
            new_history = ''
            try:
                history = old_data['sex_history'].split()
                his_dict = {}
                for partner in history:
                    his_dict[int(partner.split(':')[0])] = int(partner.split(':')[1])
                try:
                    his_dict[sex_partner] += 1
                except KeyError:
                    his_dict[sex_partner] = 1
                for key, value in his_dict.items():
                    new_history += f'{key}:{value} '
            except AttributeError:
                new_history = f'{sex_partner}:1 '
            count = int(old_data['sex_count']) + 1
        self._cursor.execute(
            """
            UPDATE  {}
            SET     sex_history = '{}', sex_count = {}
            WHERE   Dis_ID={}
            """.format(f'marriage_{table}', new_history, count, discord_id)
        )
        self._connection.commit()
        return True

    @staticmethod
    def __extract_object(row: list) -> dict:
        """
        Преобразование списка полученного из базы данных в словарь
        для обращения к данным по ключам
        :param row: список с данными о балансе и "опыте" пользователя
        :return: словарь в котором данные именованы либо None если данных нет
        """
        return {
            'discord_id': row[0],
            'steam_id': row[1],
            't_coins': row[2],
            't_coins_history': row[3],
        } if row else None

    @staticmethod
    def __extract_marriage_object(row: list) -> dict or None:
        """
        Преобразование списка полученного из базы данных в словарь
        для обращения к данным по ключам
        :param row: список с данными о "браках" пользователя
        :return: словарь в котором данные именованы либо None если данных нет
        """
        return {
            'discord_id': row[0],
            'spouse': row[1],
            'date_of_marriage': row[2],
            'marriage_history': row[3],
            'marriage_count': row[4],
            'sex_count': row[5],
            'sex_history': row[6]
        } if row else None

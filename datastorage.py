import sqlite3

from abc import abstractmethod, ABC
from typing import Iterable
import datetime
from decorators import bot_logging


class DataStorage(object):
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
    def __init__(self, collection: str):
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
        for N in range(1, 5, 1):
            self._cursor.execute("""
                                    CREATE TABLE IF NOT EXISTS Slot_{} 
                                    (
                                        Steam_ID                      BIGINT  PRIMARY KEY,
                                        CharacterClass                TEXT,
                                        Location_Thenyaw_Island       TEXT,
                                        Rotation_Thenyaw_Island       TEXT,
                                        Growth                        TEXT,
                                        Hunger                        TEXT,
                                        Thirst                        TEXT,
                                        Stamina                       TEXT,
                                        Health                        TEXT,
                                        BleedingRate                  TEXT,
                                        Oxygen                        TEXT,
                                        bGender                       BOOLEAN,
                                        bIsResting                    BOOLEAN,
                                        bBrokenLegs                   BOOLEAN,
                                        ProgressionPoints             TEXT,
                                        ProgressionTier               TEXT,
                                        UnlockedCharacters            TEXT,
                                        CameraRotation_Thenyaw_Island TEXT,
                                        CameraDistance_Thenyaw_Island TEXT,
                                        SkinPaletteSection1           INT,
                                        SkinPaletteSection2           INT,
                                        SkinPaletteSection3           INT,
                                        SkinPaletteSection4           INT,
                                        SkinPaletteSection5           INT,
                                        SkinPaletteSection6           INT,
                                        SkinPaletteVariation          TEXT
                                    )
                                """.format(N)
                                 )

    @bot_logging
    def create_account(self, table: str, user_id: int) -> True or None:
        print("Создаю запись об игроке:", user_id)
        self._cursor.execute("INSERT INTO {} (Dis_ID) VALUES({})".format(table, user_id))
        self._connection.commit()
        return True

    @bot_logging
    def set_balance(self, table: str, user_id, coins: int, coins_history: int) -> True or None:
        print("Пытаюсь внести изменения")
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
        print('Создаю таблицу браков', server_name)
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
        self._cursor.execute(f'SELECT * FROM {table}')

        for row in self._cursor:
            yield self.__extract_object(row)

    def get_marriage_accounts(self, table: str) -> Iterable:
        self._cursor.execute(f'SELECT * FROM {table}')

        for row in self._cursor:
            yield self.__extract_marriage_object(row)

    def get_account(self, table: str, user_id: int) -> dict:
        self._cursor.execute(f'SELECT * FROM {table} WHERE Dis_ID={user_id}')
        return self.__extract_object(self._cursor.fetchone())

    def get_any_account(self, table: str) -> dict:
        self._cursor.execute(f'SELECT * FROM {table} ORDER BY RANDOM() LIMIT 1')
        return self.__extract_object(self._cursor.fetchone())

    def get_marriage_account(self, table: str, discord_id: int) -> dict:
        self._cursor.execute(f'SELECT * FROM {table} WHERE Dis_ID={discord_id}')
        return self.__extract_marriage_object(self._cursor.fetchone())

    def _create_marriage_account(self, table: str, discord_id: int) -> True or None:
        self._cursor.execute("INSERT INTO {} (Dis_ID) VALUES({})".format(f'marriage_{table}', discord_id))
        self._connection.commit()
        return True

    def divorce(self, table: str, discord_id: int) -> True or None:
        self._cursor.execute(
            """
            UPDATE {}
            SET spouse = {}, date_of_marriage = {}
            WHERE Dis_ID={}
            """.format(f'marriage_{table}', 'NULL', 'NULL', discord_id)
        )
        self._connection.commit()
        return True

    # @bot_logging
    def set_marriage_account(self, table, discord_id: int, spouse: int) -> True or None:
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

    # @bot_logging
    def set_sex_in_marriage_account(self, table, discord_id: int, sex_partner: int) -> True or None:
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
        return {
            'discord_id': row[0],
            'steam_id': row[1],
            't_coins': row[2],
            't_coins_history': row[3],
        } if row else None

    @staticmethod
    def __extract_marriage_object(row: list) -> dict:
        return {
            'discord_id': row[0],
            'spouse': row[1],
            'date_of_marriage': row[2],
            'marriage_history': row[3],
            'marriage_count': row[4],
            'sex_count': row[5],
            'sex_history': row[6]
        } if row else None


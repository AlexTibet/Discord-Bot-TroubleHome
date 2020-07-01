import sqlite3

from abc import abstractmethod, ABC
from typing import Iterable
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

    def get_accounts(self, table: str) -> Iterable:
        self._cursor.execute(f'SELECT * FROM {table}')

        for row in self._cursor:
            yield self.__extract_object(row)

    def get_account(self, table: str, user_id: int) -> dict:
        self._cursor.execute(f'SELECT * FROM {table} WHERE Dis_ID={user_id}')
        return self.__extract_object(self._cursor.fetchone())

    def get_any_account(self, table: str) -> dict:
        self._cursor.execute(f'SELECT * FROM {table} ORDER BY RANDOM() LIMIT 1')
        return self.__extract_object(self._cursor.fetchone())

    @staticmethod
    def __extract_object(row: list) -> dict:
        return {
            'discord_id': row[0],
            'steam_id': row[1],
            't_coins': row[2],
            't_coins_history': row[3],
        } if row else None


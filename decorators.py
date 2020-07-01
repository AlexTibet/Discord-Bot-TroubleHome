import datetime


def bot_logging(fn):
    """Логирует работу с базой данных (создание и изменение записей)"""
    def wrapper(*args, **kwargs):
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

import requests
import config


async def bermuda_server_info():
    session = requests.Session()
    data = {
        'action': 'signin',
        'email': config.login,
        'password': config.password
    }
    auth = session.post(config.auth, data)
    bermuda_info = session.post(config.bermuda_info, data={'ugid': config.bermuda_port})
    if bermuda_info.status_code == 200:
        return bermuda_info.json()
    else:
        return None


def bermuda_test_server_info():
    session = requests.Session()
    data = {
        'email': config.g_portal_login,
        'password': config.g_portal_password
    }
    session.post(config.auth_test_server, data)
    bermuda_info = session.get(config.bermuda_test_server_info)
    if bermuda_info.status_code == 200:
        print(bermuda_info)
        return bermuda_info.json()
    else:
        return None


def bermuda_test_server_start():
    session = requests.Session()
    data = {
        'email': config.g_portal_login,
        'password': config.g_portal_password
    }
    auth = session.post(config.auth_test_server, data)
    cookies = {}
    for el in auth.cookies.items():
        cookies[el[0]] = el[1]
    print(auth)
    print(auth.cookies)
    print(cookies)
    bermuda_start = session.get(config.bermuda_test_server_start, cookies=cookies)
    print(bermuda_start)
    if bermuda_start.status_code == 200:
        print(bermuda_start)
        return bermuda_start.json()
    else:
        print(bermuda_start)
        return None


if __name__ == '__main__':
    otvet = bermuda_test_server_info()
    print(otvet)
    print(otvet['online'])
    start = bermuda_test_server_start()
    print(start)

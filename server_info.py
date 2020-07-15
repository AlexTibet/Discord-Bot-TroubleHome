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

import random
import game_config


async def bite_logic(message: str) -> (str, str, str):
    victim = message[1].replace('<', '').replace('!', '').replace('@', '').replace('>', '').replace(',', '')
    targets = random.choice(game_config.TARGET)
    gif_id = targets[1]
    target = targets[0]
    return target, victim, gif_id


async def shipper_logic(message: str) -> (str, str, str, str):
    victim_one = message[1]
    victim_two = message[2]
    compatibility = [i for i in range(101)]
    random.shuffle(compatibility)
    compatibility = random.choice(compatibility)
    title = None
    if compatibility <= 20:
        title = 'Ну такое...'
    elif 20 < compatibility < 50:
        title = 'Могут попробовать'
    elif 50 <= compatibility < 70:
        title = 'Хорошая пара'
    elif 70 <= compatibility <= 85:
        title = 'Отличная пара'
    elif 85 < compatibility <= 95:
        title = 'Идеальная пара'
    elif compatibility > 95:
        title = 'Созданы друг для друга!'
    return victim_one, victim_two, compatibility, title

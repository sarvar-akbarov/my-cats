
def type_buttons():
    return [
        [
            InlineKeyboardButton('Image', callback_data='types-jpg*png')
        ],
        [
            InlineKeyboardButton('Gif', callback_data='types-gif')
        ],
    ]

def get_breeds(breed=''):
    if os.path.isfile('datas/breeds.json'):
        with open('datas/breeds.json') as f:
            data = json.load(f)
    else:
        response = requests.get(
            url='https://api.thecatapi.com/v1/breeds', 
            headers={'x-api-key': API_KEY}
        )
        with open('datas/breeds.json', 'wb') as outf:
            outf.write(response.content)
        data = response.json()

    if breed == '':
        return data[0:2]
    else:
        breed = list(filter(lambda elem: elem['id'] == breed, data))[0]
        return breed

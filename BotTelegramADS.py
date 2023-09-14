from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup
import requests
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import json

bot = Bot(token='YOUR_TELEGRAM_BOT_TOKEN')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

keyboard1 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add("/create")

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    chat_id = message.chat.id
    # rinizializziamo le variabili
    global name
    name = ""
    global description
    description = ""
    await bot.send_message(chat_id=chat_id, text='Hi i\'m the chat bot for create ads🤖:')
    await bot.send_message(chat_id=chat_id, text='Click on the button to create a new ad.', reply_markup=keyboard1)

@dp.message_handler(commands=['stop'])
async def stop(message: types.Message):
    chat_id = message.chat.id
    global name
    name = ""
    global description
    description = ""
    await bot.send_message(chat_id=chat_id, text='Thank you for using me, if you want to create an ad press the button', reply_markup=keyboard1)
    await bot.send_message(chat_id=chat_id, text='Goodbye👋👋👋', reply_markup=keyboard1)

@dp.message_handler(commands=['create'])
async def create(message: types.Message):
    chat_id = message.chat.id

    await bot.send_message(chat_id=chat_id, text='Let\'s start, answer these questions with "𝓝𝓪𝓶𝓮𝓞𝓯𝓠𝓾𝓮𝓼𝓽𝓲𝓸𝓷: answer."')
    await bot.send_message(chat_id=chat_id, text='Remember: you can stop whenever you want by typing /stop 🛑')
    # Ask the first question
    await bot.send_message(chat_id=chat_id, text='𝓝𝓪𝓶𝓮: What\'s the name of your product?')

@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text(message: types.Message):
    global name
    global description
    chat_id = message.chat.id
    text = message.text
    if 'Name:' in message.text:
        await message.answer('Question 1 received. Now it\'s time for Question number 2.')
        name = text
        # Ask the second question
        await bot.send_message(chat_id=chat_id, text='𝓓𝓮𝓼𝓬𝓻𝓲𝓹𝓽𝓲𝓸𝓷: What\'s the description of your product?')
    elif 'Description:' in message.text:
        description = message.text
        await message.answer('Question 2 received!')
        await message.answer('Now please, send a photo of your product 📷:')
    else:
        await message.answer('Invalid response.')

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_image(message: types.Message):
    chat_id = message.chat.id
    photo = message.photo[-1].file_id

    # Get the image file
    file = await bot.get_file(photo)
    print(file)

     # Download the photo
    photo_path = f'photos/{chat_id}.jpg'
    await file.download(photo_path)

    global name
    global description
    # Upload the photo to ImgBB
    image_url = upload_image_to_imgbb(photo_path)

    # if image_url:
    #     # Reply to the user with the ImgBB URL
    #     await message.answer(f'Image uploaded successfully!\nImage URL: {image_url}')
    # else:
    #     await message.answer('Image upload failed!')

    photo_url = image_url

    card_message = f"<b>{name}</b>\n<i>{description}</i>"
    await bot.send_photo(chat_id=chat_id, photo=photo_url, caption=card_message, parse_mode="HTML")
    # post su api sito
    url = "https://socialccapi.azurewebsites.net/api/v1/AnnuncioAPI/CreaAnnuncio"

    # Request payload (data to be sent)
    payload = {
        "titolo": name,
        "descrizione": description,
        "media": image_url,
    }
    print(payload)
    json_string = json.dumps(payload)


    # Set the headers
    headers = {
        'Content-Type': 'application/json'
    }
    # Send POST request
    response = requests.post(url, data=json_string, headers=headers)

    # Check the response status code
    if response.status_code == 200:
        # Request was successful
        print("POST request successful")
        print("Response:", response.text)
    else:
        # Request failed
        print("POST request failed")
        print("Status code:", response.status_code)
        # Reply to the user
    await message.answer('Thanks for creating the ad')
    await message.answer('Press the button if you want to create another ad❗❗❗', reply_markup=keyboard1)


def upload_image_to_imgbb(image_path):
    # Prepare the POST request parameters
    payload = {
        'key': "YOUR_IMGBB_API_KEY",
    }
    files = {
        'image': open(image_path, 'rb'),
    }

    # Make the POST request to upload the image
    response = requests.post('https://api.imgbb.com/1/upload', payload, files=files)

    # Parse the JSON response
    json_data = response.json()
    image_url = json_data['data']['url']
    print(image_url)
    return image_url

async def main():
    await dp.start_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())


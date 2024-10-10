import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import FSInputFile, Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Токен вашего бота
API_TOKEN = '7707735615:AAGTv-6x0mrzo4wf8svUoJBPRNzCLA9r24Y'  # Замените на ваш токен

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Создаем объект бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Создаем объект роутера
router = Router()

# Определяем группу состояний
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

# Создаем основную клавиатуру с добавленной кнопкой "Купить"
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Рассчитать'), KeyboardButton(text='Информация')],
        [KeyboardButton(text='Купить')]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Создаем Inline-клавиатуру для расчета
inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories'),
         InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')]
    ]
)

# Создаем Inline меню для продуктов
products_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='CodliverOil', callback_data='product_buying'),
         InlineKeyboardButton(text='PapayaLeaf', callback_data='product_buying')],
        [InlineKeyboardButton(text='VitaminCOriginal', callback_data='product_buying'),
         InlineKeyboardButton(text='CranberryExtract', callback_data='product_buying')],
        [InlineKeyboardButton(text='Ginseng', callback_data='product_buying'),
         InlineKeyboardButton(text='SeleniumAdvanced', callback_data='product_buying')]
    ]
)

# Обработчик команды /start
@router.message(Command(commands=['start']))
async def start(message: Message):
    logging.info("Команда /start обработана")
    await message.answer('Привет! Я бот, помогающий твоему здоровью. Выберите действие:', reply_markup=keyboard)

# Обработчик нажатия кнопки "Рассчитать"
@router.message(lambda message: message.text == 'Рассчитать')
async def main_menu(message: Message):
    await message.answer('Выберите опцию:', reply_markup=inline_keyboard)

# Обработчик для получения формул
@router.callback_query(lambda call: call.data == 'formulas')
async def get_formulas(call):
    logging.info("Формулы расчета запрошены")
    await call.message.answer('Формула Миффлина-Сан Жеора: 10 * вес + 6.25 * рост - 5 * возраст + 5 (для мужчин).')
    await call.answer()

# Обработчик для расчета калорий
@router.callback_query(lambda call: call.data == 'calories')
async def set_age(call, state: FSMContext):
    await state.set_state(UserState.age)
    await call.message.answer('Введите свой возраст:')
    await call.answer()

# Обработчик возраста
@router.message(UserState.age)
async def set_growth(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(UserState.growth)
    await message.answer('Введите свой рост:')

# Обработчик роста
@router.message(UserState.growth)
async def set_weight(message: Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await state.set_state(UserState.weight)
    await message.answer('Введите свой вес:')

# Обработчик веса и расчет калорий
@router.message(UserState.weight)
async def send_calories(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    # Извлекаем данные
    age = int(data.get('age'))
    growth = int(data.get('growth'))
    weight = int(data.get('weight'))

    # Формула для расчета нормы калорий (для мужчин)
    calories = 10 * weight + 6.25 * growth - 5 * age + 5

    await message.answer(f'Ваша норма калорий: {calories} ккал в день.')
    await state.clear()

# Функция для отправки изображения или документа
async def send_file(message, file_path, file_name=None):
    try:
        # Создаем FSInputFile из пути
        file_input = FSInputFile(file_path, filename=file_name)
        await bot.send_document(chat_id=message.chat.id, document=file_input)
        logging.info(f"Файл отправлен: {file_path}")
    except FileNotFoundError:
        await message.answer(f"Файл {file_path} не найден.")
        logging.error(f"Файл не найден: {file_path}")
    except PermissionError:
        await message.answer(f"Нет прав доступа к файлу {file_path}.")
        logging.error(f"Нет прав доступа к файлу: {file_path}")
    except Exception as e:
        await message.answer(f"Произошла ошибка при отправке файла: {e}")
        logging.error(f"Ошибка при отправке файла {file_path}: {e}")

# Обработчик нажатия кнопки "Купить"
@router.message(lambda message: message.text == 'Купить')
async def get_buying_list(message: Message):
    image_paths = [
        'image1.jpeg',
        'image2.jpeg',
        'image3.jpeg',
        'image4.jpeg',
        'image5.jpeg',
        'image6.jpeg'
    ]

    for i, image_path in enumerate(image_paths):
        await message.answer(f'Название: Product{i + 1} | Описание: описание {i + 1} | Цена: {i * 100}')
        await send_file(message, image_path, file_name=f'Product{i + 1}.jpeg')

    await message.answer('Выберите продукт для покупки:', reply_markup=products_inline_keyboard)

# Обработчик нажатия на кнопку продукта
@router.callback_query(lambda call: call.data == 'product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()

# Обработчик всех остальных сообщений
@router.message()
async def all_messages(message: Message):
    await message.answer('Пожалуйста, используйте команду /start или нажмите кнопку "Рассчитать", чтобы продолжить.')

# Функция для правильного завершения работы бота
async def shutdown(dispatcher: Dispatcher):
    await bot.session.close()

# Основная функция
async def main():
    dp.include_router(router)
    try:
        await dp.start_polling(bot)
    finally:
        await shutdown(dp)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")

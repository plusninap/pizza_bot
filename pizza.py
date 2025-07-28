import telebot
from telebot import types

token = '7204196116:AAHErO_oWzq9ZdUTEJGVTHMRVHZwV0kranc'
bot = telebot.TeleBot(token)

# Устанавливаем команды бота
bot.set_my_commands([
    types.BotCommand("start", "Начать работу с ботом"),
    types.BotCommand("menu", "Посмотреть меню"),
    types.BotCommand("order", "Сделать заказ"),
    types.BotCommand("profile", "Профиль пользователя"),
    types.BotCommand("help", "Помощь"),
])

# Хранение данных о заказе (временное, для демонстрации)
user_orders = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    welcome_text = """
*Добро пожаловать в PizzaBot* 

Я помогу вам заказать вкуснейшую пиццу\\. Вот что я умею:

/menu \\- Посмотреть меню
/order \\- Сделать заказ
/profile \\- Ваш профиль и история заказов
/help \\- Помощь по использованию бота

Выберите действие или просто начните заказ
"""
    bot.send_message(message.chat.id, welcome_text, parse_mode="MarkdownV2")

@bot.message_handler(commands=['help'])
def help_message(message):
    help_text = """
*Как пользоваться ботом:*

1\\. Нажмите /menu чтобы посмотреть доступные пиццы
2\\. Выберите понравившуюся пиццу
3\\. Укажите размер и адрес доставки
4\\. Подтвердите заказ

Вы можете в любой момент отменить заказ или изменить данные\\.

Команды:
/menu \\- показать меню
/order \\- начать новый заказ
/profile \\- ваш профиль и история заказов
"""
    bot.send_message(message.chat.id, help_text, parse_mode="MarkdownV2")

@bot.message_handler(commands=['menu'])
def show_menu(message):
    keyboard = types.InlineKeyboardMarkup()
    
    btn_margherita = types.InlineKeyboardButton("Маргарита", callback_data="pizza_margherita")
    btn_pepperoni = types.InlineKeyboardButton("Пепперони", callback_data="pizza_pepperoni")
    btn_vegetarian = types.InlineKeyboardButton("Вегетарианская", callback_data="pizza_vegetarian")
    
    keyboard.add(btn_margherita, btn_pepperoni)
    keyboard.add(btn_vegetarian)
    
    bot.send_message(message.chat.id, "*Наше меню:*\nВыберите пиццу:", parse_mode="MarkdownV2", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('pizza_'))
def handle_pizza_selection(call):
    pizza_type = call.data.split('_')[1]
    
    if pizza_type == "margherita":
        description = "Классическая пицца с томатным соусом, сыром моцарелла и базиликом"
        price = "от 350₽"
    elif pizza_type == "pepperoni":
        description = "Острая пицца с пепперони и сыром моцарелла"
        price = "от 400₽"
    elif pizza_type == "vegetarian":
        description = "Пицца с овощами: перец, грибы, маслины и сыр моцарелла"
        price = "от 380₽"
    else:
        description = "Описание отсутствует"
        price = "уточняйте"
    
    keyboard = types.InlineKeyboardMarkup()
    btn_order = types.InlineKeyboardButton("Заказать", callback_data=f"order_{pizza_type}")
    btn_back = types.InlineKeyboardButton("Назад в меню", callback_data="back_to_menu")
    
    keyboard.add(btn_order)
    keyboard.add(btn_back)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"*{pizza_type.capitalize()}*\n\n{description}\n\nЦена: {price}",
        parse_mode="MarkdownV2",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
def handle_back_to_menu(call):
    show_menu(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('order_'))
def start_order(call):
    pizza_type = call.data.split('_')[1]
    user_orders[call.from_user.id] = {"pizza": pizza_type}
    
    keyboard = types.InlineKeyboardMarkup()
    btn_small = types.InlineKeyboardButton("Маленькая (25см)", callback_data="size_small")
    btn_medium = types.InlineKeyboardButton("Средняя (30см)", callback_data="size_medium")
    btn_large = types.InlineKeyboardButton("Большая (35см)", callback_data="size_large")
    
    keyboard.add(btn_small, btn_medium, btn_large)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Вы выбрали: {pizza_type.capitalize()}\n\nТеперь выберите размер:",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('size_'))
def handle_size_selection(call):
    size = call.data.split('_')[1]
    user_orders[call.from_user.id]["size"] = size
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Отлично! Теперь отправьте мне ваш адрес доставки текстовым сообщением."
    )

@bot.message_handler(func=lambda message: message.from_user.id in user_orders and "size" in user_orders[message.from_user.id] and "address" not in user_orders[message.from_user.id])
def handle_address(message):
    user_orders[message.from_user.id]["address"] = message.text
    
    keyboard = types.InlineKeyboardMarkup()
    btn_confirm = types.InlineKeyboardButton("Подтвердить заказ", callback_data="confirm_order")
    btn_cancel = types.InlineKeyboardButton("Отменить заказ", callback_data="cancel_order")
    
    keyboard.add(btn_confirm, btn_cancel)
    
    order = user_orders[message.from_user.id]
    bot.send_message(
        message.chat.id,
        f"*Ваш заказ:*\n\nПицца: {order['pizza'].capitalize()}\nРазмер: {order['size']}\nАдрес: {order['address']}\n\nПодтверждаете заказ?",
        parse_mode="MarkdownV2",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "confirm_order")
def handle_confirm_order(call):
    if call.from_user.id in user_orders:
        order = user_orders[call.from_user.id]
        
        # Здесь можно добавить сохранение заказа в базу данных
        order_details = f"""
*Заказ подтвержден* 

Ваш заказ:
Пицца: {order['pizza'].capitalize()}
Размер: {order['size']}
Адрес: {order['address']}

Примерное время доставки: 30\\-45 минут
"""
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=order_details,
            parse_mode="MarkdownV2"
        )
        
        # Удаляем временные данные заказа
        del user_orders[call.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "cancel_order")
def handle_cancel_order(call):
    if call.from_user.id in user_orders:
        del user_orders[call.from_user.id]
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Заказ отменен. Вы можете начать заново с команды /menu"
    )

@bot.message_handler(commands=['profile'])
def show_profile(message):
    user = message.from_user
    profile_text = f"""
*Профиль пользователя*  
Имя: {user.first_name}  
Username: @{user.username if user.username else 'N/A'}  

Ваши последние заказы:
\\- Пока нет истории заказов
"""
    
    keyboard = types.InlineKeyboardMarkup()
    btn_orders = types.InlineKeyboardButton("Мои заказы", callback_data="show_orders")
    btn_close = types.InlineKeyboardButton("Закрыть", callback_data="close_profile")
    
    keyboard.add(btn_orders, btn_close)
    
    bot.send_message(
        message.chat.id,
        profile_text,
        parse_mode="MarkdownV2",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "show_orders")
def handle_show_orders(call):
    bot.answer_callback_query(call.id, "У вас пока нет истории заказов", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "close_profile")
def handle_close_profile(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.message_handler(commands=['order'])
def start_order_command(message):
    show_menu(message)

bot.infinity_polling()
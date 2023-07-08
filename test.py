import os
import telebot
import time

users = {}
class User:
    def __init__(self, chat_id, first_name, last_name,username):
        self.chat_id = chat_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username

bot = telebot.TeleBot( "6324861862:AAFvCIXbYhsjGtzNeG9s49z6sVFZFCXUjsE" ) 
bot.set_my_commands(commands=[telebot.types.BotCommand('/start','s'),telebot.types.BotCommand('/hello','h'),telebot.types.BotCommand('/addplayer','h')])
@bot.message_handler(commands=['start'])
def send_welcome(message):
    firstreply = bot.reply_to(message, "bot started your username has been added to the data base")
    users["@"+message.from_user.username] = User(message.from_user.id,message.from_user.first_name,message.from_user.last_name,message.from_user.username)
    print (users)

    ##bot.reply_to(firstreply, "isnt this intresting not realy i need to die")
    ##bot.send_photo(message.from_user.id,photo=open('3d4.jpg','rb'))
    ##bot.send_document(message.from_user.id,document=open('3d4.jpg','rb'))

@bot.message_handler(commands=['addplayer'])
def get_username_to_invite(message):
    username_message = bot.send_message(message.from_user.id,"Please send your friend username")
    bot.register_next_step_handler(username_message ,send_invite)
def send_invite(message):
    yes_bottom = telebot.types.InlineKeyboardButton("answer",callback_data="True")
    no_bottom = telebot.types.InlineKeyboardButton("reject",callback_data="False")
    m = telebot.types.InlineKeyboardMarkup()
    m.add(yes_bottom)
    m.add(no_bottom)
    
    bot.send_message(users.get(message.text).chat_id,"usre @"+message.from_user.username+" has invited you to chat"
                     ,reply_markup= m,parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if(call.data == "True"):
        sender = call.from_user 
        bot.delete_message(call.message.chat.id,call.message.message_id)
        users_keyboard_in_chat = telebot.types.ReplyKeyboardMarkup(one_time_keyboard= False)
        end_chat_bottom = telebot.types.KeyboardButton(text= "end connection")
        users_keyboard_in_chat.add(telebot.types.KeyboardButton(text= "1"))
        users_keyboard_in_chat.add(telebot.types.KeyboardButton(text= "2"))
        users_keyboard_in_chat.add(telebot.types.KeyboardButton(text= "3"))
        users_keyboard_in_chat.add(telebot.types.KeyboardButton(text= "4"))

        users_keyboard_in_chat.add(end_chat_bottom)
        startchat_message_user1 = bot.send_message(sender.id,"you are chatting with " +call.message.text[5:][:-24]+ " ...",reply_markup=users_keyboard_in_chat)
        startchat_message_user2 = bot.send_message(users.get(call.message.text[5:][:-24]).chat_id,"you are chatting with @" +sender.username+ " ...",reply_markup=users_keyboard_in_chat)
        bot.register_next_step_handler(startchat_message_user1 ,chattin_1_on_1 , user1 = users.get(call.message.text[5:][:-24]).chat_id ,user2 = sender.id)
        bot.register_next_step_handler(startchat_message_user2 ,chattin_1_on_1 , user1 = sender.id ,user2 = users.get(call.message.text[5:][:-24]).chat_id)
        
    if(call.data == "False"):
        sender = call.from_user 
        bot.delete_message(call.message.chat.id,call.message.message_id)
        startchat_message_user2 = bot.send_message(users.get(call.message.text[5:][:-24]).chat_id,"@" +sender.username+ " rejected your love")
def chattin_1_on_1 (message:telebot.types.Message,user1 , user2 ) :
        #print("message : "+message.text+ " user = "+message.from_user.username)
        m = bot.send_message(user1 ,text = message.text)
        bot.register_next_step_handler(message,chattin_1_on_1,user1 = user1 , user2 = user2)




@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)
    

# while True:
#     try:
#         bot.polling(none_stop=True, interval=0, timeout=0)
#     except:
#         time.sleep(10)

bot.infinity_polling()
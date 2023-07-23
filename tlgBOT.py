import os
import telebot
from mypoker import NL_Holdem,Poker_Table,Player,User
import time
import json
import string
import random
import sqlite3

private_tables = {}
users = {}

if __name__ == '__main__':
    bot = telebot.TeleBot( "6324861862:AAFvCIXbYhsjGtzNeG9s49z6sVFZFCXUjsE" ) 
    bot.set_my_commands(commands=[telebot.types.BotCommand('/start','s'),telebot.types.BotCommand('/hello','h'),telebot.types.BotCommand('/addplayer','h'),
                              telebot.types.BotCommand('/create_private_table','Create Private Table')])
    users_db = sqlite3.connect('users.db')
    cursor = users_db.cursor()
    #cursor.execute('''CREATE TABLE mytable (id INTEGER PRIMARY KEY,chat_id INTEGER, first_name TEXT, last_name TEXT, username TEXT, nickname TEXT)''')
    cursor.execute("SELECT * FROM mytable")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    users_db.commit()
    users_db.close()


def nickname_handler(nickname,message):
    users[message.from_user.id] = User(message.chat.id,message.from_user.first_name,message.from_user.last_name,message.from_user.username,message.from_user.id,nickname.text)
    users_db1 = sqlite3.connect('users.db')
    cursor1 = users_db1.cursor()
    cursor1.execute("INSERT INTO mytable (id, chat_id, first_name, last_name, username, nickname) VALUES (?, ?, ?, ?, ?, ?)",
                    ((message.from_user.id, message.chat.id,message.from_user.first_name,message.from_user.last_name,message.from_user.username,nickname.text)))
    users_db1.commit()
    users_db1.close()

    bot.reply_to(nickname,"welcome :)")
def select_table_handler(table_number,poker_table,user):
    buy_in_message = bot.send_message(user.id,"buy in :"+str(poker_table.buy_in_min)+" - "+str(poker_table.buy_in_max)+
                                          "\nyour balance : "+str(user.balance))
    bot.register_next_step_handler(buy_in_message,buy_in_handler,table_number,poker_table,user)
def buy_in_handler(amount,table_number,poker_table,user):
    if(int(amount.text)<=user.balance and int(amount.text)>= poker_table.buy_in_min):
        p = Player(user)
        poker_table.game.add_player(int(table_number.text)-1,int(amount.text),p)
        user.balance -= int(amount.text)
        joined_message = bot.send_message(user.id,"joined succusfully!\nyour table stack : "+amount.text+
                                        "\nyour balance :"+str(user.balance))
    elif(int(amount.text) < poker_table.buy_in_min):
        bot.send_message(user.id,"not enough to buy-in")
    else:
        bot.send_message(user.id,"insuficent balance")

def test_hello(update):
    print(update)
    data = json.loads(update.message.web_app_data.data)
    for result in data:
        print(f"{result['name']}: {result['value']}")

@bot.message_handler(commands=['hello'])
def test_fun(message):
    k =telebot.types.KeyboardButton("show me gooodlle",web_app=telebot.types.WebAppInfo("https://calixtemayoraz.gitlab.io/web-interfacer-bot/"))
        
    m =telebot.types.ReplyKeyboardMarkup()
    m.add(k)
    mm =bot.send_message(message.from_user.id,"heey",reply_markup=m)
    bot.register_callback_query_handler(mm,test_hello)
    bot.re
    #bot.send_message(message.from_user.id,"┌─────────┐\n│1        │\n│         │\n│         │\n│    1    │\n│         │\n│         │\n│        1│\n└─────────┘")
    # bot.send_sticker(message.from_user.id,"CAACAgUAAxkBAAEjhopkrPqtrFu47EKa4aA2Zrf7tAAB4iYAAogBAAJa9cBVw84sUD1gdGsvBA")
    # bot.send_photo(message.from_user.id,"AgACAgQAAxkBAAEjhwlkrQZjNfczYWEyR89VVLZ7qRQOZQACHL0xGyEqaVGoRTUf_MxVhQEAAwIAA3gAAy8E")
    # bot.send_media_group(message.from_user.id,[telebot.types.InputMediaPhoto("AgACAgQAAxkBAAEjhu1krQP9nRaYtihJIeO8Zgx6gqULAAMYvDEbQHdpURYjJ4vomcC5AQADAgADeAADLwQ"),
    #                                            telebot.types.InputMediaPhoto("AgACAgQAAxkBAAEjhu1krQP9nRaYtihJIeO8Zgx6gqULAAMYvDEbQHdpURYjJ4vomcC5AQADAgADeAADLwQ"),
    #                                            telebot.types.InputMediaPhoto("AgACAgQAAxkBAAEjhu1krQP9nRaYtihJIeO8Zgx6gqULAAMYvDEbQHdpURYjJ4vomcC5AQADAgADeAADLwQ"),
    #                                            telebot.types.InputMediaPhoto("AgACAgQAAxkBAAEjhu1krQP9nRaYtihJIeO8Zgx6gqULAAMYvDEbQHdpURYjJ4vomcC5AQADAgADeAADLwQ"),
    #                                            telebot.types.InputMediaPhoto("AgACAgQAAxkBAAEjhu1krQP9nRaYtihJIeO8Zgx6gqULAAMYvDEbQHdpURYjJ4vomcC5AQADAgADeAADLwQ")],protect_content=True)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if (message.text == "/start"):
        if (None == users.get(message.from_user.id)):
            nick_name_request = bot.reply_to(message, "choose a nickname for yourself")
            bot.register_next_step_handler(nick_name_request ,nickname_handler,message)
        else:
            firstreply = bot.reply_to(message, "hey "+users[message.from_user.id].nickname+" what can i do?")
    if(message.text.startswith("/start pt")):
        key = message.text[10:]
        poker_table = private_tables[key]
        select_tabale_message = bot.send_message(message.from_user.id,"Choose one of the empty tables"+str(poker_table.game.empty_tables_list()))
        if (None == users.get(message.from_user.id)):
            nick_name_request = bot.reply_to(message, "register first")
            return
        else:
            bot.register_next_step_handler(select_tabale_message ,select_table_handler,poker_table,users[message.from_user.id])



    # print(message.text)
    # firstreply = bot.reply_to(message, "bot started your username has been added to the data base")
    # users["@"+message.from_user.username] = User(message.from_user.id,message.from_user.first_name,message.from_user.last_name,message.from_user.username)
    # print (users)

    ##bot.reply_to(firstreply, "isnt this intresting not realy i need to die")
    ##bot.send_photo(message.from_user.id,photo=open('3d4.jpg','rb'))
    ##bot.send_document(message.from_user.id,document=open('3d4.jpg','rb'))

@bot.message_handler(commands=['create_private_table'])
def send_welcome(message):
    nl_holdem = telebot.types.InlineKeyboardButton("Texas Hold'em",callback_data="NL_Holdem")
    omaha = telebot.types.InlineKeyboardButton("Omaha",callback_data="Omaha")
    stud = telebot.types.InlineKeyboardButton("Stud",callback_data="Stud")
    m = telebot.types.InlineKeyboardMarkup()
    m.add(nl_holdem)
    m.add(omaha)
    m.add(stud)
    firstreply = bot.reply_to(message, "select game mode",reply_markup= m,parse_mode='HTML')
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


def big_blind_message_handler(amount,game_mode,num_players,sender,big_blind_message):
    bot.delete_message(big_blind_message.chat.id,big_blind_message.message_id)
    bot.delete_message(amount.chat.id,amount.message_id)
    table_created_message = bot.send_message(sender.id,"Game mode : "+game_mode+"\nPlayers : "+str(num_players)+"\nBig-Blinds : "+amount.text+
                                             "\nBuy-in :  "+str(int(amount.text)*20)+" to "+str(int(amount.text)*100))
    link_created_message = bot.send_message(sender.id,"share the link below to invite your friends to this private table")
    key = ''.join(random.choice(string.ascii_uppercase + string.digits+string.ascii_lowercase) for _ in range(14))
    if(None == private_tables.get(key)):
        pv_tb = Poker_Table(key,bot,number_tables = num_players,stack_size_bb=int(amount.text))
        private_tables[key] = pv_tb
    else:
        while(None != private_tables.get(key)):
            key=''.join(random.choice(string.ascii_uppercase + string.digits+string.ascii_lowercase) for _ in range(14))
        pv_tb = Poker_Table(key,bot,num_players,int(amount.text))
        private_tables[key] = pv_tb
    link_created_message = bot.send_message(sender.id,"https://telegram.me/HRM_TestBot?start=pt-"+key)
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if(call.data == "NL_Holdem_8"):
        sender = call.from_user 
        bot.delete_message(call.message.chat.id,call.message.message_id)
        big_blind_message = bot.send_message(sender.id,"Game mode : Texas Hold'em\nPlayers : 8\nPlease enter the Big-Blind amount")
        bot.register_next_step_handler(big_blind_message ,big_blind_message_handler,"Texas Hold'em",8,sender,big_blind_message)
    if(call.data == "NL_Holdem_6"):
        sender = call.from_user 
        bot.delete_message(call.message.chat.id,call.message.message_id)
        big_blind_message = bot.send_message(sender.id,"Game mode : Texas Hold'em\nPlayers : 6\nPlease enter the Big-Blind amount")
        bot.register_next_step_handler(big_blind_message ,big_blind_message_handler,"Texas Hold'em",6,sender,big_blind_message)
    if(call.data == "NL_Holdem_4"):
        sender = call.from_user 
        bot.delete_message(call.message.chat.id,call.message.message_id)
        big_blind_message = bot.send_message(sender.id,"Game mode : Texas Hold'em\nPlayers : 4\nPlease enter the Big-Blind amount")
        bot.register_next_step_handler(big_blind_message ,big_blind_message_handler,"Texas Hold'em",4,sender,big_blind_message)
    if(call.data == "NL_Holdem_2"):
        sender = call.from_user 
        bot.delete_message(call.message.chat.id,call.message.message_id)
        big_blind_message = bot.send_message(sender.id,"Game mode : Texas Hold'em\nPlayers : 2\nPlease enter the Big-Blind amount")
        bot.register_next_step_handler(big_blind_message ,big_blind_message_handler,"Texas Hold'em",2,sender,big_blind_message)
    if(call.data == "NL_Holdem"):
        sender = call.from_user 
        bot.delete_message(call.message.chat.id,call.message.message_id)
        table_of_two_bottom = telebot.types.InlineKeyboardButton("2",callback_data="NL_Holdem_2")
        table_of_four_bottom = telebot.types.InlineKeyboardButton("4",callback_data="NL_Holdem_4")
        table_of_six_bottom = telebot.types.InlineKeyboardButton("6",callback_data="NL_Holdem_6")
        table_of_eight_bottom = telebot.types.InlineKeyboardButton("8",callback_data="NL_Holdem_8")
        m = telebot.types.InlineKeyboardMarkup()
        m.add(table_of_two_bottom)
        m.add(table_of_four_bottom)
        m.add(table_of_six_bottom)
        m.add(table_of_eight_bottom)
        game_mode_message = bot.send_message(sender.id,"Game mode : Texas hold'em\nselect number of players at table",reply_markup = m,parse_mode='HTML')
    if(call.data == "Omaha"):
        sender = call.from_user 
        game_mode_message = bot.send_message(sender.id,"Accese Denied")
    if(call.data == "Stud"):
        sender = call.from_user 
        game_mode_message = bot.send_message(sender.id,"Accese Denied")
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
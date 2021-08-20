
import logging
from telegram import Update, InlineKeyboardMarkup, ParseMode, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import pandas as pd
import os

from utils import custom_reply_handler

from user import update_chat_id, update_messages_logs, num_handler, music_thearpy, get_message, cbt_handler, doubt_issue
from user import logs, inline_keyboards

#from admin_expert import accept_request, delete_expert_acc, generate_all_doubts, get_queries, get_statistics, process_query, send_query_answer, validate_admin, admin, save_expert_request, expert_requests, experts_list, announcement, get_expert_request, accept_request, reject_request, get_expert_for_removing
from admin_expert import *



# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

TOKEN = "1732516218:AAHFSWoMwJ35ZcemIRZDgYlvU-8r5oHC8EM" #dummy


######   List of different label    ######
# Following list contains the total number of message labels which 
# just have callback query of numbers to be processed by single condition
# in option_selector method
num_handler_list = ["a", "b", "c", "e", "b1", "y", "w"]

# list of users who had initiated /become_expert command
become_expert_list = []

############   Initializing admin object    ##################
try:
    admin_object = None
    with open("Resources/admin/admin.txt", "r") as file:
        chat_id = int(file.readline())
        
        admin_object = admin(chat_id, "?WN34Az8p^wRURc5-k3!")
        
        logger.info(" Admin object initialized\n")
        logs[chat_id] = 'z'

except:
    admin_object = None
###############################################################

# Defining command handlers. 

##################### user commands ########################

def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    
    user = update.effective_user
    
    update.message.reply_markdown_v2(fr'Hi {user.mention_markdown_v2()}\!')
    update.message.reply_sticker("https://github.com/HarshMathur86/test-repo/blob/main/Bot_logo.webp?raw=true")
    update.message.reply_text("<b>I am a bot here to help you in different aspects of mental health and wellness</b>", parse_mode=ParseMode.HTML)
    update.message.reply_text("<b>Just click</b> - /services", parse_mode=ParseMode.HTML)
    
    update_chat_id(update.message.chat_id)
    update_messages_logs(update.message.chat_id, "z")
    
    logger.info(str(update.message.chat_id) + " - start command initiated")
  
def services(update: Update, _: CallbackContext):
    """Send a message of taking numerical option"""
    
    logger.info(str(update.message.chat_id) + " - services command initiated")

    update.message.reply_text(get_message("a"), parse_mode=ParseMode.HTML)
    update.message.reply_text("select respective option", reply_markup=InlineKeyboardMarkup(inline_keyboards["a"]))    

    update_messages_logs(update.message.chat_id, "a")

def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""

    logger.info(str(update.message.chat_id) + " - help command initiated")

    update.message.reply_text(get_message("help"), parse_mode=ParseMode.HTML)
    if admin_object != None and admin_object.check_chat_id(update.message.chat_id):
        update.message.reply_text(get_message("admin_help"), parse_mode=ParseMode.HTML)
    elif update.message.chat_id in experts_list:
        update.message.reply_text(get_message("expert_help"), parse_mode=ParseMode.HTML)

def contact(update: Update, _: CallbackContext):
    
    if update.message.chat_id in become_expert_list:
    
        logger.info(str(update.message.chat_id) + " - Contact recieved")
        if update.message.chat_id in expert_requests:
            update.message.reply_text("you already requested for expert. Please wait for approval by admin.")
            return
        bool, reply =  save_expert_request(update.message.chat_id, update.message.from_user.full_name, update.message.contact.phone_number)
        if bool == True:
            logger.info(str(update.message.chat_id) + " - User requested for expert")
            update.message.reply_text(reply)
            become_expert_list.remove(update.message.chat_id)

        else:
            update.message.reply_text(reply)
    
    else:
        update.message.reply_text("Please don't send contact.")

#####################  admin commands ########################

def admin_login(update: Update, _: CallbackContext):
    
    logger.info(" - admin_login command initiated")
    
    if admin.admin_created == True:
        update.message.reply_text("Sorry, command is not for you")        
        return

    update.message.reply_text("Enter the security key 🔑 to access administrative privileges")
    update_messages_logs(update.message.chat_id, "admin_login")
    
def accept_expert_request(update:Update, _: CallbackContext):
    if admin_object.check_chat_id(update.message.chat_id):
        
        logger.info(str(update.message.chat_id) + " - accept_expert_request command initiated")

        reply = get_expert_request()
        if str(reply) == 'False':
            update.message.reply_text("No requests found")
            return
        
        admin.admin_log = "a_expert"
        update.message.reply_text(reply, parse_mode=ParseMode.HTML)
        update.message.reply_text("select action to perform", reply_markup=InlineKeyboardMarkup(inline_keyboards["expert_req"]))

def remove_expert(update:Update, _: CallbackContext):
    if admin_object.check_chat_id(update.message.chat_id):
        
        logger.info(str(update.message.chat_id) + " - remove_expert command initiated")

        reply, keyboard = get_expert_for_removing()
        update.message.reply_text(reply, parse_mode=ParseMode.HTML)
        try:
            update.message.reply_text("Select the expert you want to remove", reply_markup=InlineKeyboardMarkup(keyboard))
            admin.admin_log = "r_expert"
        except:
            pass

def admin_logout(update:Update, _: CallbackContext):
    if admin_object.check_chat_id(update.message.chat_id):
        
        logger.info(str(update.message.chat_id) + " - admin_logout command initiated")

        admin.admin_log = "admin_logout"
        update.message.reply_text("Enter the security key 🔑 to logout as administrator")

def issues_reported(update:Update, _: CallbackContext):
    if admin_object.check_chat_id(update.message.chat_id):
        
        logger.info(str(update.message.chat_id) + " - issues_reported command initiated")

        df = pd.read_csv("Resources/Records/issues.csv")
        if df.shape[0] == 0:
            update.message.reply_text("<b>Sorry, currently no issues reported.</b>", parse_mode=ParseMode.HTML)
        else:
            with open("Resources/Records/issues.csv", "rb") as file:
                update.message.reply_document(file)
                update.message.reply_text("Above file contains list of all the issues reported")
            
def experts_list_command(update:Update, _: CallbackContext):
    if admin_object.check_chat_id(update.message.chat_id):
        
        logger.info(str(update.message.chat_id) + " - experts_list_command command initiated")

        df = pd.read_csv("Resources/Experts/approved_experts.csv")
        experts_array = df.values
        if df.shape[0] == 0:
            update.message.reply_text("<b>Sorry, currently no experts are registered.</b>", parse_mode=ParseMode.HTML)
        else:
            with open("Resources/Experts/approved_experts.csv", "rb") as file:
                update.message.reply_document(file)
                message = "<b>Follwing is the list of experts:</b>\n\n"
                i = 1
                for expert in experts_array:
                    message += "{}. {} - {}\n".format(str(i), expert[1], expert[2])
                    i +=1
                update.message.reply_text(message, parse_mode=ParseMode.HTML)    

def statistics(update:Update, _: CallbackContext):
    if admin_object.check_chat_id(update.message.chat_id):

        logger.info(str(update.message.chat_id) + " - statistics command initiated")

        reply = get_statistics()
        update.message.reply_text(reply, parse_mode=ParseMode.HTML)

###################### expert commands ##########################

def become_expert(update:Update, _:CallbackContext):
    
    if admin.admin_created == False:
        update.message.reply_text("Sorry, your request to become expert can't be processed because admin is offline.")
        return

    contact_keyboard = KeyboardButton(text="Click this button to send phone number.",request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[ contact_keyboard ]],resize_keyboard=True, one_time_keyboard=True)

    logger.info(str(update.message.chat_id) + " - become_expert command initiated")
    
    if update.message.chat_id in experts_list:
        update.message.reply_text("You is already an expert.")
        return
    elif update.message.chat_id in expert_requests:
        update.message.reply_text("you already requested to become expert. Please wait for approval by admin.")
        return
    
    update.message.reply_text("Click 👇 button to send phone number.\nIt is mandatory to give phone number for verification purpose.", reply_markup=reply_markup)
    become_expert_list.append(update.message.chat_id)
    
def answer_query(update:Update, _:CallbackContext):
    if update.message.chat_id in experts_list or admin_object.check_chat_id(update.message.chat_id):

        logger.info(str(update.message.chat_id) + " - answer_query command initiated")

        reply, keyboard = get_queries()
        update.message.reply_text(reply)
        try:
            update.message.reply_text("select the question you want to answer", reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            pass

        logs[update.message.chat_id] = "get_query"

def announce(update:Update, _:CallbackContext):
    if update.message.chat_id in experts_list or admin_object.check_chat_id(update.message.chat_id):

        logger.info(str(update.message.chat_id) + " - announce command initiated")

        logs[update.message.chat_id] = "announce"
        update.message.reply_text("<b>Please send the message to be announced 📢</b> \n\n⚠️ Message should be in the form of text only and can contain links.", parse_mode=ParseMode.HTML)

def get_doubts(update:Update, _: CallbackContext):
    if update.message.chat_id in experts_list or admin_object.check_chat_id(update.message.chat_id):

        logger.info(str(update.message.chat_id) + " - get_doubts command initiated")

        update.message.reply_text("Processing file please wait...")
        outcome = generate_all_doubts()
        if outcome:
            with open("Resources/Records/Doubts.csv", "rb") as file:
                update.message.reply_document(file)
        else:
            update.message.reply_text("Sorry no doubts asked")


###################### user's message processing functions ####################

def reply_text(update: Update, _: CallbackContext) -> None:
    """Reply the message."""
    logger.info(str(update.message.chat_id) + " - Message recieved ")

    try:
        if logs[update.message.chat_id] == "cbt":
            reply, sticker_path = cbt_handler(update.message.chat_id, get_remarks=True)
            try:
                with open(sticker_path, "rb") as s:
                    update.message.reply_sticker(s)
            except:
                update.message.reply_text(reply, parse_mode=ParseMode.HTML)
                return
            update.message.reply_text(reply, parse_mode=ParseMode.HTML)
            logs[update.message.chat_id] = "d"
            #update.message.reply_text(get_message("d"), parse_mode=ParseMode.HTML)
            update.message.reply_text("Try another therapy 🙂", reply_markup=InlineKeyboardMarkup(inline_keyboards["d"]))
            return
        
        elif logs[update.message.chat_id] == "doubt" or logs[update.message.chat_id] == "issue":

            logger.info(str(update.message.chat_id) + " - {} Recived ".format(logs[update.message.chat_id]))

            reply, sticker_path = doubt_issue(update.message.chat_id, update.effective_user.full_name, update.message.text)
            with open(sticker_path, "rb") as s:
                update.message.reply_sticker(s)
            update.message.reply_text(reply, parse_mode=ParseMode.HTML)
            update.message.reply_text("Select respective option", reply_markup=InlineKeyboardMarkup(inline_keyboards["a"]))
            return

        # Following conditional statement part is for admin and experts use only

        elif logs[update.message.chat_id] == "admin_login":
            bool, reply = validate_admin(update.message.chat_id, update.message.text)
            if bool == True:
                global admin_object
                admin_object = admin(update.message.chat_id, update.message.text)

                logger.info(" ADMIN LOGGED IN - Admin object created")

                #Saving the chat_id in the file
                with open("Resources/admin/admin.txt", "w") as file:
                    file.write(str(update.message.chat_id))
            
            update.message.reply_text(reply)
            update.message.reply_text(get_message("admin_help"), parse_mode= ParseMode.HTML)
            logs[update.message.chat_id] = 'z'
            return

        elif admin.admin_created == True:
            
            if admin_object.check_chat_id(update.message.chat_id) and admin_object.admin_log == "admin_logout":
                if admin_object.check_security_key(str(update.message.text)):

                    admin.admin_created = False
                    admin_object = None
                    update.message.reply_text("Logout successfully")
                    
                    logger.info("ADMIN LOGGED OUT - Admin object deleted")

                    # Deleting the admin file in which chat_id is stored
                    os.remove("Resources/admin/admin.txt")
                
                else:
                    update.message.reply_text("Incorrect security key sent")
                logs[update.message.chat_id] = 'z'
                return

            elif (update.message.chat_id in experts_list or admin_object.check_chat_id(update.message.chat_id)): 
                if logs[update.message.chat_id] == "ans_query": # query answering
                    reply = send_query_answer(update.message.chat_id, update.message.text)
                    update.message.reply_text(reply)
                    logs[update.message.chat_id] = 'z'
                    
                    logger.info(str(update.message.chat_id) + " - Query answer recieved ")

                    return

                elif logs[update.message.chat_id] == "announce": # making announcement to all users of the bot
                    update.message.reply_text("Announcing please wait...")
                    reply = announcement(update.message.text)
                    update.message.reply_text("Successfully announced to every user of the bot")
                    logs[update.message.chat_id] = 'z'

                    logger.info(str(update.message.chat_id) + " - Announcemnet completed ")

                    return


    except: # this part is when somehow the logs is deleted and user send custom message


        if update.message.text in ["hello", "hi", "hey", "Hello", "Hi", "Hey"]:
            update.message.reply_text(get_message("a"), parse_mode=ParseMode.HTML)
            logs[update.message.chat_id] = "a"
            update.message.reply_text("Select respective option", reply_markup=InlineKeyboardMarkup(inline_keyboards["a"]))
            return

        logger.info(str(update.message.chat_id) + " - sending query to Dialogflow API")
        
        reply, keyboard = custom_reply_handler(update.message.text, update.message.chat_id)
        update.message.reply_text(reply, parse_mode=ParseMode.HTML)
        try:
            update.message.reply_text("Select respective option", reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            pass
        print("Curret log from reply_text() - ", logs[update.message.chat_id])

    else:
        if update.message.text in ["hello", "hi", "hey", "Hello", "Hi", "Hey"]:
            update.message.reply_text(get_message("a"), parse_mode=ParseMode.HTML)
            logs[update.message.chat_id] = "a"
            update.message.reply_text("Select respective option", reply_markup=InlineKeyboardMarkup(inline_keyboards["a"]))
            return

        logger.info(str(update.message.chat_id) + " - sending query to Dialogflow API")
        
        reply, keyboard = custom_reply_handler(update.message.text, update.message.chat_id)
        update.message.reply_text(reply, parse_mode=ParseMode.HTML)
        try:
            update.message.reply_text("Select respective option", reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            pass




def option_selector(update: Update, _: CallbackContext):
    """ Handles the query(the number selected in the inline keyboard)"""
    
    query = update.callback_query
    text = query.data   # data send back by Inkine Keyboard

    logger.info(str(query.message.chat_id) + " - Callback query recieved  - {}".format(text))

    try:
        if logs[query.message.chat_id] != "cbt":
            query.edit_message_text("Here we go")

        ########## Following part will be used by expert and admin only ###################
        if query.message.chat_id in experts_list or admin_object.check_chat_id(query.message.chat_id):
            
            if logs[query.message.chat_id] == "get_query":
                reply = process_query(query.message.chat_id, int(text))
                query.message.reply_text(reply, parse_mode=ParseMode.HTML)
                logs[query.message.chat_id] = "ans_query" 
                return

            elif admin.admin_log == "a_expert": # accepting/rejecting expert 
                if int(text) == 1: # accepting the user request
                    reply = accept_request()
                elif int(text) == 0: # rejecting the user request
                    reply = reject_request()
                query.message.reply_text(reply, parse_mode=ParseMode.HTML)
                admin.admin_log = None
                return

            elif admin.admin_log == "r_expert": # removing expert
                reply = delete_expert_acc(int(text))
                query.message.reply_text(reply, parse_mode=ParseMode.HTML)
                admin.admin_log = None
                return
            
            # Setting the admin log to None because it could lead error "single positional indexer is out-of-bounds" in both elif statements.
            
        ##################################################################################

        if logs[query.message.chat_id] in num_handler_list and text.isnumeric(): # for 1,2,4 of services
            reply, image, link, keyboard = num_handler(query.message.chat_id, int(text))

            try:
                query.message.reply_photo(image)
                query.message.reply_text(link)
            except:
                if link != None:
                    query.message.reply_text(link)
            query.message.reply_text(reply, parse_mode=ParseMode.HTML)
            query.message.reply_text("Select respective option", reply_markup=InlineKeyboardMarkup(keyboard))    
                
        elif text=="I" : # for 5 of services
            query.message.reply_photo("http://static.businessworld.in/upload/GCX0sG_1551349353052.jpeg")
            query.message.reply_photo("https://github.com/HarshMathur86/test-repo/blob/main/Screenshot%20(2).png?raw=true")        
            query.message.reply_text(get_message("I"), parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(inline_keyboards["I"]))
            query.message.reply_text("Select respective option", reply_markup=InlineKeyboardMarkup(inline_keyboards["a"])) 
                
        elif text=="H": # for 6 of services
            with open("Resources/Stickers/doctor.tgs", "rb") as f:
                query.message.reply_sticker(f)
            query.message.reply_document("https://github.com/HarshMathur86/test-repo/blob/main/Mental%20Hospitals.pdf?raw=true")
            query.message.reply_text("Select respective option", reply_markup=InlineKeyboardMarkup(inline_keyboards["a"])) 


        elif text=="mt" or logs[query.message.chat_id] == "mt": # for music therapy
            try:
                reply, music, keyboard = music_thearpy(query.message.chat_id, int(text))

            except: # for the first time start of music therapy
                reply, music, keyboard = music_thearpy(query.message.chat_id, 1)
                query.message.reply_text(reply, reply_markup=InlineKeyboardMarkup(inline_keyboards["music_link"]))
            
            try:
                query.message.reply_voice(music)
            except:
                pass
            query.message.reply_text("🙂 Wan't some more?", reply_markup=InlineKeyboardMarkup(keyboard))

        elif logs[query.message.chat_id] == "d" and text.isnumeric(): # exiting to main menu from d(therapy) message

            update_messages_logs(query.message.chat_id, "a")
            query.message.reply_text(get_message("a"), parse_mode=ParseMode.HTML)
            query.message.reply_text("Select respective option", reply_markup=InlineKeyboardMarkup(inline_keyboards["a"])) 

        elif logs[query.message.chat_id] == 'cbt' or text == 'cbt': # for cbt therapy
            
            if text == 'cbt':
                logs[query.message.chat_id] = 'cbt'
                query.message.reply_text(get_message("cbt"), reply_markup=InlineKeyboardMarkup(inline_keyboards["cbt_link"]))
                query.message.reply_text("So here's my challenge {}:  You will take this therapy every day for the next couple of weeks".format(query.message.chat.first_name), reply_markup=InlineKeyboardMarkup(inline_keyboards["cbt_yn"]))
            
            if text.isnumeric():
                if int(text) <= 4:
                    query.edit_message_text("Next Question")
                    q_list, keyboard = cbt_handler(query.message.chat_id, int(text))
                    for q in q_list:
                        query.message.reply_text('<b><i>' + q + "</i></b>", parse_mode=ParseMode.HTML)
                    try:
                        query.message.reply_text("Select your answer", reply_markup=InlineKeyboardMarkup(keyboard))
                    except:
                        with open("Resources/Stickers/Pencil.tgs", "rb") as s:
                            query.message.reply_sticker(s)
                
                elif int(text) > 4:
                    
                    if int(text) == 5:
                        query.edit_message_text("Awesome, here comes the first question.")
                        query.message.reply_text("🎉")
                        q_list, keyboard = cbt_handler(query.message.chat_id)
                        for q in q_list:
                            query.message.reply_text('<b><i>' + q + '</i></b>', parse_mode=ParseMode.HTML)
                        query.message.reply_text("Select your answer", reply_markup=InlineKeyboardMarkup(keyboard))
                    else:
                        query.edit_message_text("Okay")
                        logs[query.message.chat_id] = "d"
                        query.message.reply_text(get_message("d"), parse_mode=ParseMode.HTML)
                        query.message.reply_text("Select respective option", reply_markup=InlineKeyboardMarkup(inline_keyboards["d"])) 

        elif text == "doubt" or text == "issue":  # for doubt asking and issue reporting
            with open("Resources/Stickers/Pencil.tgs", "rb") as s:
                query.message.reply_sticker(s)
            logs[query.message.chat_id] = text
            query.message.reply_text("Please write your {}.".format(text)) 

        print("current log - ", logs[query.message.chat_id])

    except Exception as E:
        
        query.message.reply_text(get_message("error"), parse_mode=ParseMode.HTML)
        logger.error(str(query.message.chat_id) + " - {}".format(E))
    



def main():
    print(logs)
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    # Following commands are user centric but can be used by anyone
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("admin_login", admin_login))
    dispatcher.add_handler(CommandHandler("services", services))
    dispatcher.add_handler(CommandHandler("become_expert", become_expert))

    # Following commands can only be used only by admin
    dispatcher.add_handler(CommandHandler("accept_expert_request", accept_expert_request))
    dispatcher.add_handler(CommandHandler("remove_expert", remove_expert))
    dispatcher.add_handler(CommandHandler("admin_logout", admin_logout))
    dispatcher.add_handler(CommandHandler("issues_reported", issues_reported))
    dispatcher.add_handler(CommandHandler("experts_list", experts_list_command))
    dispatcher.add_handler(CommandHandler("statistics", statistics))
    
    # Following commands can be used by expert and admin
    dispatcher.add_handler(CommandHandler("answer_query", answer_query))
    dispatcher.add_handler(CommandHandler("announce", announce))
    dispatcher.add_handler(CommandHandler("get_doubts", get_doubts))

    
    dispatcher.add_handler(CallbackQueryHandler(option_selector, run_async=True))
    
    dispatcher.add_handler(MessageHandler(Filters.text, reply_text, run_async=True))
    
    dispatcher.add_handler(MessageHandler(Filters.contact, contact))
    
    updater.start_polling()
    logger.info("Listening to telegram...\n\n")
    updater.idle()

if __name__ == '__main__':
    main()

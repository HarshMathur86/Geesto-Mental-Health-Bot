
import logging
from telegram import Update, InlineKeyboardMarkup, ParseMode, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

from utils import custom_reply_handler

from user import update_chat_id, update_messages_logs, num_handler, music_thearpy, get_message, cbt_handler, doubt_issue
from user import logs, inline_keyboards

from admin_expert import *



# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

TOKEN = "SAMPLE" #dummy


######   List of different label    ######
# Following list contains the total number of message labels which 
# just have callback query of numbers to be processed by single condition
# in option_selector method
num_handler_list = ["a", "b", "c", "e", "b1", "y", "w"]

# list of users who had initiated /become_expert command
become_expert_list = []

############   Initializing admin object    ##################
try:
    admin_object = Admin()
    admin_chat_id = admin_object.get_chat_id()
    if admin_chat_id is not None:
        logs[admin_chat_id] = 'z'
    del admin_chat_id
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

    update.message.reply_video("https://www.youtube.com/watch?v=7PBW4OKcuGc")
  
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
    if admin_object.is_user_admin(update.message.chat_id):
        update.message.reply_text(get_message("admin_help"), parse_mode=ParseMode.HTML)
    elif Expert.is_expert(update.message.chat_id):
        update.message.reply_text(get_message("expert_help"), parse_mode=ParseMode.HTML)

#####################  admin commands ########################

def admin_login(update: Update, _: CallbackContext):
    
    logger.info(" - admin_login command initiated")
    
    if Admin.admin_exists == True: 
        return

    update.message.reply_text("Enter the security key 🔑 to access administrative privileges")
    update_messages_logs(update.message.chat_id, "admin_login")
    
def accept_expert_request(update:Update, _: CallbackContext):
    if admin_object.is_user_admin(update.message.chat_id):
        
        logger.info(str(update.message.chat_id) + " - accept_expert_request command initiated")

        get_expert_request(update.message.chat_id)
        
        print("admin-log --->", Admin.admin_log)

def remove_expert(update:Update, _: CallbackContext):
    if admin_object.is_user_admin(update.message.chat_id):
        
        logger.info(str(update.message.chat_id) + " - remove_expert command initiated")

        get_expert_for_removing()

        Admin.admin_log = "r_expert"

def admin_logout(update:Update, _: CallbackContext):
    if admin_object is None:
        return
    if admin_object.is_user_admin(update.message.chat_id):
        
        logger.info(str(update.message.chat_id) + " - admin_logout command initiated")
        admin_object.admin_logout(update.message.chat_id)
        update.message.reply_text("Successfuly logged out.")


def tech_issues(update:Update, _: CallbackContext):
    if admin_object.is_user_admin(update.message.chat_id):
        
        logger.info(str(update.message.chat_id) + " - tech_issues command initiated")

        query_result_file_extractor("select issue as \"Technical issues reported\" from technical_issues_reported", "Technical issues.csv")

        with open("Resources/Database CSVs/Technical issues.csv", "rb") as file:
            update.message.reply_document(file, caption = "Above file contains list of all the issues reported")
            
def experts_list_command(update:Update, _: CallbackContext):
    if admin_object.is_user_admin(update.message.chat_id):
        
        logger.info(str(update.message.chat_id) + " - experts_list_command command initiated")

        data = execute_query("select name, contact_number from EXPERTS_DETAIL where approved_or_not is TRUE order by expert_id;")
        if len(data) == 0:
            update.message.reply_text("<b>Sorry, currently no experts are registered.</b>", parse_mode=ParseMode.HTML)
        else:
            # Document File Generation pending
            #update.message.reply_document(file)
            message = "<b><i>Follwing is the list of experts:</i></b>\n\n"
            i = 1
            for row in data:
                message += "{}. <b>{}</b> - {}\n".format(str(i), row["name"], row["contact_number"])
                i +=1
            update.message.reply_text(message, parse_mode=ParseMode.HTML)    

def statistics(update:Update, _: CallbackContext):
    if admin_object.is_user_admin(update.message.chat_id):

        logger.info(str(update.message.chat_id) + " - statistics command initiated")

        reply = get_statistics()
        update.message.reply_text(reply, parse_mode=ParseMode.HTML)

def medical_queries(update:Update, _: CallbackContext):
    if admin_object.is_user_admin(update.message.chat_id):

        logger.info(str(update.message.chat_id) + " - medical_queries command initiated")

        query = """select 
                    que_id as "Question ID",
                    que_asked as "Question asked",
                    CASE 
                        WHEN answered_or_not is FALSE THEN 'Not answered' ELSE 'Answered'
                    END as "Answered or not",
                    coalesce(name, '-') as "Name of Expert who answered",
                    coalesce(contact_number, 0)  as "Contact number of Expert",
                    coalesce(answer, '-') as "Expert's answer"
                    from 
                    patients_query LEFT OUTER JOIN experts_detail 
                    ON PATIENTS_QUERY.answered_by_expert_id = EXPERTS_DETAIL.expert_id 
                    order by que_id"""

        query_result_file_extractor(query, "Medical query records.csv")

        with open("Resources/Database CSVs/Medical query records.csv", "rb") as file:
            update.message.reply_document(file, caption = "Above file contains list of all the issues reported")
         
   
###################### expert commands ##########################

def become_expert(update:Update, _:CallbackContext):

    contact_keyboard = KeyboardButton(text="Click this button to send phone number.",request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[ contact_keyboard ]],resize_keyboard=True, one_time_keyboard=True)

    logger.info(str(update.message.chat_id) + " - become_expert command initiated")
    
    if Expert.is_expert(update.message.chat_id):
        update.message.reply_text("You is already an expert.")
        return
        
    elif Expert.is_expert(update.message.chat_id, applied=True):
        update.message.reply_text("you had already requested to become expert. Please wait for approval by admin.")
        return

    update.message.reply_text("Click 👇 button to send phone number.\nIt is mandatory to give phone number for verification purpose.", reply_markup=reply_markup)
    become_expert_list.append(update.message.chat_id)
    

def answer_query(update:Update, _:CallbackContext):
    if Expert.is_expert(update.message.chat_id) or admin_object.is_user_admin(update.message.chat_id):

        logger.info(str(update.message.chat_id) + " - answer_query command initiated")

        get_queries(update.message.chat_id)

        logs[update.message.chat_id] = "ans_query"

def announce(update:Update, _:CallbackContext):
    # Checking whether admin is sending the message or not
    if Expert.is_expert(update.message.chat_id) or admin_object.is_user_admin(update.message.chat_id):
        logger.info("{} - announce command initiated by admin".format(update.message.chat_id))
        
        update.message.reply_text("Hello, admin please send the message you want announce 🗣 among <b>all users</b> of the bot.\n\n<b>Note: If announcement contains image then send text message in caption of image.</b>", parse_mode=ParseMode.HTML)
        logs[update.message.chat_id] = 'ann' # announcement
        logger.info("{} - announce command initiated by admin".format(update.message.chat_id))

     
################## Message type specific functions ###################

def image_handler(update: Update, _:CallbackContext):
    logger.info("{} - announcement message recieved with image".format(update.message.chat_id))

    if logs[update.message.chat_id] != 'ann':
        return

    if Expert.is_expert(update.message.chat_id) or admin_object.is_user_admin(update.message.chat_id):
        announcement(update.message.caption, update.message.chat_id, update.message.photo[-1])
        update.message.reply_text("<b>Announcement to all users is compeleted</b>", parse_mode=ParseMode.HTML)
        logs[update.message.chat_id] = 'z'

def contact(update: Update, _: CallbackContext):
    
    if update.message.chat_id in become_expert_list:
    
        logger.info(str(update.message.chat_id) + " - Contact recieved")
        
        expert_objects[update.message.chat_id] = Expert(update.message.chat_id, update.message.contact.phone_number)

        logs[update.message.chat_id] = "name_exp"
        
        become_expert_list.remove(update.message.chat_id)
    
    else:
        update.message.reply_text("Please don't send contact.")


def reply_text(update: Update, _: CallbackContext) -> None:
    """Reply the message."""
    logger.info(str(update.message.chat_id) + " - Message recieved ")
    print(logs)
    print(Admin.admin_log)
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
            global admin_object
            bool, reply = admin_object.admin_login(update.message.chat_id, update.message.text) # text is the security key
            if bool == True:
                logger.info(" ADMIN LOGGED IN")
                update.message.reply_text(reply)
                update.message.reply_text(get_message("admin_help"), parse_mode= ParseMode.HTML)
            else:
                update.message.reply_text(reply)
                
            logs[update.message.chat_id] = 'z'
            return

        elif logs[update.message.chat_id] == "name_exp":
            # Processes the name received by the user for becoming an expert
            expert_objects[update.message.chat_id].add_name(update.message.text)
            expert_objects[update.message.chat_id].send_request()
            del expert_objects[update.message.chat_id]
            print(expert_objects)
            return

        elif Expert.is_expert(update.message.chat_id) or admin_object.is_user_admin(update.message.chat_id): # changed from previous version

            print("Expert/admin")
            
            if logs[update.message.chat_id] == "ans_query": 
                # Query answering
                send_query_answer(update.message.chat_id, update.message.text)
                
                logs[update.message.chat_id] = 'z'
                logger.info(str(update.message.chat_id) + " - Query answer recieved ")
                return

            elif logs[update.message.chat_id] == "ann": # making announcement to all users of the bot
                update.message.reply_text("Announcing please wait...")
                reply = announcement(update.message.text, update.message.chat_id)
                
                update.message.reply_text("<b>Announcement to all users is compeleted</b>", parse_mode=ParseMode.HTML)
                logs[update.message.chat_id] = 'z'
                return


    except Exception as error: # this part is when somehow the logs is deleted and user send custom message
        print(error)

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
        if admin_object.is_user_admin(query.message.chat_id):
            print("ADmin controles") 
            
            if Admin.admin_log == "a_expert": # accepting/rejecting expert 
                print("accepting/rejecting")
                if int(text) == 1: # accepting the user request
                    accept_request()
                elif int(text) == 0: # rejecting the user request
                    reject_request()
                
                Admin.admin_log = None
                return

            elif Admin.admin_log == "r_expert": # removing existing expert
                delete_expert(int(text)) # callback data is individual expert's ID
                Admin.admin_log = None
                return
            
            # Setting the admin log to None because it could lead error "single positional indexer is out-of-bounds" in both elif statements.
            
        ##################################################################################

        if logs[query.message.chat_id] in num_handler_list and text.isnumeric(): # for 1,2,4 of services
            reply, image, link, keyboard = num_handler(query.message.chat_id, int(text))

            """try:
                query.message.reply_photo(image)
                query.message.reply_text(link)
            except:
                if link != None:
                    query.message.reply_text(link)
            query.message.reply_text(reply, parse_mode=ParseMode.HTML)
            query.message.reply_text("Select respective option", reply_markup=InlineKeyboardMarkup(keyboard))"""

            if link != None:
                query.message.reply_text(link)
            
            try:
                query.message.reply_photo(image, caption=reply, parse_mode=ParseMode.HTML)
            except:
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
            if text == "doubt":
                # Medical issue
                query.message.reply_text("Welcome, we have dedicated team of <b><i>Doctors, Psychiatrist & Medical Consultants</i></b> for clarifying any doubt. Please also specify your/patient's age & gender (It would help our team to give u best suited advice).", parse_mode=ParseMode.HTML)
            
            query.message.reply_text("Please write your {}.".format(text)) 


    
    except Exception as E:    
        query.message.reply_text(get_message("error"), parse_mode=ParseMode.HTML)
        logger.error(str(query.message.chat_id) + " - {}".format(E))
    



def main():
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
    dispatcher.add_handler(CommandHandler("tech_issues", tech_issues))
    dispatcher.add_handler(CommandHandler("experts_list", experts_list_command))
    dispatcher.add_handler(CommandHandler("statistics", statistics))

    
    # Following commands can be used by expert and admin
    dispatcher.add_handler(CommandHandler("answer_query", answer_query))
    dispatcher.add_handler(CommandHandler("announce", announce))
    dispatcher.add_handler(CommandHandler("medical_queries", medical_queries))

    # Filtered message handlers
    dispatcher.add_handler(CallbackQueryHandler(option_selector))
    dispatcher.add_handler(MessageHandler(Filters.text, reply_text))
    dispatcher.add_handler(MessageHandler(Filters.contact, contact))
    dispatcher.add_handler(MessageHandler(Filters.photo, image_handler))

    
    updater.start_polling()
    logger.info("Listening to telegram...\n\n")
    updater.idle()

if __name__ == '__main__':
    main()

import logging
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram import Bot, ParseMode, InlineKeyboardMarkup

import schedule
import time
import threading

from user import message, update_messages_logs

from database import execute_query, query_result_file_extractor

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

#################### MULTI THREADING - Creating seprate thread for scheduling function ###################

#dummy scheduled function()
def dummy_fun():
    return
schedule.every(24).hours.do(dummy_fun)

def scheduled_functions_handler():
    while len(schedule.get_jobs())>0:
        
        time.sleep(1)
        try:
            schedule.run_pending()
        except Exception as exp:
            logger.info("exception occured - ".format(exp))

    # Killing the thread intentionally
    try: 
        raise BaseException("\n\nKilling the window closing thread")
    except:
        pass 

scheduler_thread = threading.Thread(target=scheduled_functions_handler)
scheduler_thread.setName("SchedulerThread")
scheduler_thread.start()
logger.info("SchedulerThread initiated")



# For containg Experts class object with chat_id as key
expert_objects = {}

#Initialising query_recipient_data[chat_id of expert answering the query] = chat_id of the user who asked the query
query_recipient_data = {}

bot = Bot(token="SAMPLE")

############## Admin Class #####################

class Admin():
    admin_exists = False
    admin_log = None
    
    def __init__(self):
        self.admin_chat_id = None
        self.security_key = "SAMPLE"

        # Loading 
        data = execute_query("select chat_id from ADMIN;")
        if len(data) > 0:
            self.admin_chat_id = data[0]["chat_id"]
            Admin.admin_exists = True
            logger.info(" Admin object initialized")
        else:
            logger.info(" Admin doesn't exist")

        
    def admin_login(self, chat_id, security_key):
        if Admin.admin_exists is False:
            # Login
            if security_key == self.security_key:
                execute_query("insert into ADMIN values({});".format(chat_id))
                self.admin_chat_id = chat_id
                Admin.admin_exists = True
                return True, "Successfully logged in as admin."
            else:
                return False, "Unsuccessful login, security key is wrong please retry."

    
    def admin_logout(self, chat_id):
        # Deleting the admin's data from the database
        execute_query("delete from ADMIN where chat_id = {}".format(chat_id))

        self.admin_chat_id = None
        Admin.admin_exists = False
        logger.info(" ADMIN LOGGED OUT")

    def check_chat_id(self, chat_id): # REJECTED
        print("CHECK - called")
        return self.admin_chat_id == chat_id

    def is_user_admin(self, chat_id):

        try:
            if chat_id == self.admin_chat_id:
                return True
            else:
                return False
        except:
            # this is required when admin is not logged in and initiates admin_logout command
            return False

    def get_chat_id(self):
        return self.admin_chat_id
        

    def send_message_to_admin(message, keyboard = None):
        if Admin.admin_exists:
            data = execute_query("select chat_id from admin;")
            if keyboard is None:
                bot.send_message(int(data[0]["chat_id"]), message, parse_mode=ParseMode.HTML)
            else:
                bot.send_message(int(data[0]["chat_id"]), message, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
        
        
#################################################

class Expert(): # specifically for processing user's request to become an expert 
    def __init__(self, chat_id, contact_number):
        self.chat_id = chat_id
        self.contact_number = None
        self.name = None

        print(type(contact_number))
        if len(str(contact_number)) > 10:
            if contact_number.startswith("+"):
                self.contact_number = contact_number[3:]
            else:
                self.contact_number = contact_number[2:]

        print(self.contact_number)
        bot.send_message(chat_id, "Please send your name.")

    def add_name(self, name):
        name.replace('\n', ' ')
        self.name = name

    def send_request(self):
        # Generating expert id
        data = execute_query("select max(expert_id) from experts_detail;")
        try:
            id = data[0]["max"] + 1
        except:
            id = 1
            
        execute_query("insert into EXPERTS_DETAIL values({}, {}, '{}', {}, FALSE);".format(
                self.chat_id, id, self.name, self.contact_number
            ))

        bot.send_message(self.chat_id, "Request for becoming expert is successfully received please wait for approval.")

    # Class Methods

    def is_expert(chat_id, applied = False):
        """This function will check whether a user has already applied for expert role or is an expert"""
        data = execute_query("select approved_or_not from EXPERTS_DETAIL where expert_chat_id = {}".format(chat_id))

        if len(data) == 0:
            return False
        elif applied:
            if data[0]["approved_or_not"] is False:
                # Used when user try to apply for expert role more than one 
                return True
        else:
            if data[0]["approved_or_not"] is True:
                return True

    def get_expert_id(chat_id):
        return execute_query("select expert_id from EXPERTS_DETAIL where expert_chat_id = {}".format(chat_id))[0]["expert_id"]
    
###########################################

def get_expert_request(chat_id):
    """ used by user to get request info and decide whether to accept or reject the request"""
    data = execute_query("select name, contact_number from EXPERTS_DETAIL where approved_or_not is FALSE order by expert_id limit 1;")

    if len(data) == 0:
        bot.send_message(chat_id, "No requests found")
    else:
        bot.send_message(chat_id, "Request to become expert received from:\n\nName : <b>{}</b>\nContact number : <b>{}</b>".format(data[0]["name"], data[0]["contact_number"]), 
                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Accept request", callback_data=1)], [InlineKeyboardButton("Reject request", callback_data=0)]]),
                            parse_mode=ParseMode.HTML)
        Admin.admin_log = "a_expert"

def accept_request():

    # extracting expert 
    data = execute_query("select expert_id, name, expert_chat_id from EXPERTS_DETAIL where approved_or_not is FALSE order by expert_id limit 1;")

    execute_query("update EXPERTS_DETAIL set approved_or_not = True where expert_id = {};".format(data[0]["expert_id"]))
    remaining_requests = execute_query("select count(expert_id) from EXPERTS_DETAIL where approved_or_not is FALSE;")[0]["count"]

    # Sending message to admin 
    Admin.send_message_to_admin("Successfully accepted the request of {} as our expert.\n\nRemaining experts request are {}.\n\n<b>Please use /accept_expert_request to accept them.</b>".format(data[0]["name"], remaining_requests))

    # ending message to user who is accepted as admin
    bot.send_message(int(data[0]["expert_chat_id"]), "🥳🥳 Congratulations, admin accepted your request as an expert.")
    
    logger.info(" Expert request accepted by ADMIN")

def reject_request():

    # extracting expert data
    data = execute_query("select expert_id, name, expert_chat_id from EXPERTS_DETAIL where approved_or_not is FALSE order by expert_id limit 1;")

    execute_query("delete from EXPERTS_DETAIL where expert_id = {};".format(data[0]["expert_id"]))
    remaining_requests = execute_query("select count(expert_id) from EXPERTS_DETAIL where approved_or_not is FALSE;")[0]["count"]

    # Sending message to admin 
    Admin.send_message_to_admin("Successfully rejected the request of {} as our expert.\n\nRemaining experts request are {}.\nPlease use /accept_expert_request to accept them.".format(data[0]["name"], remaining_requests))

    # ending message to user who is accepted as admin
    bot.send_message(int(data[0]["expert_chat_id"]), "Sorry, but admin rejected your request for becoming an expert.")
    
    logger.info(" Expert request rejected by ADMIN")

############  Functions to remove expert  ##################

def get_expert_for_removing():
    keyboard = []
    data = execute_query("select name, contact_number, expert_id from EXPERTS_DETAIL where approved_or_not is TRUE and expert_id != 1;")

    if len(data) == 0:
        Admin.send_message_to_admin("<b>Sorry, there are no experts registered.</b>")
        return 
    
    
    for row in data:
        keyboard.append([InlineKeyboardButton("{} - {}".format(row["name"], row["contact_number"]), callback_data=int(row["expert_id"]))])
        
    # Adding addition keyboard button for terminating removing of the user
    keyboard.append([InlineKeyboardButton("Don't want to remove", callback_data=0)])
    print(keyboard)
    Admin.send_message_to_admin("<b>Following is the list of experts with there phone number.</b>\nPlease select the expert you want to remove", keyboard=keyboard)


def delete_expert(expert_id):

    # Checking if admin don't want to remove any user by clicking "Don't want to remove" button custom keyboard
    if expert_id == 0: # zero expert id is not possible it is just used for idenfying termination of the task
        Admin.send_message_to_admin(message["admin_help"])
        return

    # Sending message to the user of removing him/her as expert 
    data = execute_query("select expert_chat_id, name from EXPERTS_DETAIL where expert_id = {};".format(expert_id))
    bot.send_message(int(data[0]['expert_chat_id']), "Sorry, but admin removed you as an expert.")

    # Removing the expert's data from database
    execute_query("delete from EXPERTS_DETAIL where expert_id = {}".format(expert_id))

    # Updating the logs
    logger.info(" - ADMIN removed expert / deleting expert account") 
    
    # Success message to admin
    Admin.send_message_to_admin("Successfully removed {} as our expert.\n\n<b>For removing more expert click - /remove_expert</b>".format(data[0]["name"]))


############  Functions to process queriers/doubts asked by user ##################

def unanswered_query_revoker(chat_id, question_id):
    print("REvoker - ",threading.current_thread())
    print(schedule.get_jobs())
    # Condition of unanswered question by mistake and reserved
    data = execute_query("select que_id from PATIENTS_QUERY where answer is NULL and que_id = {};".format(question_id))
    print("data from revoker ---> ", data)
    if len(data) > 0:
        # Que asigned to an expert exists and needs to be revoked(by putting answered_by_expert_id again to NULL)
        execute_query("update PATIENTS_QUERY set answered_by_expert_id = NULL where que_id = {};".format(question_id))
        bot.send_message(chat_id, "Answering window for previous question timed out. Please click - /answer_query if want to restart.")
        update_messages_logs(chat_id, 'z')

    return schedule.CancelJob


def get_queries(chat_id):

    # Extracting query from database on FCFS basis using question id number
    data = execute_query("select que_id, que_asked from PATIENTS_QUERY where answered_or_not is FALSE and answered_by_expert_id is NULL order by que_id limit 1;") 
    print("data Fresh ---> ", data, type(data))
    
    
    if len(data) == 0:
        bot.send_message(chat_id, "No doubts asked recently.")
        return

    expert_id = Expert.get_expert_id(chat_id)

    # Reserving the que for this particular expert to answer
    execute_query("update PATIENTS_QUERY set answered_by_expert_id = {} where que_id = {}".format(expert_id, data[0]["que_id"]))

    # Sending the question to the expert
    bot.send_message(chat_id, "<b>Following question is asked by a user/patient:-</b>\n\n{}".format(data[0]["que_asked"]), parse_mode = ParseMode.HTML)
    bot.send_message(chat_id, "Please write the suggestion/answer of user's query.")

    # Scheduling the revoker function and Generating the thread
    schedule.every(180).seconds.do(unanswered_query_revoker, chat_id, data[0]["que_id"])
    

def send_query_answer(expert_chat_id, answer):

    # Extracting the query which is reserved for this particular expert
    expert_id = Expert.get_expert_id(expert_chat_id)
    data = execute_query("select patient_chat_id, que_id, que_asked from PATIENTS_QUERY where answered_by_expert_id = {} and answered_or_not is FALSE order by que_id limit 1;".format(expert_id))

    print(data)

    # Saving the data to database
    execute_query("update PATIENTS_QUERY set answered_or_not = TRUE, answer = '{}' where que_id = {}".format((answer.replace('\n', ' ')).replace(',', ' '), data[0]["que_id"]))

    # Sending the answer to the user/patient who asked the question
    bot.send_message(int(data[0]["patient_chat_id"]), "Congratulations, our expert answered your query: \n\n<b>Question you asked</b> \n👉 <i>{}</i>\n\n<b>Answer from expert</b>\n👉 {}".format(data[0]["que_asked"], answer), parse_mode=ParseMode.HTML)

    #updating the logs
    logger.info(str(expert_chat_id) + " - sending query answer") 

    bot.send_message(expert_chat_id, "Answer send successfully to user.")   


############ Function for announcement #############################
def announcement(message_to_announce, sender_chat_id, image=None):

    logger.info("sending announcements")

    data = execute_query("select * from ARRIVED_USERS where chat_id!={};".format(sender_chat_id))

    if image is None:
        for row in data:
            try:
                bot.send_message(int(row["chat_id"]), message_to_announce)
                logger.info(str(row["chat_id"]) + " - annoucement sent")
            except:
                pass
    else:
        for row in data:
            try:
                bot.send_photo(int(row["chat_id"]), image, caption=message_to_announce)
                logger.info(str(row["chat_id"]) + " - annoucement sent")
            except Exception as e:
                pass
        
############ Function for Statistics generation ###############################
def get_statistics():

    #updating the logs
    logger.info("preparing statistical data") 

    message = "<b>Following are some staticstics 🗒 of the bot:</b>\n\n"
    
    # no of user
    data = execute_query("select count(chat_id) from ARRIVED_USERS;")
    message += "Total number of unique users : <b>{}</b>\n\n".format(data[0]["count"])

    # no of technical issues reported
    data = execute_query("select count(issue) from TECHNICAL_ISSUES_REPORTED;")
    message += "Technical issues reported : <b>{}</b>\n\n".format(data[0]["count"])

    # no of medical queries asked
    data = execute_query("select count(que_id) from PATIENTS_QUERY;")
    message += "Medical queries recieved : <b>{}</b>\n".format(data[0]["count"])
    
    data = execute_query("select count(que_id) from PATIENTS_QUERY where answered_or_not is TRUE;")
    message += "Resolved : <b>{}</b>\n".format(data[0]["count"])

    data = execute_query("select count(que_id) from PATIENTS_QUERY where answered_or_not is FALSE;")
    message += "Unresolved : <b>{}</b>\n\n".format(data[0]["count"])
    
    # no of experts
    data  = execute_query("select count(expert_id) from EXPERTS_DETAIL where approved_or_not is TRUE")
    message += "Total number of experts : <b>{}</b>\n".format(data[0]["count"])
    
    data  = execute_query("select count(expert_id) from EXPERTS_DETAIL where approved_or_not is FALSE")
    message += "Number of expert requests pending : <b>{}</b>\n\n".format(data[0]["count"])

    # no of cbt
    #from user import cbt_takers_count # to get real time value 
    #message += "Number of <i>CBT therapy</i> taken : <b>{}</b>\n".format(cbt_takers_count)

    return message

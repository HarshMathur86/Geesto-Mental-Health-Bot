import logging
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram import Bot, ParseMode, InlineKeyboardMarkup
import pandas as pd
import numpy as np

from user import records_updater, message

from database import execute_query

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


#Initialising experts list containg chat_id of experts

expert_objects = {}


try:
    df = pd.read_csv("Resources/Experts/approved_experts.csv")
    experts_list  = df.chat_id.values
    experts_list = [c for c in experts_list]
    del df
except:
    experts_list = []

#Initailising experts request
try:
    df = pd.read_csv("Resources/Experts/requests.csv")
    expert_requests  = df.chat_id.values
    expert_requests = [c for c in expert_requests]
    del df
except:
    expert_requests = []


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
    data = execute_query("select name, contact_number, expert_id from EXPERTS_DETAIL where approved_or_not is TRUE;")

    if len(data) == 0:
        Admin.send_message_to_admin("<b>Sorry, there are no experts registered.</b>")
        return 
    
    
    for row in data:
        keyboard.append([InlineKeyboardButton("{} - {}".format(row["name"], row["contact_number"]), callback_data=int(row["expert_id"]))])
        
    # Adding addition keyboard button for terminating removing of the user
    keyboard.append([InlineKeyboardButton("Don't want to remove", callback_data=0)])

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

def get_queries():
    df_query = pd.read_csv("Resources/Records/doubts.csv")

    if df_query.shape[0] == 0:
        return "No doubts asked", None

    questions = df_query.data.values

    keyboard = []
    idx = 0
    for que in questions:
        keyboard.append([InlineKeyboardButton(que, callback_data=idx)])
        idx += 1

    return "Following is the list of doubts asked", keyboard 

def process_query(expert_chat_id, index):
    # Removing the data from doubts.csv file
    df_query = pd.read_csv("Resources/Records/doubts.csv")
    query_data = df_query.iloc[index]
    queries_array = df_query.values
    queries_array = np.delete(queries_array, index, axis=0)

    new_df = pd.DataFrame(queries_array)
    new_df.columns = ["chat_id", "username", "data"]
    new_df.to_csv("Resources/Records/doubts.csv", index=False)

    #Saving the data in resolved_doubts.csv
    records_updater("Resources/Records/resolved_doubts.csv", "{},{},{}".format(str(query_data[0]), query_data[1], query_data[2]))
        
    # storing the reciepient chat_id
    query_recipient_data[expert_chat_id] = query_data
    
    return "Please send the answer of the following question:\n\n<b>{}</b>".format(query_data[2])

def send_query_answer(expert_chat_id, answer):
    bot.send_message(str(query_recipient_data[expert_chat_id][0]), "🤩🤩Congratulations, our expert answered your query: \n\nQuestion you asked \n👉 {}\n\nAnswer from expert\n👉 ".format(query_recipient_data[expert_chat_id][2]) + answer)
    del query_recipient_data[expert_chat_id]

    #updating the logs
    logger.info(str(expert_chat_id) + " - sending query answer") 

    return "Answer send successfully to user."   

############ Function for announcement #############################
def announcement(message_to_announce):
    chat_ids_df = pd.read_csv("chat_id.csv")
    chat_ids = np.array(chat_ids_df.chat_id)
    
    for chat_id in chat_ids:

        bot.send_message(str(chat_id), text=message_to_announce)

        logger.info(str(chat_id) + " - annoucement sent")
        
############ Function for Statistics generation ###############################
def get_statistics():

    #updating the logs
    logger.info("preparing statistical data") 

    message = "<b>Following are some staticstics 🗒 of the bot:</b>\n\n"
    
    # no of user
    chat_id_df = pd.read_csv("chat_id.csv")
    message += "Total number of unique users : <b>{}</b>\n\n".format(chat_id_df.shape[0])

    # no of issues
    issues_df = pd.read_csv("Resources/Records/issues.csv")
    message += "Total issues reported : <b>{}</b>\n\n".format(issues_df.shape[0])

    # no of doubts
    unresolved_doubts_df = pd.read_csv("Resources/Records/doubts.csv")
    resolved_doubts_df = pd.read_csv("Resources/Records/resolved_doubts.csv")
    total_doubts = unresolved_doubts_df.shape[0] + resolved_doubts_df.shape[0]

    message += "Total doubts recieved : <b>{}</b>\n".format(total_doubts)
    message += "Resolved : <b>{}</b>\n".format(resolved_doubts_df.shape[0])
    message += "Unresolved : <b>{}</b>\n\n".format(unresolved_doubts_df.shape[0])
    
    # no of experts
    message += "Total number of experts : <b>{}</b>\n".format(len(experts_list))
    message += "Number of expert requests pending : <b>{}</b>\n\n".format(len(expert_requests))

    # no of cbt
    from user import cbt_takers_count # to get real time value 
    message += "Number of <i>CBT therapy</i> taken : <b>{}</b>\n".format(cbt_takers_count)

    return message
    
############ Function to generate file all_doubts.csv ################
def generate_all_doubts():
    #Reading the file
    ur_df = pd.read_csv("Resources/Records/doubts.csv")
    r_df = pd.read_csv("Resources/Records/resolved_doubts.csv")

    #droping chat_id column
    ur_df = ur_df.drop("chat_id", axis=1)
    r_df = r_df.drop("chat_id", axis=1)

    #creating numpy array of the data frames
    r_array = np.array(r_df)
    ur_array = np.array(ur_df)

    if r_array.shape[0] != 0 and ur_array.shape[0] != 0: 
        
        #creating and adding column for status
        status = np.array(["Unresolved" for i in range(ur_array.shape[0])])
        status = status.reshape(ur_array.shape[0],-1)
        ur_array = np.hstack((ur_array, status))

        status = np.array(["Resolved" for i in range(r_array.shape[0])])
        status = status.reshape(r_array.shape[0],-1)
        r_array = np.hstack((r_array, status))

        #adding both the array
        all_doubts_array = np.vstack((ur_array, r_array))

    elif r_array.shape[0] != 0 and ur_array.shape[0] == 0: 
        # when unresolved array is empty then only processing all resolved doubts
        
        #creating and adding column for status
        status = np.array(["Resolved" for i in range(r_array.shape[0])])
        status = status.reshape(r_array.shape[0],-1)
        all_doubts_array = np.hstack((r_array, status))

    elif r_array.shape[0] == 0 and ur_array.shape[0] != 0: 
        # when resolved array is empty then only processing all unresolved doubts
        
        #creating and adding column for status
        status = np.array(["Unresolved" for i in range(ur_array.shape[0])])
        status = status.reshape(ur_array.shape[0],-1)
        all_doubts_array = np.hstack((ur_array, status))

    else: # when both is empty
        return False


    #creating the data frame of all doubts
    all_doubts_df = pd.DataFrame(all_doubts_array)
    all_doubts_df.columns = ["Name of user", "Doubt asked", "Status"]

    all_doubts_df.to_csv("Resources/Records/Doubts.csv", index=False)
    return True

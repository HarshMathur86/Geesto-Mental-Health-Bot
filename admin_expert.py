import logging
from types import resolve_bases

from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from support import records_updater
from telegram import Bot, message, user
import pandas as pd
import numpy as np

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# structure of admin_object dict --> admin_object = {"chat_id_of_admin": <obj of "admin" class> }   
admin_object = {}

#Initialising experts list containg chat_id of experts
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


bot = Bot(token="1732516218:AAGTpXB4HeMgP4qROqh4orLwY42ipAsarp8")



class admin():
    admin_created = False
    chat_id = None
    admin_log = None
    
    def __init__(self, chat_id, security_key):
        if admin.admin_created == False and security_key == "?WN34Az8p^wRURc5-k3!":
            self.admin_chat_id = chat_id
            admin.chat_id = chat_id
            admin.admin_created = True
            admin.admin_log = None

    def check_chat_id(self, chat_id):
        return self.admin_chat_id == chat_id

    def check_security_key(self, key):
        return "?WN34Az8p^wRURc5-k3!" == key


def validate_admin(chat_id, security_key):

    logger.info(" validating admin login credentials")

    if admin.admin_created == False and security_key == "?WN34Az8p^wRURc5-k3!":
        return True, "Successfully logged in as admin."

    elif admin.admin_created == True and security_key == "?WN34Az8p^wRURc5-k3!":
        if(admin.chat_id == chat_id):
            return False, "You is already logged in as admin."
        return False, "Unsuccessful login admin already exists."
    
    elif security_key != "?WN34Az8p^wRURc5-k3!":
        return False, "Unsuccessful login security key is wrong please retry."



############  Functions to process user request to become expert ################## 

def save_expert_request(chat_id, name, phone_number):
    
    if len(str(phone_number)) > 10:
        if phone_number.startswith("+"):
            phone_number = phone_number[3:]
        else:
            phone_number = phone_number[2:]
    
    bot.send_message(str(admin.chat_id),  text="User request recieved to become expert from:\n\nName : " + name + "\nPhone number : " + phone_number + "\n\n for approving request please click - /accept_expert_request")
    logger.info(str(chat_id) + " - saving request for expert in file")

    expert_requests.append(chat_id)
    records_updater("Resources/Experts/requests.csv", str(chat_id) + "," + name + "," + phone_number)
    return True, "Request for becoming expert is successfully sent to admin please wait for approval."

def get_expert_request():
    df = pd.read_csv("Resources/Experts/requests.csv")
    if df.shape[0] == 0:
        return False
    first_req = df.values[0]
    return "Request to become expert recived from:\n\nName : <b>{}</b>\nPhone number : <b>{}</b>".format(first_req[1], first_req[2])

def accept_request():
    #updating the files
    df = pd.read_csv("Resources/Experts/requests.csv")
    user_data = df.iloc[0]
    df = df[1:][:]
    df.to_csv("Resources/Experts/requests.csv", index=False)
    records_updater("Resources/Experts/approved_experts.csv", "{},{},{}".format(str(user_data[0]), user_data[1], user_data[2]))

    #updating the lists
    expert_requests.remove(user_data[0])
    experts_list.append(user_data[0])

    #updating the logs
    logger.info(str(user_data[0]) + " - accepting request of user as expert") 

    #sending confirmation message to the user of request approval
    bot.send_message(str(user_data[0]), "Congratulations, admin accepted your request as an expert.")
    return "Successfully accepted the request of {} as our expert.\n\nRemaining experts request are {}.\n\n<b>Please use /accept_expert_request to accept them.</b>".format(user_data[1], str(len(expert_requests)))


def reject_request():
    #updating the file(delete the request data from requests.csv)
    df = pd.read_csv("Resources/Experts/requests.csv")
    user_data = df.iloc[0]
    df = df[1:][:]
    df.to_csv("Resources/Experts/requests.csv", index=False)
    
    #updating the lists
    expert_requests.remove(user_data[0])

    #updating the logs
    logger.info(str(user_data[0]) + " - rejecting request of user as expert") 

    #sending confirmation message to the user of request approval
    bot.send_message(str(user_data[0]), "Sorry, but admin rejected your request for becoming an expert.")
    return "Successfully rejected the request of {} as our expert.\n\nRemaining experts request are {}.\nPlease use /accept_expert_request to accept them.".format(user_data[1], str(len(expert_requests)))


############  Functions to remove expert  ##################

def get_expert_for_removing():
    keyboard = []
    df_experts = pd.read_csv("Resources/Experts/approved_experts.csv")
    experts_array = df_experts.values
    if experts_array.shape[0] == 0:
        return "<b>Sorry, there are no experts registered.</b>", None
    idx = 0
    for user_data in experts_array:
        keyboard.append([InlineKeyboardButton("{} - {}".format(user_data[1], user_data[2]), callback_data=idx)])
        idx += 1
    return "<b>Following is the list of experts with there phone number.</b>", keyboard


def delete_expert_acc(idx):
    # Removing the data from approved_experts.csv file
    df_experts = pd.read_csv("Resources/Experts/approved_experts.csv")
    user_data = df_experts.iloc[idx]
    experts_array = df_experts.values
    experts_array = np.delete(experts_array, idx, axis=0)

    new_df = pd.DataFrame(experts_array)
    new_df.columns = ["chat_id", "username", "data"]
    
    new_df.to_csv("Resources/Experts/approved_experts.csv", index=False)

    #updating the list
    experts_list.remove(user_data[0])

    #updating the logs
    logger.info(str(user_data[0]) + " - removing expert / deleting expert account") 
    
    #sending message to the user of removing him/her as expert
    bot.send_message(str(user_data[0]), "Sorry, but admin removed you as an expert.")
    return "Successfully removed {} as our expert.\n\n<b>For removing more expert click - /remove_expert</b>".format(user_data[1])


############  Functions to process queriers/doubts asked by expert ##################

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
    from support import cbt_takers_count
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
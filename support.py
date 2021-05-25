import logging
import numpy as np
import pandas as pd
import random
from telegram import InlineKeyboardButton
import sys as s

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


"""different messages with var name as there label"""

message = {

    'a': "<b>Hi, here is how I will aware you & help you regarding mental health-</b>\n😀\nExplore the services:\n\n<b>1.</b> 🧠 Mental Health & Wellness Introduction\n<b>2.</b> 📈 How to improve mental health?\n<b>3.</b> 👨‍⚕ Improve your health - I am a therapist\n<b>4.</b> 🧘 Yoga, Workout & Meditation\n<b>5.</b> 🇮🇳 Mental health in India\n<b>6.</b> 🏥 Hospitals & NGOs to help you\n<b>7.</b> ❓ Expert doubt support\n<b>8.</b> 🛠 Report any issue\n\nRespond with option number (e.g. 1 for mental health introduction)\n\nIf you don't find what you are looking for, please send me a query.",
    'b': "<b>Let's understand mental health</b> 🤔\n\n1. What is Mental Health?\n2. What is Mental Wellbeing?\n3. Different types of mental disorder.\n4. How to treat mentally ill patients?\n5. How can you aware others about mental health?\n6. 🔙 Go back to main menu\n\nReply the option just like earlier",
    'c': 'These are some tasks you should do if finding yourself in stress or anxiety:\n\n1. Talk about your feeling\n2. Keep active \n3. Eat well\n4. Drink sensibly\n5. Keep in touch\n6. Ask for help\n7. Take a break\n8. Do something you are good at\n9. Accept who you are\n10. Care for others\n11. 🔙 Go back to main menu\n\n<b>Also,try therapy in which I will help you to improve you mental health</b> 😇\nJust go back and hit 3⃣ for therapy',
    'b1': "\n<b>There are many different conditions that are recognized as mental illnesses. The more common types include:</b>\n\n1. Depressive disorders\n2. Anxiety disorders\n3. Neurodevelopmental Disorders\n4. Bipolar disorders\n5. Stress related disorders\n6. Dissociative disorders\n7. Neuro cognitive disorder\n8. 🔙 Go back \n\nselect option to know in detail about particular disorders",
    'e': "There are many activities you can do to improve your mental as well as physical health 🤩🤩 like:<b>\n\n 👉  Yoga\n 👉  Workout\n 👉  Meditation\n\n</b>So why not to try out some of them. \n\nLet's start🙂",
    'y': '<b>Astounding Yoga Poses For Mental Health And Wellness:</b>\n\n1. Balasana (Baby Pose)\n2. Viparita Karani (Legs Up The Wall Pose)\n3. Uttanasana (Forward Bent Pose)\n4. Sethubandhasana (Bridge Pose)\n5. Shavasana (Corpse Pose)\n6. Anjaneyasana (Crescent Moon Pose)\n7. Garudasana (Eagle Pose)\n8. 🔙 Go back to main menu\n\nselect option to know in detail about particular disorder',
    'w': "<b>These are some workouts you can perform to make yourself healthy:</b>\n\n1. Running\n2. Cycling\n3. Weight lifting\n4. Push ups\n5. Deep breathing\n6. Laughter\n\nLet's try any of these.",
    'd': "Hello,\nI can take following therapy session so that you can improve your mental health: 😇\n\n👉 <b>CBT</b> (<i>Cognitive Behavioral Thearpy</i>)\n\n👉 <b>Music Therapy</b>",
    'error': "Sorry unable to process please restart by <b>clicking</b> - /services",
    'cbt': "Cognitive behavioral therapy (CBT) is a type of psychotherapeutic treatment that helps people learn how to identify and change destructive or disturbing thought patterns that have a negative influence on behavior and emotions.\n\nCheckout the below link 👇 to know more about CBT.",
    'I': " 📌 The scenario surrounding mental health has not changed much, especially in India. There’s still stigma attached to mental illnesses and the number of psychiatrists and counsellors in the country are very less.\n\n 📌 1 in a 5 has some emotional and behavioural problems. Close to 60 to 70 million people in the country suffer from common and severe mental disorders. India is the world’s suicide capital with over 2.6 lakh cases of suicide in a year. <b>WHO statistics say the average suicide rate in India is 10.9 for every lakh people accounting for 36.6 per cent of suicides globally.</b>\n\n 📌 WHO also estimates that, in India, the economic loss, due to mental health conditions, between 2012-2030, is 1.03 trillions of 2010 dollars.",
    'issue': "<b>Thumps up</b> for that, thanks for reporting this issue my creators will immediately resolve this.",
    'doubt': "<b>Thanks for sending your query our experts will answer this shortly.</b>",
    'help': "<b>Welcome, to mental health & wellness bot.</b>\nThis bot will help you in every aspect of mental health like-\n 👉 What is mental health?\n 👉 How to aware people & promote mental health?\n 👉 Can take therapies of mental health?\n 👉 Also help you to do yoga/workout/meditation?\nAnd, many more\n\n<b>Explore the services by following commands:\n\n/start  </b><i>- Start the bot</i>\n<b>/services</b>  <i>- Services offered by bot</i>\n<b>/help</b>  <i>- Get help</i>\n\nBot can talk and also have nice conversation ability.\n\nSay <b>👋 hi/hello</b> or click - /services to explore the services",
    'admin_help': "<b>Explore the following commands you can use as an admin 🧐 </b>\n\n<b>/accept_expert_request</b> - <i>accepting user's request to become expert</i>\n<b>/remove_expert</b> - <i>to remove expert</i>\n<b>/issues_reported</b> - <i>get issues reported by the users</i>\n<b>/experts_list</b> - <i>get list of experts</i>\n<b>/statistics</b> - <i>get statistical data of bot</i>\n\n<b>/admin_login</b> - <i>login as admin</i>\n<b>/admin_logout</b> - <i>logout as admin</i>\n\n<b>You can also access all the cammands used by an expert\n\n/answer_query</b> - <i>answering query asked by user</i>\n<b>/announce</b> - <i>making an announcemnet</i>\n<b>/get_doubts</b> - <i>get list of all doubts asked</i>",
    'expert_help': "<b>Explore the following commands you can use as an expert 🧐 </b>\n\n<b>/answer_query</b> - <i>answering query asked by user</i>\n<b>/announce</b> - <i>making an announcemnet</i>\n<b>/get_doubts</b> - <i>get list of all doubts asked</i>"
}


service = {

    1:"b",
    2:"c",
    3:"d",
    4:"e",
    7:"f",
    8:"g"
}

mental_health_intro = {
    1:"b",
    2:"b",
    3:"b1",
    4:"b",
    5:"b",
    6:"a"   #go back updating label to "a"
}

activities = {
    1:"y",
    2:"w",
    3:"m",
    4:"a"
}

inline_keyboards = {
    "a":[
        [
            InlineKeyboardButton("1", callback_data=1),
            InlineKeyboardButton("2", callback_data=2),
            InlineKeyboardButton("3", callback_data=3),
            InlineKeyboardButton("4", callback_data=4)
        ],
        [
            InlineKeyboardButton("5", callback_data="I"), # option 5 will have direct answer
            InlineKeyboardButton("6", callback_data="H"), # option 6 will have direct answer
            InlineKeyboardButton("7", callback_data="doubt"),
            InlineKeyboardButton("8", callback_data="issue")
        ]
    ],

    "b":[
        [
            InlineKeyboardButton("1", callback_data=1),
            InlineKeyboardButton("2", callback_data=2),
            InlineKeyboardButton("3", callback_data=3),
            InlineKeyboardButton("4", callback_data=4),
            InlineKeyboardButton("5", callback_data=5)
        ],
        [
            InlineKeyboardButton("🔙 to main menu", callback_data=6)
        ]
    ],

    "b1":[
        [
            InlineKeyboardButton("Depressive", callback_data=1),
            InlineKeyboardButton("Anxiety", callback_data=2)
        ],
        [
            InlineKeyboardButton("Neurodevelopmental", callback_data=3),
            InlineKeyboardButton("Bipolar", callback_data=4)
        ],
        [
            InlineKeyboardButton("Stress related", callback_data=5),
            InlineKeyboardButton("Dissociative", callback_data=6)
        ],
        [
            InlineKeyboardButton("Neuro cognitive", callback_data=7),
            InlineKeyboardButton("🔙 Go back", callback_data=8)
        ]        
    ],

    "c":[
        [
            InlineKeyboardButton("1", callback_data=1),
            InlineKeyboardButton("2", callback_data=2),
            InlineKeyboardButton("3", callback_data=3),
            InlineKeyboardButton("4", callback_data=4),
            InlineKeyboardButton("5", callback_data=5)
        ],
        [
            InlineKeyboardButton("6", callback_data=6),
            InlineKeyboardButton("7", callback_data=7),
            InlineKeyboardButton("8", callback_data=8),
            InlineKeyboardButton("9", callback_data=9),
            InlineKeyboardButton("10", callback_data=10)
        ],
        [
            InlineKeyboardButton("🔙 to main menu", callback_data=11)
        ]
    ],

    "e":[
        [
            InlineKeyboardButton("Yoga", callback_data=1)
        ],
        [
            InlineKeyboardButton("Workout", callback_data=2)
        ],
        [
            InlineKeyboardButton("Meditation", callback_data=3)
        ],
        [
            InlineKeyboardButton("🔙 to main menu", callback_data=4)
        ]
    ],

    "y":[
        [
            InlineKeyboardButton("Balasana", callback_data=1),
            InlineKeyboardButton("Viparita Karani", callback_data=2)
        ],
        [
            InlineKeyboardButton("Uttanasana", callback_data=3),
            InlineKeyboardButton("Sethubandhasana", callback_data=4)
        ],
        [
            InlineKeyboardButton("Shavasana", callback_data=5),
            InlineKeyboardButton("Anjaneyasana", callback_data=6)
        ],
        [
            InlineKeyboardButton("Garudasana", callback_data=7),
            InlineKeyboardButton("🔙 Go back", callback_data=8)
        ]        
    ],

    "w":[
        [
            InlineKeyboardButton("Running", callback_data=1),
            InlineKeyboardButton("Cycling", callback_data=2)
        ],
        [

            InlineKeyboardButton("Weight lifting", callback_data=3),
            InlineKeyboardButton("Push ups", callback_data=4)
        ],
        [

            InlineKeyboardButton("Deep breathing", callback_data=5),
            InlineKeyboardButton("Laughter", callback_data=6)
        ],
        [

            InlineKeyboardButton("🔙 Go back", callback_data=7)
        ]
    ],

    "I":[
        [
            InlineKeyboardButton("Report of Indian Mental Health Survey", url="http://www.indianmhs.nimhans.ac.in/Docs/Summary.pdf")
        ]
    ],

    "d":[
        [
            InlineKeyboardButton("CBT (Cognitive Behavioural Therapy)", callback_data="cbt")
        ],
        [
            InlineKeyboardButton("🎵 Music Therapy 🎵", callback_data="mt")
        ],
        [
            InlineKeyboardButton("🔙 to main menu", callback_data=3)
        ]
    ],

    "mt":[
        [
            InlineKeyboardButton("🎵 More Music 🎵", callback_data=1)
        ],
        [
            InlineKeyboardButton("🔙 Go back", callback_data=2)
        ]
    ],
    
    "music_link":[
        [
            InlineKeyboardButton("Why music is great for your mental health❔", url="https://www.mind.org.uk/information-support/your-stories/why-music-is-great-for-your-mental-health/#:~:text=Last%20month%2C%20researchers%20found%20that,between%20music%20and%20mental%20wellbeing.")
        ]
    ],

    "cbt_link":[
        [
            InlineKeyboardButton("What is Cognitive Behavioral Therapy(CBT)❔", url="https://www.verywellmind.com/what-is-cognitive-behavior-therapy-2795747")
        ]
    ],

    "cbt_yn":[
        [
            InlineKeyboardButton("👍 Yes❕ I accept the challenge", callback_data=5)
        ],
        [
            InlineKeyboardButton("No, I am sorry.", callback_data=6)
        ]
    ],

    "expert_req":[
        [
            InlineKeyboardButton("Accept request", callback_data=1)
        ],
        [
            InlineKeyboardButton("Reject request", callback_data=0)
        ]
    ]
}

def update_chat_id(chat_id):
    try:
        with open("chat_id.csv", "a") as f:
            df = pd.read_csv("chat_id.csv")
            if chat_id in np.array(df.chat_id):
                return
            else:    
                f.write(str(chat_id) + "\n")
                logger.info(str(chat_id) + " - New user arrived")
    except:
        with open("chat_id.csv", "w") as f:
            f.write("chat_id\n")
            f.write(str(chat_id) + "\n") 

logs = {}
# Structure of logs -->  logs["chat_id"] = "label"
# Logs will store the label of the message sent to the user 

def update_messages_logs(chat_id, label):
    logs[chat_id] = label
    return

def read_file(path, read_img = True):
    if read_img == False:
        with open(path, "r") as f:
            link = f.readline()
            reply = f.read()
        return  reply, None, link
    else:
        with open(path, "r") as f:
            image = f.readline()
            link = f.readline()
            reply = f.read()
        return reply, image, link

def get_message(label):
    return message[label]


def num_handler(chat_id, num):  # handles 1,2,4 option 
    """ 
    This function - num handler is for selection of 1, 2, 4 option of the /services message option 
    then it will extract and return all the four things required to send it back to query handler function 
    in "main.py" those are:
                    reply(the text to be send as new message)
                    image(if ther is any)
                    link(to be sent with message)
                    keyboard(inline keyboard markup list)   
    """

    if logs[chat_id] == "a":
        label = service[num]
        logs[chat_id] = label #updating the label of the message which we will send
        reply = message[label]
        return reply, None, None, inline_keyboards[label]

    elif logs[chat_id] == "b":
        if num == 1:
            df = pd.read_csv("Resources/Understand_mental_health(b)/1.csv")
            df = df.values
            i = np.random.randint(0, len(df))
            link = df[i][0]
            with open("Resources/Understand_mental_health(b)/1.txt", "r") as f:
                image = f.readline()
                reply = f.read()
                
            return reply, image, link, inline_keyboards["b"]
        elif num == 2 or num == 4 or num == 5:
            reply, image, link = read_file("Resources/Understand_mental_health(b)/" + str(num) + ".txt")
            return reply, image, link, inline_keyboards["b"]

        # handels the opt no 3 
        label = mental_health_intro[num]
        logs[chat_id] = label #updating the label of the message which we will send
        
        return message[label], None, None, inline_keyboards[label]

    elif logs[chat_id] == 'c':
        if num < 11:
            reply, image, link = read_file("Resources/improve_mental_health(c)/" + str(num) + ".txt")
            return reply, image, link, inline_keyboards["c"]
        elif num == 11:
            logs[chat_id] = "a"
            return message["a"], None, None, inline_keyboards["a"]

    elif logs[chat_id] == 'b1':
        if num < 8:
            reply, image, link = read_file("Resources/diff_disorders(b1)/"+ str(num) + ".txt", read_img=False)
            return reply, image, link, inline_keyboards["b1"]
        elif num == 8:
            logs[chat_id] = "b" #going back to previous menu (b)
            return message["b"], None, None, inline_keyboards["b"]

    elif logs[chat_id] == "e":
        if num == 3: # Meditation -> Direct message w/o selection option
            reply, image, link = read_file("Resources/meditation/1.txt", read_img=False)
            return reply, image, link, inline_keyboards["e"]
        label = activities[num]
        logs[chat_id] = label #updating the label of the message which we will send
        reply = message[label]
        return reply, None, None, inline_keyboards[label]

    elif logs[chat_id] == "y":
        if num < 8:
            reply, image, link = read_file("Resources/yoga(y)/"+ str(num) + ".txt", read_img=False)
            return reply, image, link, inline_keyboards["y"]
        elif num == 8:
            logs[chat_id] = "e" #going back to previous menu (b)
            return message["e"], None, None, inline_keyboards["e"]

    elif logs[chat_id] == "w":
        if num < 7:
            reply, image, link = read_file("Resources/workout(w)/"+ str(num) + ".txt")
            return reply, image, link, inline_keyboards["w"]
        elif num == 7:
            logs[chat_id] = "e" #going back to previous menu (b)
            return message["e"], None, None, inline_keyboards["e"]



def music_thearpy(chat_id, num):
    """
        This function will return the music, message and inline keyboard list 
    """
    if num==1:
        logs[chat_id] = "mt"
        music_df = pd.read_csv("Resources/therapy(d)/music_links.csv")
        music_df = np.array(music_df)
        i = np.random.randint(0, len(music_df))
        music_link = music_df[i][0]
        reply = "Music therapy decreases pain perception, reduces the amount of pain medication needed, helps relieve depression in pain patients, and gives them a sense of better control over their pain.\n\n So, why not to try it?"
        return reply, str(music_link), inline_keyboards["mt"]
    elif num==2:
        logs[chat_id] = "d"
        return message["d"], None, inline_keyboards["d"] 


#######################  class for CBT therapy  ###########################

class cbt:   
    # cbt handles the reading of questions and giving each question one by one as string
    # Intialising the keyboards of answer
    
    daily_ans_pos_keyboard = [
        [
            InlineKeyboardButton("Almost Always", callback_data=4)
        ],
        [
            InlineKeyboardButton("Frequently", callback_data=3)
        ],
        [
            InlineKeyboardButton("Sometimes", callback_data=2)
        ],
        [
            InlineKeyboardButton("Never", callback_data=1)
        ]
    ]
    
    daily_ans_neg_keyboard = [
        [
            InlineKeyboardButton("Almost Always", callback_data=1)
        ],
        [
            InlineKeyboardButton("Frequently", callback_data=2)
        ],
        [
            InlineKeyboardButton("Sometimes", callback_data=3)
        ],
        [
            InlineKeyboardButton("Never", callback_data=4)
        ]
    ]

    weekly_ans_keyboard = [
        [
            InlineKeyboardButton("Not at all", callback_data=4)
        ],
        [
            InlineKeyboardButton("Several days", callback_data=3)
        ],
        [
            InlineKeyboardButton("More than half the days", callback_data=2)
        ],
        [
            InlineKeyboardButton("Nearly every day", callback_data=1)
        ]
    ]
    
    #Initialising stickers path to be sent at the end via get_remarks()
    happy_sticker = "Resources/Stickers/Laugh face.tgs"
    neutral_sticker = "Resources/Stickers/Neutral face.tgs"
    sad_sticker = "Resources/Stickers/Sad face.tgs"
    
    def __init__(self):
        
        self.questions = []
        self.que_label = 0
        self.score = 0
        with open("Resources/therapy(d)/daily_life_questions_pos.txt", "r") as f:
            que = f.readlines()
            random.shuffle(que)
            self.questions = [[que[i][:-1], cbt.daily_ans_pos_keyboard] for i in range(5)]
        
        with open("Resources/therapy(d)/daily_life_questions_neg.txt", "r") as f:
            que = f.readlines()
            random.shuffle(que)
            for i in range(3):
                self.questions.append([que[i][:-1], cbt.daily_ans_neg_keyboard])
                
        #Shuffling the questions list
        random.shuffle(self.questions)
        
        with open("Resources/therapy(d)/two_week_questions.txt", "r") as f:
            que = f.readlines()
            random.shuffle(que)
            for i in range(4):
                self.questions.append([que[i][:-1], cbt.weekly_ans_keyboard])
        
    def get_que(self):   # return the question as string
        try:
            que = self.questions[self.que_label][0]
            keyboard = self.questions[self.que_label][1]
            self.que_label += 1
            return que, keyboard
        except:
            return None, None

    def score_updater(self, s):
        self.score += s

    def get_remarks(self):
        if self.score > 32:
            return "<b>Congratulations, you performed well just be happy & felicitous as you always be.</b>", cbt.happy_sticker
        elif self.score <= 32 and self.score >= 20:
            return "<b>Your performance is Okay try to be happier.</b>", cbt.neutral_sticker
        else:
            return "<b>Sorry to say but your performance is not good but doesn't worry. I will help you to improve yourself. Please use the resources provided by me and follow them and you are good to go.</b>", cbt.sad_sticker

################################################################################

cbt_objects = {}
# Structure of objects :  cbt_object[chat_id] = <object of "cbt" class>
cbt_takers_count = 0

def cbt_handler(chat_id, previous_score = None, get_remarks = False):
    """ This function handles the cbt thearpy """
    lst = []
    
    if get_remarks == True:
        
        if cbt_objects[chat_id].que_label < 13:
            return "🙏 Please don't interrrupt the CBT session and answer the above question.", None
        reply, sticker = cbt_objects[chat_id].get_remarks()

        # Deleting the object of cbt() because thearpy completed
        del cbt_objects[chat_id]

        return reply, sticker

    elif previous_score == None: # Creating object and sending first question 
        cbt_objects[chat_id] = cbt()
        global cbt_takers_count
        cbt_takers_count += 1

        logger.info(str(chat_id) + " - cbt therapy started")
        
        lst.append("👉 Read the upcoming questions and indicate how much these apply to how you feel and think on a typical day.")
        que, keyboard = cbt_objects[chat_id].get_que()
        lst.append(que)
        return lst, keyboard
    
    else:
        cbt_objects[chat_id].score_updater(previous_score)

        if cbt_objects[chat_id].que_label == 8:
            lst.append(" 👉 Over the last two weeks, how often have you been bothered by any of the following upcoming problems?")
            que, keyboard = cbt_objects[chat_id].get_que()
            lst.append(que)
            return lst, keyboard

        elif cbt_objects[chat_id].que_label < 12:
            que, keyboard = cbt_objects[chat_id].get_que()
            lst.append(que)
            return lst, keyboard

        else:
            cbt_objects[chat_id].que_label += 1
            return ["Tell any good moment happend to you within last two weeks"], None

def records_updater(path, data): # Especially for doubt and issue reporting in .csv file
    try:
        with open(path, "r") as f: # for checking if the file exists or not
            pass
        with open(path, "a") as f:
            f.write(data + "\n")
        return
    except:
        with open(path, "w") as f:
            f.write("chat_id,username,data\n")
            f.write(data + "\n")
        return

def doubt_issue(chat_id, username, user_reply):
    label = logs[chat_id]
    user_reply = user_reply.replace("\n", " ")
    user_reply = user_reply.replace(",", " ")
    records_updater("Resources/Records/" + label + "s.csv", str(chat_id) + "," + username + "," + user_reply)
    
    logger.info(str(chat_id) + " - {} file updated".format(logs[chat_id]))

    logs[chat_id] = "a"
    return message[label], "Resources/Stickers/" + label + ".tgs"

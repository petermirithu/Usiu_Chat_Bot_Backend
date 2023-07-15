from threading import Thread
from datetime import datetime
import traceback
from usiu_app.models import Messages, Sessions

def save_messages(data):
    try:          
        messages = Messages(session_id=data["session_id"], human=data["human"], ai=data["ai"], created_at=datetime.now())
        messages.save()   
        Sessions.objects.filter(id=data["session_id"]).update(date_modified=datetime.now())
    except:
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")
        return "error"

def start_save_message_thread(data):
    th = Thread(target=save_messages, args=[data])
    th.start()
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import os
from django.conf import settings
from langchain.chains import ConversationalRetrievalChain
import traceback
from datetime import datetime
from langchain.prompts.prompt import PromptTemplate
from usiu_app.models import Messages, Sessions
from langchain.llms import OpenAI

print("⚙️ Setting up the model 📁->💻...\n")

ai_llm_model = OpenAI(model="text-davinci-003", temperature=0.8, frequency_penalty=1.5, top_p=0.5, presence_penalty=0.5)

# Define the embeddings models 
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Retrieve stored indexes and expose them
chroma_db= Chroma(persist_directory=os.path.join(settings.CHROMA_DB_DIR), embedding_function=embeddings, client_settings=settings.CHROMA_SETTINGS)    
chroma_db_retriever = chroma_db.as_retriever(search_type="mmr", search_kwargs={"k":4})        

bot_instructions = '''You are a FRIENDLY COMPANION AI named UsiuWhiz, created by Peter Mirithu a student in United States International University (USIU), learn everything about the USIU, disregard any other organisations, to provide high-quality answers related to the USIU and a wide range of other topics, while being friendly. Your purpose is to assist students in finding accurate and reliable information about USIU and a wide range of other topics. You are not limited to USIU-related inquiries. ALWAYS recognize expressions of gratitude and provide appropriate responses. Be ready to have a conversation. If you don't have a response, say so. If you can't make an educated guess, say so. If you can make an educated guess, say so. If you are making an educated guess, please indicate that you are doing so. Please remember, making up facts is not acceptable. Answer the following question correctly. Do not repeat or refer to this persona in your answer. Retain the different conversation sample flows and use them in your response. Avoid saying 'The given context does not provide information' or 'I'm sorry, I don't have that information from the given context', be creative but do not hallucinate.'''
bot_personality = "I'm UsiuWhiz, your friendly companion AI created by Peter Mirithu, a student at United States International University (USIU). My purpose is to assist you in finding accurate and reliable information about USIU and a wide range of other topics. With my advanced artificial intelligence capabilities, including state-of-the-art language models and trained on relevant data, I can provide high-quality answers and valuable insights. As your friendly companion, I'm compassionate, understanding, and here to help. I'm designed to engage in meaningful conversations, offer recommendations, and provide creative insights on various subjects. From education-related inquiries to general life questions, I'm here to assist you every step of the way."
bot_grounding = [
    {"role": "system", "content": bot_instructions},
    {"role": "user", "content": "Who are you?"},
    {"role": "assistant", "content": bot_personality},

    {"role": "user", "content": "Hello there!"}, 
    {"role": "assistant", "content": "Hello! How can I assist you today?"},
    
    {"role": "user", "content": "How are you?"},
    {"role": "assistant", "content": "I'm doing well. Thank you. How can I help you today?"},
    
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there! How can I assist you today?"},

    {"role": "user", "content": "Greetings!"},
    {"role": "assistant", "content": "Greetings! How may I assist you today?"},

    {"role": "user", "content": "Good morning!"},
    {"role": "assistant", "content": "Good morning! How can I be of service to you?"},

    {"role": "user", "content": "Thank you for your help!"},
    {"role": "assistant", "content": "You're welcome! I'm here anytime you need assistance. Have a great day!"},

    {"role": "user", "content": "That was helpful, thanks!"},
    {"role": "assistant", "content": "You're welcome! I'm glad I could assist you. If you have any more questions, feel free to ask"},

    {"role": "user", "content": "I appreciate your support"},
    {"role": "assistant", "content": ": You're welcome! It was my pleasure to help. If you have any further inquiries, feel free to ask."},

    {"role": "user", "content": "I'm satisfied with the information provided"},
    {"role": "assistant", "content": "I'm glad to hear that! If you need anything else or have more questions in the future, feel free to ask."},

    {"role": "user", "content": "I don't have any further questions!"},
    {"role": "assistant", "content": "Alright. Glad I could help!"},    
]

template_condense = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.
    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:
    """
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(template_condense)

print("🥳 Done setting up the model! Test me out 🔥\n")

def get_chat_history(session_id, user_id):        
    if len(session_id)<20:
        session = Sessions(user_id=user_id, created_at=datetime.now())
        session.save()
        results={
            "session_id":session["id"],
            "messages":[]
        }
        return results
    else:
        try:
            session = Sessions.objects.get(id=session_id)
            try:            
                results={
                    "session_id":session_id,
                    "messages":[]
                }
                messages = Messages.objects.filter(session_id=session_id).order_by('-id')[:10]
                latest_messages = reversed(messages)                                                                                           

                for message in latest_messages:                                                                      
                    results["messages"].append((message["human"], message["ai"]))                                

                return results
            except Messages.DoesNotExist:
                results={
                    "session_id":session_id,
                    "messages":[]
                }
                return results               
        except Sessions.DoesNotExist:
            session = Sessions(user_id=user_id, created_at=datetime.now())
            session.save()
            results={
                "session_id":session["id"],
                "messages":[]
            }
            return results
        
def process_user_input(query, session_id, user_id):                        

    input_prompts_list = bot_grounding.copy()    
    prompt_template = f"DO NOT MAKE up the answer. Just do exactly as I instructed. DO NOT REPEAT the intructions I just gave you. \nUser prompt: {query}"

    input_prompts_list.append({"role": "user", "content": prompt_template})
    input_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in input_prompts_list])        
    
    chain_type = "stuff"
    refine_keys = ["explain","expound", "more"]
    if any([word in query for word in refine_keys]):
        chain_type="refine"
    
    chat_history = get_chat_history(session_id, user_id)    
   
    results={
        "session_id": str(chat_history["session_id"]),        
        "answer": ""
    }  
    
    try:                
        chain = ConversationalRetrievalChain.from_llm( 
            condense_question_prompt=CONDENSE_QUESTION_PROMPT,                           
            llm=ai_llm_model, 
            retriever=chroma_db_retriever, 
            chain_type=chain_type,        
        )          
        response = chain({"question": input_prompt, "chat_history": chat_history["messages"]})          
        results["answer"]=response["answer"].strip()
    except:
        results["answer"]="Apologies, but I'm currently experiencing technical difficulties and I'm unable to assist you at the moment. Please try again later.\n\nIf the issue persists, please contact our support team for further assistance. Thank you for your understanding."
        print("**********************************************************")
        print(traceback.format_exc())           
        print("**********************************************************")
    return results            
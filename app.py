from flask import Flask, request
import requests
from newspaper import Article
import random
import string 
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import numpy as np
import warnings
from lxml import html
from googlesearch import search
from bs4 import BeautifulSoup

app = Flask(__name__)

FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
VERIFY_TOKEN = ''# <paste your verify token here>
PAGE_ACCESS_TOKEN = ''# paste your page access token here>"

nltk.download('punkt', quiet=True)







def greeting_response(text):
  text = text.lower()
  bot_greetings = ["howdy","hi", "hey", "what's good",  "hello","hey there"]
  #Greeting input from the user
  user_greetings = ["hi", "hello",  "hola", "greetings",  "wassup","hey"] 

  for word in text.split():
    if word in user_greetings:
      return random.choice(bot_greetings)




def index_sort(list_var):
    length = len(list_var)
    list_index = list(range(0, length))
    x  = list_var
    for i in range(length):
        for j in range(length):
            if x[list_index[i]] > x[list_index[j]]:
                temp = list_index[i]
                list_index[i] = list_index[j]
                list_index[j] = temp
    return list_index





# Generate the response
def bot_response(user_input,sentence_list):
    user_input = user_input.lower()
    sentence_list.append(user_input)
    bot_response=''
    cm = CountVectorizer().fit_transform(sentence_list)
    similarity_scores = cosine_similarity(cm[-1], cm)
    flatten = similarity_scores.flatten()
    index = index_sort(flatten)
    index = index[1:]
    response_flag=0

    j = 0
    for i in range(0, len(index)):
      if flatten[index[i]] > 0.0:
        bot_response = bot_response+' '+sentence_list[index[i]]
        #print(bot_response)
        response_flag = 1
        j = j+1
      if j > 2:
        break  
    if(response_flag==0):
        #print(1)
        return None
    sentence_list.remove(user_input)
       
    return bot_response



def Search(query):
    search_result_list = list(search(query, tld="co.in", num=10, stop=10, pause=1))
    return search_result_list


def tokened_text(link):
    #print(link)
    article = Article(link)
    article.download() 
    article.parse() 
    article.nlp()
    #print(article.text)
    sentence_list = nltk.sent_tokenize(article.text)
    #print(sentence_list)
    return sentence_list
    


def Bot(message):
    #print("Gaming Bot: I am GAMING BOT. I will answer your queries about ANY GAME. If you want to exit, type Bye!")
    exit_list = ['exit', 'see you later','bye', 'quit', 'break']
    user_input = message
    if(user_input.lower() in exit_list):
      #print("Gaming Bot: Chat with you later !")
        return "Chat with you later !"
    else:
      if(greeting_response(user_input)!= None):
        #print("Gaming Bot: "+greeting_response(user_input))
          return greeting_response(user_input)
      else:              
            i=0
            link=Search(user_input)
            #print(link)
            if 'youtube' in user_input.lower() or 'link' in user_input.lower() or 'video' in user_input.lower():
                #print("Gaming Bot: "+link[0])
                return link[0]
            else:                
                while True:
                    #print(link[i])
                    lis=tokened_text(link[i])
                    if bot_response(user_input, lis) != None:
                        break
                    i+=1
                #print("Gaming Bot: "+bot_response(user_input,lis))
                return bot_response(user_input,lis)



def send_message(recipient_id, text):
    """Send a response to Facebook"""
    payload = {
        'message': {
            'text': text
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }

    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }

    response = requests.post(
        FB_API_URL,
        params=auth,
        json=payload
    )

    return response.json()


def get_bot_response(message):
    """This is just a dummy function, returning a variation of what
    the user said. Replace this function with one connected to chatbot."""
    return Bot(message)


def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"

def respond(sender, message):
    """Formulate a response to the user and
    pass it on to a function that sends it."""
    response = get_bot_response(message)
    send_message(sender, response)


def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))


@app.route("/webhook")
def listen():
    """This is the main function flask uses to 
    listen at the `/webhook` endpoint"""
    if request.method == 'GET':
        return verify_webhook(request)

    if request.method == 'POST':
        payload = request.json
        event = payload['entry'][0]['messaging']
        for x in event:
            if is_user_message(x):
                text = x['message']['text']
                sender_id = x['sender']['id']
                respond(sender_id, text)

        return "ok"
    
if __name__ == "__main__":
    app.run(debug=True)
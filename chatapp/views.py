from itertools import count
from urllib import response
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.files import File
from .models import *

###########################################################################
import colorama
from colorama import Fore
import wikipedia as wk
import nltk
#nltk.download('omw-1.4')
#nltk.download('averaged_perceptron_tagger')
from nltk.corpus import stopwords
nltk.download('stopwords')
import random
import re, string, unicodedata
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer

from collections import defaultdict
import warnings

warnings.filterwarnings("ignore")
#nltk.download('punkt')
#nltk.download('wordnet')
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
from django.views.decorators.csrf import csrf_exempt

data = open('files//questions.txt', 'r', errors='ignore')
raw = data.read()
raw = raw.lower()


sent_tokens = nltk.sent_tokenize(raw)

def wikipedia_data(input):
    reg_ex = re.search('tell me about (.*)', input) #or re.search('what is (.)', input)
    try:
        if reg_ex:
            topic = reg_ex.group(1)
            wiki = wk.summary(topic, sentences = 3)
            return wiki
    except Exception as e:
            print("No content has been found")

def Normalize(text):
    remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
    # word tokenization
    word_token = nltk.word_tokenize(text.lower().translate(remove_punct_dict))

    # remove ascii
    new_words = []
    for word in word_token:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)

    # Remove tags
    rmv = []
    for w in new_words:
        text = re.sub("&lt;/?.*?&gt;", "&lt;&gt;", w)
        rmv.append(text)

    # pos tagging and lemmatization
    tag_map = defaultdict(lambda: wn.NOUN)
    tag_map['J'] = wn.ADJ
    tag_map['V'] = wn.VERB
    tag_map['R'] = wn.ADV
    lmtzr = WordNetLemmatizer()
    lemma_list = []
    rmv = [i for i in rmv if i]
    for token, tag in nltk.pos_tag(rmv):
        lemma = lmtzr.lemmatize(token, tag_map[tag[0]])
        lemma_list.append(lemma)
    return lemma_list


welcome_input = ["what's up","hey", "hello", "hi", "greetings",]
welcome_response = ["hi", "hey",  "hi there", "hello",]


def welcome(user_response):
    for word in user_response.split():
        if word.lower() in welcome_input:
            return random.choice(welcome_response)


def generateResponse(user_response, raw):
    robo_response = ''
    sent_tokens.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=Normalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx = vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    text = re.sub(r'[^\w\s]', '', user_response)
    text_tokens = text.split(" ")
    tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]
    print(tokens_without_sw)
    # print("User response: {b}".format(b=user_response))
    counts = []
    for i in tokens_without_sw:
        tf=raw.count(i)
        print("Count : {a}".format(a=tf))
        counts.append(tf)
    m =  max(counts)
    req_tfidf = flat[-2]
    if(req_tfidf==0) or "tell me about" in user_response:#or "what is " in user_response:
        if user_response:
            robo_response = wikipedia_data(user_response)        
    else:
        robo_response = robo_response + sent_tokens[idx]
        item = '\n"Please, tell me more specificly"'
        if m>1:
            robo_response = "<pre style='background-color: transparent; border: none; color:#fff; font-size: 1.5rem; font-weight: bold; font-family: sans-serif;'>{robo_res}<br> <font color='cyan'>{}</font></pre>".format(item, robo_res=robo_response)

    return robo_response


@csrf_exempt
def chatbot(request):
    flag = True
    while (flag == True):
        if request.method == 'POST':
            user_response = request.POST['question']
            user_response = user_response.lower()
            if (user_response not in ['bye', 'shutdown', 'exit', 'quit']):
                if (user_response == 'thanks' or user_response == 'thank you'):
                    flag = False
                    mydict = "You are welcome.."
                else:
                    if (welcome(user_response) != None):
                        mydict = welcome(user_response)
                    else:
                        mydict = generateResponse(user_response, raw)
                        sent_tokens.remove(user_response)
            else:
                flag = False
                mydict =  "Thanks for connecting me. Bye!!! "
        print(response)
        return JsonResponse({"response": mydict})
#############################################################################

def home(request):
    return render(request, 'index.html')
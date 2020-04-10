# -*- coding: utf-8 -*-
"""main

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yf9NjR01mGGsvfCNFDXKF07PMInINfD9
"""

import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy as np
import tflearn
import tensorflow
import random
import json
import pickle

with open("intents.json") as file:
    data = json.load(file)
try:
    with open("data.pickle","rb") as f:
        words,labels,training,output = pickle.load(f)
except:
    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w !="?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x,doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = np.array(training)
    output = np.array(output)

    with open("data.pickle","wb") as f:
        pickle.dump((words,labels,training,output),f)

tensorflow.reset_default_graph()

net = tflearn.input_data(shape=[None,len(training[0])])
net = tflearn.fully_connected(net,8)
net = tflearn.fully_connected(net,8)
net = tflearn.fully_connected(net,len(output[0]),activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)

try:
    model.load("model.tflearn")
except:
    model.fit(training,output,n_epoch=1000,batch_size=8,show_metric=True)
    model.save("model.tflearn")

def bag_of_words(s,words):
    bag = [0 for _ in range(len(words))]
    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]
    for se in s_words:
        for i,w in enumerate(words):
            if w == se:
                bag[i] = 1
    return np.array(bag)

def chat():
    print("Hello! I am your chatbot I will answer your queries")
    while True:
        inp = input("You: ")
        if inp == "quit":
            break
        results = model.predict([bag_of_words(inp,words)])[0]
        results_index = np.argmax(results)
        tag = labels[results_index]
        if tag == 'action':
            fetch_data(1)
        elif tag == 'history':                  
            fetch_data(2)
        elif tag == 'anthology':
            fetch_data(3)
        elif results[results_index] > 0.6:
            for x,tg in enumerate(data["intents"]):
                if tg['tag'] == tag:
                    responses = tg['responses']
            print(random.choice(responses))
        else:
            print("I didn't get that, kindly be more specific!")

def fetch_data(s):
    book = open("books.txt")
    for n,name in enumerate(book):
        if n==(s-1):
            print(name,end="")

chat()

for x, tg in enumerate(data['intents']):
    print(x,tg)
    print(data['intents'])
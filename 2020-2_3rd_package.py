# -*- coding: utf-8 -*-
"""package4_syp

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1a8MXqVLw_8jAOLeJyvks4Dw2xhe2zvHV
"""

# 드라이브 연동
from google.colab import drive
drive.mount('/content/drive')

direc = '/content/drive/My Drive/패키지/'

"""0번"""

#0 코드
import os
import pandas as pd
import numpy as np
import tensorflow as tf
import keras
from keras.layers import Dense
from keras import models
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from sklearn.feature_extraction.text import CountVectorizer
from keras.optimizers import Adam
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer, text_to_word_sequence
import gensim

#os.chdir("your dir")

dat = pd.read_csv(direc + "dat.csv")
dat = dat.iloc[:,1:]

dat = shuffle(dat)

dat['article'] = dat['article'].str.replace('<[^>]*>'," ")
dat['article'] = dat['article'].str.replace('[^A-Za-z]'," ")

dat['class'] = dat['class'].replace('film',0)
dat['class'] = dat['class'].replace('music',1)
dat['class'] = dat['class'].replace('economics',2)
dat['class'] = dat['class'].replace('politics',3)

x_train, x_test, y_train, y_test = train_test_split(dat['article'], dat['class'], test_size = 0.2,
                                                   shuffle = False, random_state = 777)

c_vec = CountVectorizer( stop_words = 'english', max_features = 6000, binary = True )

train_x = c_vec.fit_transform(x_train)
test_x = c_vec.transform(x_test)

train_y = to_categorical(y_train)
test_y = to_categorical(y_test)

"""1번(DNN)

1-1번
"""

model = models.Sequential()

model.add(Dense(23, activation = 'relu', input_shape = (6000,) ))
model.add(Dense(23, activation = 'relu'))

model.add(Dense(4, activation = 'softmax'))

model.compile(optimizer = Adam(lr = 0.0005), loss = 'categorical_crossentropy', metrics = ['accuracy'])

history = model.fit(train_x, train_y, validation_split = 0.2, epochs = 100, batch_size = 100)

import matplotlib
import matplotlib.pyplot as plt

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Training and validation loss')
plt.ylabel('loss')
plt.xlabel('epochs')
plt.legend(['loss', 'val_loss'])
plt.show()

#오버피팅 문제 발생하였기에, 얼리스탑이 필요하다.

"""1-2번"""

x_train, x_test, y_train, y_test = train_test_split(dat['article'], dat['class'], test_size = 0.2,
                                                   shuffle = False, random_state = 777)

c_vec = CountVectorizer( stop_words = 'english', max_features = 4000, binary = True ) #6000 -> 4000으로 바꿔줌

train_x = c_vec.fit_transform(x_train)
test_x = c_vec.transform(x_test)

train_y = to_categorical(y_train)
test_y = to_categorical(y_test)

from tensorflow.keras.callbacks import EarlyStopping
from keras.layers.advanced_activations import LeakyReLU


model = models.Sequential()

model.add(Dense(10, activation = 'relu', input_shape = (4000,) ))
model.add(Dense(10, activation = 'relu'))

model.add(Dense(4, activation = 'softmax'))

model.compile(optimizer = Adam(lr = 0.0005), loss = 'categorical_crossentropy', metrics = ['accuracy'])

es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=7)

history = model.fit(train_x, train_y, validation_split = 0.2, epochs = 100, batch_size = 70, callbacks=[es])

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Training and validation loss')
plt.ylabel('loss')
plt.xlabel('epochs')
plt.legend(['loss', 'val_loss'])
plt.show()

"""2번(CNN)

2-1. word2vec설치
"""

#!pip install word2vec

"""2-2. 주어진 코드를 실행하여 cnn에 들어갈 임베딩 데이터셋을 만드세요."""

#!pip install gensim
from gensim.models.word2vec import Word2Vec

!wget -P /root/input/ -c "https://s3.amazonaws.com/dl4j-distribution/GoogleNews-vectors-negative300.bin.gz"

tnz = Tokenizer()
dat_emd = dat['article']
dat_emd = dat['article'].apply(lambda x: ' '.join([w for w in x.split() if len(w)>3]))

total = [sent.split() for sent in dat_emd]
total = sum(total,[])

tnz.fit_on_texts(total)


v_size = len(tnz.word_index)+1
words = dat['article'].apply(lambda x: ' '.join([w for w in x.split() if len(w)>3]))
words = [sent.split() for sent in words ]
w_len = []
for sent in words:
    w_len.append( [len(w) for w in sent]  )
w_len = sum(w_len,[])
max_len = max(w_len)

emd_set = tnz.texts_to_sequences(dat_emd)

padded = pad_sequences(emd_set, maxlen = max_len, padding = 'post')

#os.chdir('')
EMBEDDING_FILE = '/root/input/GoogleNews-vectors-negative300.bin.gz'
word2vec_model = gensim.models.KeyedVectors.load_word2vec_format(EMBEDDING_FILE, binary=True)  

embedding_matrix = np.zeros((v_size, 300))

def get_vector(word):
    if word in word2vec_model:
        return word2vec_model[word]
    else:
        return None
    
for word, i in tnz.word_index.items():
    temp = get_vector(word) 
    if temp is not None: 
        embedding_matrix[i] = temp
        
dat_x = padded
dat_y = dat['class']

x_train, x_test, y_train, y_test = train_test_split(padded,dat_y, test_size = 0.2, shuffle = False,
                                                   random_state = 777)

y_train = to_categorical(y_train)
y_test = to_categorical(y_test)

"""2-3 주어진 코드에서 하이퍼 파라미터를 자유롭게 튜닝하여 최고의 성능을 보이
세요
"""

#원본
import matplotlib.pyplot as plt
from keras.layers import Embedding
from keras.layers import Conv1D
from keras.layers import MaxPooling1D
from keras.layers import Flatten
model = models.Sequential()

model.add( Embedding(v_size, 300, weights = [embedding_matrix], input_length = max_len, trainable = False) )

model.add(Conv1D( filters = 32, kernel_size = 6, activation = 'relu' ))
model.add(MaxPooling1D(pool_size = 2))

model.add(Flatten())

model.add(Dense(16, activation = 'relu'))
model.add(Dense(16, activation = 'relu'))

model.add(Dense(4, activation = 'softmax'))

model.compile( optimizer = Adam(lr = 0.0005), loss = 'categorical_crossentropy', metrics = ['accuracy'])

history = model.fit(x_train, y_train, validation_split = 0.2, epochs = 10, batch_size = 100 )
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.legend(['train_Accuracy','val_accuracy'],loc='upper')
plt.show()

#변화_GlobalMaxPooling1D 사용 + he_uniform + leakyRelu  +batch_size 반으로 줄임 _accuracy로 비교했을 때 더 좋은 성능을 보임

from keras.layers import GlobalMaxPooling1D
from keras.layers.advanced_activations import LeakyReLU
model = models.Sequential()

model.add( Embedding(v_size, 300, weights = [embedding_matrix], input_length = max_len, trainable = False) )

model.add(Conv1D( filters = 32, kernel_size = 6, activation = 'relu' ))
model.add(GlobalMaxPooling1D(data_format='channels_last'))

keras.initializers.he_uniform(seed=None)
lrelu = lambda x: keras.activations.relu(x,alpha=0.1)
model.add(Dense(16, activation = lrelu))
model.add(Dense(16, activation = lrelu))

model.add(Dense(4, activation = 'softmax'))

model.compile( optimizer = Adam(lr = 0.0005), loss = 'categorical_crossentropy', metrics = ['accuracy'])

history = model.fit(x_train, y_train, validation_split = 0.2, epochs = 10, batch_size = 50 )
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.legend(['train_Accuracy','val_accuracy'],loc='upper')
plt.show()
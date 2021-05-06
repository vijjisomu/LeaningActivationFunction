# -*- coding: utf-8 -*-
"""breast_cancer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ScNzGFXzkKQxAm_4lfrCXH-VwLnTFKnv
"""

!pip install keras-tuner

import tensorflow as tf
import pandas as pd
from tensorflow import keras
import numpy as np
from keras.layers import Dense, Flatten
from keras.models import Sequential
import kerastuner as kt
from kerastuner import RandomSearch
from kerastuner.engine.hyperparameters import HyperParameters
import matplotlib.pyplot as plt
from sklearn.metrics import f1_score
from sklearn import datasets

breast_cancer = datasets.load_breast_cancer()

data=pd.DataFrame(breast_cancer.data)
data.head()
target=pd.DataFrame(breast_cancer.target)
target.head()

df=pd.concat([data,target],axis=1)
df.head()

df.isnull().sum()

df.describe()

import seaborn as sns
sns.heatmap(df.corr(),annot=True)

x=df.iloc[:,0:30].values
y=df.iloc[:,30].values

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)

print(X_train.shape,X_test.shape)
np.unique(y_train)

from sklearn.preprocessing import StandardScaler
sc=StandardScaler()
X_train=sc.fit_transform(X_train)
X_test = sc.transform(X_test)

def build_model(hp):  
  model = Sequential()
  #model.add(Flatten(input_shape=(28,28)))
  model.add(Dense( units=hp.Int(
                    'units',
                    min_value=32,
                    max_value=1000,
                    step=32,
                    default=128),
        activation=hp.Choice('act_'+str(),['relu','tanh','sigmoid'],default='relu')))
  model.add(Dense(2, activation='softmax'))

  
  model.compile(optimizer=keras.optimizers.Adam(hp.Choice('learning_rate', values=[1e-2, 1e-3])), loss='sparse_categorical_crossentropy', metrics=['accuracy']) 

  return model

tuner=kt.Hyperband(build_model,
                          objective='val_accuracy',
                          max_epochs=5,directory='outp2',project_name="Auto-AF")

stop_early = tf.keras.callbacks.EarlyStopping(monitor='val_loss',patience=5)

tuner.search(X_train,y_train,epochs=2,validation_split=0.2)

tuner.search_space_summary()

best_hps=tuner.get_best_hyperparameters(num_trials=1)[0]

print(f""" The optimal units in dense layer is {best_hps.get('units')} the optimal learning rate is {best_hps.get('learning_rate')} and the best activation function is {best_hps.get('act_')}""")

model=tuner.hypermodel.build(best_hps)
history =model.fit(X_train,y_train,epochs=30, validation_split=0.3, initial_epoch=3)

history.history??

loss_train = history.history['loss']
plt.plot(loss_train, 'g', label='loss')
plt.title('loss vs epochs')
plt.xlabel('Epoch')
plt.ylabel('loss')
plt.legend()
plt.show()

y_pred=model.predict(X_test)
y_pred[0]

test_pred_labels = np.argmax(y_pred, axis=-1)

test_pred_labels.shape

model_eval=model.evaluate(X_test,y_test)
print("[test loss,test accuracy]:",model_eval)

f1score = f1_score(y_test, test_pred_labels)
print(f1score)


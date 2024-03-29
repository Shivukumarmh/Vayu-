# -*- coding: utf-8 -*-
"""Untitled3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-Hpe1OwoKxFXpAqrLq2Kew5KZ1Glot15
"""

pip install flask flask-wtf

pip install gunicorn

from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Load the dataset
DATA_PATH = "/content/Training.csv"
data = pd.read_csv(DATA_PATH).dropna(axis=1)

# Encoding labels
encoder = LabelEncoder()
data["prognosis"] = encoder.fit_transform(data["prognosis"])

# Features and target variable
X = data.iloc[:, :-1]
y = data.iloc[:, -1]

# Initialize models
final_svm_model = SVC().fit(X, y)
final_nb_model = GaussianNB().fit(X, y)
final_rf_model = RandomForestClassifier(random_state=18).fit(X, y)

# Symptoms index and prediction classes
symptom_index = {symptom: index for index, symptom in enumerate(X.columns.values)}
predictions_classes = encoder.classes_

class SymptomsForm(FlaskForm):
    symptoms = TextAreaField('Enter Symptoms (comma-separated)', validators=[DataRequired()])
    submit = SubmitField('Predict')

def predict_disease(symptoms):
    symptoms = symptoms.split(",")
    input_data = [1 if symptom in symptom_index else 0 for symptom in symptoms]

    input_data = np.array(input_data).reshape(1, -1)

    rf_prediction = encoder.inverse_transform([final_rf_model.predict(input_data)[0]])[0]
    nb_prediction = encoder.inverse_transform([final_nb_model.predict(input_data)[0]])[0]
    svm_prediction = encoder.inverse_transform([final_svm_model.predict(input_data)[0]])[0]

    predictions, counts = np.unique([rf_prediction, nb_prediction, svm_prediction], return_counts=True)
    final_prediction = predictions[np.argmax(counts)]

    predictions = {
        "rf_model_prediction": rf_prediction,
        "naive_bayes_prediction": nb_prediction,
        "svm_model_prediction": svm_prediction,
        "final_prediction": final_prediction
    }

    return predictions

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SymptomsForm()

    if form.validate_on_submit():
        symptoms_input = form.symptoms.data
        predictions = predict_disease(symptoms_input)
        return render_template('result.html', form=form, predictions=predictions)

    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
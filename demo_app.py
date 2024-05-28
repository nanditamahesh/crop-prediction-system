import streamlit as st
import boto3
import os
import requests
import tqdm
import re
import pandas as pd
import numpy as np
import pickle
import warnings
import h5py as h5

from decimal import Decimal
from boto3.dynamodb.conditions import Key
from keras.models import load_model

st.set_page_config(page_title="Crop Recommender", page_icon="🌿", layout='centered', initial_sidebar_state="collapsed")
dynamo_client  =  boto3.resource(service_name = 'dynamodb',region_name = 'ap-northeast-1', aws_access_key_id = '', aws_secret_access_key = '') #Enter key codes
dht3 = dynamo_client.Table('dht_rain')
response = dht3.query(
        KeyConditionExpression=Key("date").eq("2023-04-11"),
        ScanIndexForward=False,  # set to false to get the latest record
        Limit=1  # limit to only 1 result
    )

def load_model(modelfile):
    loaded_model = pickle.load(open(modelfile, 'rb'))
    return loaded_model

def get_latest_temp():
    temp = dict1['temperature']
    temp_str = str(temp)+" "+chr(176)+"C"
    return temp_str

def get_latest_hum():
    hum = dict1['humidity']
    hum_str = str(hum)+"%"
    return hum_str

def get_latest_rain():
    rain = dict1['rainfall'] - 400
    rain_str = str(rain)+" mm"
    return rain_str

def main():
    # title
    html_temp = """
    <div>
    <h1 style="color:#576CBC;text-align:center;font-family:monospace ;">Crop Recommendation System  🌱 </h1>
    </div>
    """
    button_style = """
    <style>
        .stButton > button {
            background-color: darkgreen;
        }
        .stButton button:hover {
        background-color: darkgreen;
        color: white;
        border-color: darkgreen;
    }
    </style>
"""
    st.markdown(html_temp, unsafe_allow_html=True)
    
    cur_temp = '<p style = "font-family:sans-serif;">Current Temperature: '
    st.markdown(cur_temp, unsafe_allow_html=True)
    ph_t = st.empty()
    cur_hum = '<p style = "font-family:sans-serif;">Current Humidity: '
    st.markdown(cur_hum, unsafe_allow_html=True)
    ph_h = st.empty()
    cur_rain = '<p style = "font-family:sans-serif;">Current Rainfall Level: '
    st.markdown(cur_rain, unsafe_allow_html=True)
    ph_r = st.empty()
    
    if st.button("Fetch Values from AWS"):
        temp_str = get_latest_temp()
        ph_t.text(temp_str)
        hum_str = get_latest_hum()
        ph_h.text(hum_str)
        rain_str = get_latest_rain()
        ph_r.text(rain_str)
    st.markdown(button_style, unsafe_allow_html=True)
    
    #ML Part
    values=response['Items']
    dict1 = values[0]
    temp = dict1['temperature']
    hum = dict1['humidity']
    rain = dict1['rainfall']
    temp_fl = float(temp)
    hum_fl = float(hum)
    rain_fl = float(rain)
    st.header("Enter values")
    N = st.number_input("Nitrogen", 1,10000)
    P = st.number_input("Phosporus", 1,10000)
    K = st.number_input("Potassium", 1,10000)
    ph = st.number_input("Ph", 0.0,100000.0)
    feature_list = [N, P, K, temp_fl, hum_fl, ph, rain_fl]
    single_pred = np.array(feature_list).reshape(1,-1)
    if st.button('Predict Crop'):
        loaded_model = load_model('myModel')
        prediction = loaded_model.predict(single_pred)
        st.header('''Results 🔍 ''')
        st.success(f"{prediction.item().title()} is recommended by the A.I for your farm.")
        
    st.write("Made by Shreya and Nandita")
    
if __name__ == '__main__':
    main()
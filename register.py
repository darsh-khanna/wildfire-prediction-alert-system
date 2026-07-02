import streamlit as st
import joblib
import requests
from PIL import Image
import base64
import pandas as pd
from datetime import datetime
import os
import mysql.connector as sql
import subprocess

def save_to_mysql(phone, name, location, temperature, humidity, pollution, risk):
        mycon = sql.connect(host="localhost", user="root", passwd="JoelRoot1319", database="USERS")
        cursor = mycon.cursor()
        query = "INSERT INTO USERS (phone, name, location) VALUES ('{}', '{}', '{}');".format(phone, name, location)
        cursor.execute(query)
        mycon.commit()
        if mycon.is_connected:
            print("Connectersd")
        else:
            print("sefgffhdkjd")
        cursor.close()
        mycon.close()
        return True
save_to_mysql("rwer","wR","RWFER","WR","R","WE","E")
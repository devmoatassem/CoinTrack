import csv
from datetime import datetime
import pytz
import subprocess
import urllib
import uuid
import os
import sqlite3
from flask import redirect, render_template, session
from functools import wraps





def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("uid") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def pkr(value):
    """Format value as USD."""
    return f"{value:,.2f}PKR"


def create_db(path,id,username): #Enter path like this "../Database/user-databases"
    try:
        directory_path = (f"{path}/{id}")
        if not os.path.exists(directory_path):
            os.makedirs(f"{path}/{id}")
            conn = sqlite3.connect(f"{path}/{id}/{username}.db")
            
            # Close the database connection when done
            conn.close()
            return True
        elif not os.path.exists(f"{directory_path}/{username}.db") and os.path.exists(directory_path):
            conn = sqlite3.connect(f"{path}/{id}/{username}.db")
            conn.close()
            return True
        else:
            return False
    except Exception as e:
        return False
    
def get_time_stamp():
    # from datetime import datetime
    # Get the current date and time
    current_datetime = datetime.now()
    # Format the datetime as a string in the desired format
    formatted_timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_timestamp

def querry_table(path,id,username,table_name):
    try:
        conn = sqlite3.connect(f"{path}/{id}/{username}.db")
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()
        conn.close()
        
        return rows
    except Exception as e:
        print(e)
        return False




def extract_date_info(date_string):
    try:
        # Parse the input string as a datetime object
        date_obj = datetime.strptime(date_string, "%Y-%m-%d")

        # Extract the date, year, and month separately
        extracted_date = date_obj.strftime("%d")
        extracted_year = date_obj.strftime("%Y")
        extracted_month = date_obj.strftime("%m")

        return extracted_date, extracted_year, extracted_month

    except ValueError:
        # Handle invalid date format
        return None, None, None


import csv
import datetime
import pytz
import requests
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
        if session.get("user_id") is None:
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
    from datetime import datetime
    # Get the current date and time
    current_datetime = datetime.now()
    # Format the datetime as a string in the desired format
    formatted_timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_timestamp
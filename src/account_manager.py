import json
from reader import *

FILE_PATH = 'dataset/users.json'

def create_account(username, password, repeat_password, access_level):
    data = load_json(FILE_PATH)

    errors = []

    if username in data[]



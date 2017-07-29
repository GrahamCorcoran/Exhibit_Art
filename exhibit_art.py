import praw
import config
import json
import time

def login():
    """
    Returns a reddit instance using your bot login information in config.py
    Usage example: r = login()
    """
    r = praw.Reddit(username=config.username,
                password=config.password,
                client_id=config.client_id,
                client_secret=config.client_secret,
                user_agent=config.user_agent)
    return r


def add_tlc(tlc):
    """
    Takes a top level comment and '...'
    """
    threadid = tlc.submission
    author = tlc.author
    commentid = tlc


def write_to_json(data):
    with open(config.filename, 'w') as f:
        json.dump(data, f, indent=4)


def user_check(author):
    """
    :param author: String of a Reddit Username
    :return: True if author is in json file, else false.
    """
    with open("subreddit_data.json", "r") as f:
        subreddit_data = json.load(f)
        if author in subreddit_data["Users"]:
            subreddit_data["Users"][author]["TLC Count"] += 1
            subreddit_data["Users"][author]["Flair"] = "Testity Test"
            print("Found!")
        else:
            subreddit_data["Users"][author] = {}
            subreddit_data["Users"][author]["TLC Count"] = 1
            subreddit_data["Users"][author]["Flair"] = "Testity test"
            print("Not found, created for next time!")
        write_to_json(subreddit_data)

user_check("leftpig")



r = login()
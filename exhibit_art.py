import praw
import config
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


r = login()
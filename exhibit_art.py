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


def add_comment(comment):
    """
    Takes a top level comment and adds it to filename (set in config).
    """
    with open(config.filename, "r") as f:
        subreddit_data = json.load(f)
        if comment in subreddit_data["Comments"]:
            pass
        else:
            subreddit_data["Comments"][comment] = True
            write_to_json(subreddit_data)


def write_to_json(data):
    """
    Writes data to filename (set in config).
    """
    with open(config.filename, 'w') as f:
        json.dump(data, f, indent=4)


def user_check(author):
    """
    :param author: String of a Reddit Username
    :return: True if author is in filename (set in config), else false.
    """
    with open(config.filename, "r") as f:
        subreddit_data = json.load(f)
        if author in subreddit_data["Users"]:
            return True
        else: return False


def comment_check(commentid):
    """
    :param commentid: CommentID to check.
    :return: True if CommentID is in filename, else false.
    """
    with open(config.filename, "r") as f:
        subreddit_data = json.load(f)
        return True if commentid in subreddit_data["Comments"] else False


def user_tracker(author):
    with open(config.filename, "r") as f:
        user = str(author)
        subreddit_data = json.load(f)
        if user in subreddit_data["Users"]:
            subreddit_data["Users"][user]["TLC Count"] += 1
            subreddit_data["Users"][user]["Flair"] = "Testity Test"
            print("Found!")
        else:
            subreddit_data["Users"][user] = {}
            subreddit_data["Users"][user]["TLC Count"] = 1
            subreddit_data["Users"][user]["Flair"] = "Testity test"
            print("Not found, created for next time!")
        write_to_json(subreddit_data)
    pass


# Main function very incomplete.
def main(r):
    subreddit = r.subreddit("Exhibit_Art")
    for comment in subreddit.comments(limit=100):
        # If comment already has been worked; continues to next.
        if comment_check(str(comment)):
            continue
        # Adds comment to list of worked comments.
        add_comment(str(comment))
        # If comment isn't top level comment, ignores.
        if not comment.is_root:
            continue
        # Verifies that this is in fact a weekly contribution thread.
        # ** This also causes massive slowdown, find out if there's a way to fix that.
        if "contribution" not in comment.submission.link_flair_text.lower():
            continue
        print("We've passed all our validation so far.")
        user_tracker(comment.author)


        print("This is a top level comment.")





"""
    with open(config.filename, "r") as f:
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
    pass
"""


r = login()

main(r)



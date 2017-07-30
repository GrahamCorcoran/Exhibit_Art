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
            subreddit_data["Comments"].append(comment)
            write_to_json(subreddit_data)


def change_flair(flair_text, tlc_count):
    try:
        flair = flair_text.split(" - ")[0] + " - " + str(tlc_count)
        if not flair_text.isalpha():
            flair = str(tlc_count)
    except AttributeError:
        flair = str(tlc_count)
    return flair


def set_flair(subreddit):
    with open(config.filename, "r") as f:
        subreddit_data = json.load(f)
        for user in subreddit_data['Users']:
            flair = subreddit_data['Users'][user]['Flair']
            subreddit.flair.set(user, flair)



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


def user_tracker(comment):
    with open(config.filename, "r") as f:

        user = str(comment.author)
        submission = str(comment.submission)
        subreddit_data = json.load(f)

        # If a user already exists
        if user in subreddit_data["Users"]:
            if submission not in subreddit_data["Users"][user]["Threads Participated"]:
                subreddit_data["Users"][user]["Threads Participated"].append(submission)

            subreddit_data["Users"][user]["TLC Count"] = len(
                subreddit_data["Users"][user]["Threads Participated"])

            subreddit_data["Users"][user]["Flair"] = change_flair(
                comment.author_flair_text, subreddit_data["Users"][user]["TLC Count"])
            print("Found!")

        # Creating a user for the first time.
        else:
            subreddit_data["Users"][user] = {}
            subreddit_data["Users"][user]["TLC Count"] = 1
            subreddit_data["Users"][user]["Threads Participated"] = [submission]

            subreddit_data["Users"][user]["Flair"] = change_flair(
                comment.author_flair_text, subreddit_data["Users"][user]["TLC Count"])
            print("Not found, created for next time!")

        write_to_json(subreddit_data)


def main(r):
    try:
        subreddit = r.subreddit("Exhibit_Art")
        for comment in subreddit.comments(limit=1000):
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

            # Pass this to user_tracker, to add this to the users stats.
            user_tracker(comment)
        # After updating, sets all user flairs.
        set_flair(subreddit)
        # Waits one minute
        time.sleep(60)
    except Exception as e:
        print(e)


r = login()
main(r)




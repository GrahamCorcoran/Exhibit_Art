import praw
import config
import json
import time


class load(object):
    def __init__(self, filename):
        self.filename = filename

        with open(self.filename, 'r') as f:
            self.data = json.load(f)

    def __enter__(self):
        return self.data

    def __exit__(self, type, value, tb):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)


def login():
    """
    Returns a reddit instance using your bot login information in config.py
    Usage example: r = login()
    """
    return praw.Reddit(username=config.username,
                       password=config.password,
                       client_id=config.client_id,
                       client_secret=config.client_secret,
                       user_agent=config.user_agent)


def add_comment(comment):
    """
    Takes a top level comment and adds it to filename (set in config).
    """
    with load(config.filename) as subreddit_data:
        if comment not in subreddit_data["Comments"]:
            subreddit_data["Comments"].append(comment)


def get_flair(flair_text, tlc_count):
    """
    :param flair_text: Old Flair Text
    :param tlc_count: Count of top level comments user has.
    :return: New flair text in format "<alpha> - <number>" or "<number>"
    """
    if flair_text is None or not flair_text.isalpha():
        return str(tlc_count)

    return flair_text.split(" - ")[0] + " - " + str(tlc_count)


def set_flair(subreddit):
    """
    Modifies all flairs in json file to values in format <alpha> - <number> or <number>
    """
    with load(config.filename) as subreddit_data:
        for user in subreddit_data['Users']:
            flair = subreddit_data['Users'][user]['Flair']
            subreddit.flair.set(user, flair)


def has_user(author):
    """
    :param author: String of a Reddit Username
    :return: True if author is in filename (set in config), else false.
    """
    with load(config.filename) as subreddit_data:
        return author in subreddit_data["Users"]


def has_comment(commentid):
    """
    :param commentid: CommentID to check.
    :return: True if CommentID is in filename, else false.
    """
    with load(config.filename) as subreddit_data:
        return commentid in subreddit_data["Comments"]


def existing_user(user, comment, subreddit_data, submission):
    if submission not in subreddit_data["Users"][user]["Threads Participated"]:
        subreddit_data["Users"][user]["Threads Participated"].append(submission)

    subreddit_data["Users"][user]["TLC Count"] = len(
        subreddit_data["Users"][user]["Threads Participated"])

    subreddit_data["Users"][user]["Flair"] = get_flair(
        comment.author_flair_text, subreddit_data["Users"][user]["TLC Count"])


def new_user(user, comment, subreddit_data, submission):
    subreddit_data["Users"][user] = {}
    subreddit_data["Users"][user]["TLC Count"] = 1
    subreddit_data["Users"][user]["Threads Participated"] = [submission]

    subreddit_data["Users"][user]["Flair"] = get_flair(
        comment.author_flair_text, subreddit_data["Users"][user]["TLC Count"])


def track_user(comment):
    user = str(comment.author)
    submission = str(comment.submission)

    with load(config.filename) as subreddit_data:
        # If a user already exists
        if user in subreddit_data["Users"]:
            existing_user(user, comment, subreddit_data, submission)

        # Creating a user for the first time.
        else:
            new_user(user, comment, subreddit_data, submission)


def main(r):
    try:
        subreddit = r.subreddit("Exhibit_Art")
        for comment in subreddit.comments(limit=1000):
            # If comment already has been worked; continues to next.
            if has_comment(str(comment)):
                continue

            # If comment isn't top level comment, ignores.
            if not comment.is_root:
                continue

            # Verifies that this is in fact a weekly contribution thread.
            # ** This also causes massive slowdown, find out if there's a way to fix that.
            if "contribution" not in comment.submission.link_flair_text.lower():
                continue

            # Adds comment to list of worked comments.
            add_comment(str(comment))

            # Pass this to track_user, to add this to the users stats.
            track_user(comment)

        # After updating, sets all user flairs.
        set_flair(subreddit)

        # Waits one minute
        time.sleep(60)

    except Exception as e:
        print(e)


r = login()

while True:
    main(r)




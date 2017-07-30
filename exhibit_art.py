import praw
import config
import json
import time

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


def read_config():
    with open(config.filename, "r") as f:
        return json.load(f)


def add_comment(comment):
    """
    Takes a top level comment and adds it to filename (set in config).
    """
    subreddit_data = read_config()
    if comment not in subreddit_data["Comments"]:
        subreddit_data["Comments"].append(comment)
        write_to_json(subreddit_data)


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
    subreddit_data = read_config()
    for user in subreddit_data['Users']:
        flair = subreddit_data['Users'][user]['Flair']
        subreddit.flair.set(user, flair)


def write_to_json(data):
    """
    Writes data to filename (set in config).
    """
    with open(config.filename, 'w') as f:
        json.dump(data, f, indent=4)


def has_user(author):
    """
    :param author: String of a Reddit Username
    :return: True if author is in filename (set in config), else false.
    """
    subreddit_data = read_config()
    return author in subreddit_data["Users"]


def has_comment(commentid):
    """
    :param commentid: CommentID to check.
    :return: True if CommentID is in filename, else false.
    """
    subreddit_data = read_config()
    return commentid in subreddit_data["Comments"]


def track_user(comment):
    user = str(comment.author)
    submission = str(comment.submission)
    subreddit_data = read_config()

    # If a user already exists
    if user in subreddit_data["Users"]:
        if submission not in subreddit_data["Users"][user]["Threads Participated"]:
            subreddit_data["Users"][user]["Threads Participated"].append(submission)

        subreddit_data["Users"][user]["TLC Count"] = len(
            subreddit_data["Users"][user]["Threads Participated"])

        subreddit_data["Users"][user]["Flair"] = get_flair(
            comment.author_flair_text, subreddit_data["Users"][user]["TLC Count"])
        print("Found!")

    # Creating a user for the first time.
    else:
        subreddit_data["Users"][user] = {}
        subreddit_data["Users"][user]["TLC Count"] = 1
        subreddit_data["Users"][user]["Threads Participated"] = [submission]

        subreddit_data["Users"][user]["Flair"] = get_flair(
            comment.author_flair_text, subreddit_data["Users"][user]["TLC Count"])
        print("Not found, created for next time!")

    write_to_json(subreddit_data)


def main(r):
    try:
        subreddit = r.subreddit("Exhibit_Art")
        for comment in subreddit.comments(limit=1000):
            # If comment already has been worked; continues to next.
            if has_comment(str(comment)):
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

            # Pass this to track_user, to add this to the users stats.
            track_user(comment)
        # After updating, sets all user flairs.
        set_flair(subreddit)
        # Waits one minute
        time.sleep(60)
    except Exception as e:
        print(e)


r = login()
main(r)




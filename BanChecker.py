import os
from slack_bolt import App

app = App(
    token=os.environ.get("BAN_CHECKER_BOT_TOKEN"),
    signing_secret=os.environ.get("BAN_CHECKER_SIGNING_SECRET")
)

@app.event("message")
def handle_event(event, say):
    if event["channel_type"] == "im":
        handle_input(event, say, None)
    elif event["channel"] == "C04KMCWTGJU":
        thread_ts = event.get("thread_ts", None) or event["ts"]
        handle_input(event, say, thread_ts)

@app.event("app_mention")
def respond_to_mention(event, say):
    debug = open("debug.txt", "a")
    thread_ts = event.get("thread_ts", None) or event["ts"]
    debug.write(thread_ts)
    handle_input(event, say, thread_ts)

def handle_input(event, say, thread):
    event["text"] = event["text"].replace('’', '\'')
    try:
        if "statuscheck" in event["text"]: 
            say(text="I'm alive.", thread_ts=thread)
        elif "checkbans" in event["text"]:
            say(text="Current banlist in memory: \n" + getBans(), thread_ts=thread)
        elif "addbans" in event["text"]:
            addBans(event)
            say(text="Bans added.", thread_ts=thread)
        elif "removebans" in event["text"]:
            removeBans(event)
            say(text="Bans removed.", thread_ts=thread)
        else:
            evaluateDeck(event, say, thread)
    except Exception as e:
        say(text="An error occurred. " + "msg: " + str(e))

def removeBans(event):
    try:
        banlist = open("banlist.txt", "rw", encoding="utf-8")
    except:
        return "Error reading from banlist"
    lines = event["text"].splitlines(False)
    bans = banlist.read().splitlines(False)
    newBans = ""
    for ban in bans:
        for line in lines: 
            if "addbans" not in line and line != ban:
                newBans += ban + '\n'
    banlist.write(newBans)

def addBans(event):
    banlist = None
    try:
        banlist = open("banlist.txt", "a", encoding="utf-8")
    except:
        banlist = open("banlist.txt", "x", encoding="utf-8")
    lines = event["text"].splitlines(True)
    for line in lines:
        if "addbans" not in line:
            banlist.write(line)

def getBans():
    try:
        banlist = open("banlist.txt", "r", encoding="utf-8")
    except:
        return "Error reading from banlist"
    return banlist.read()

def evaluateDeck(event, say, thread):
    try:
        banlist = open("banlist.txt", "r", encoding="utf-8")
    except:
        return "Error reading from banlist"
    banned_cards = banlist.read().splitlines(False)
    deck = event["text"].splitlines(False)
    deck_errors = ""
    for card in deck:
        if len(card) > 0:
            card_split = card.split() # strip card count
            if card_split[0] == "<@U05BRL18PST>":
                card_split = card_split[1 : len(card_split)]
            card_name = ' '.join(card_split[1 : len(card_split)])
            for ban in banned_cards:
                if card_name == ban:
                    deck_errors = deck_errors + card_name + '\n'
    if deck_errors != "":
        say("WARNING: Deck contains banned cards:\n" + deck_errors, thread_ts=thread)
    else:
        say(text="Deck contains no banned cards!", thread_ts=thread)


if __name__ == "__main__":
    app.start(3001)
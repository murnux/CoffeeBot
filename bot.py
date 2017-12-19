# Massive thanks to Cormac o-brien's tutorial for helping me understand how IRC networking works.
# Tutorial link: http://www.instructables.com/id/Twitchtv-Moderator-Bot/

import cfg
import socket, re
from time import sleep

# Send a normal chat message for various scenarios
def chat (sock, msg):
    sock.send("PRIVMSG {} :{}".format(cfg.CHAN, msg).encode("utf-8"))


# BANHAMMER
def timeout (sock, user, secs=600):
    chat(sock, ".timeout {}".format(user,secs))

# Have the bot print out the result of a command to the channel's chat
def bot_command (sock, cmd):
    sock.send("PRIVMSG {} : {}\r\n".format(cfg.CHAN, cfg.COMMANDS.get(cmd)).encode("utf-8"))

s = socket.socket()
s.connect((cfg.HOST,cfg.PORT))

s.send("PASS {}\r\n".format(cfg.BOT_PASS).encode("utf-8"))
s.send("NICK {}\r\n".format(cfg.BOT_NICK).encode("utf-8"))
s.send("JOIN {}\r\n".format(cfg.CHAN).encode("utf-8"))

CHAT_MSG=re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

while True:
    response = s.recv(1024).decode("utf-8")
    if response == "PING :tmi.twitch.tv\r\n":
        s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
    else:
        username = re.search(r"\w+", response).group(0)
        message = CHAT_MSG.sub("", response)
        print(username + ": " + message)
        for pattern in cfg.BAN_WORDS:
            if re.match(pattern, message):
                timeout(s, username)
                print(username + " has been banned for saying: " + message)
                break
        for goof in cfg.GOOFY_WORDS:
            if re.match(goof, message):
                print(cfg.BOT_NICK + ": "+message)
                chat(s, message)
                break

        # Commands utilize a directory system in cfg.py
        for command in cfg.COMMANDS:
            if re.match(command, message):
                # IRC syntax causes \r\n to get appended to the message. Below gets rid of it.
                message = message.replace("\r\n", "")
                bot_command(s, message)
                break

#!/usr/bin/env python3

import os
import sys
import discord
import random
from configparser import ConfigParser
import mysql.connector


config = ConfigParser()
config.read(os.path.abspath(sys.argv[0]+"/../config.ini"))

client = discord.Client()


simposiumdb = mysql.connector.connect (
        host = config['mysql']['host'],
        user = config['mysql']['user'],
        password = config['mysql']['password'],
        database = config['mysql']['database']
)

dbcursor = simposiumdb.cursor()

message_responses = {
        "jsem vtipnej": "ne nejsi...",
        "*jsi": "Aha, tak hele ty debílku.",
        "jsi*": "Aha, tak hele ty debílku.",
        "bože": "Ano?",
        "jžš": "Ano?",
        "jzs": "Ano?",
        "omg": "Ano?",
        "OMG": "Ano?",
        "Máme radost?": "...",
        "Mame radost?": "...",
        "Tak máme?": "Máme radost!",
        "Tak mame?": "Máme radost!",
}

pupickovi_sloveni = [
        "Pupíčku",
        "pupíčku",
        "Pupicku",
        "pupicku",
        "Pupíku",
        "pupíku",
        "Pupiku",
        "pupiku",
        "Pupajs",
        "pupajs",
]

# CONSTANTS and MACROS
WAKEUP_CALL = "!fetch_pupik"

# true = spam
def pupik_filter(msg):
    
    #TODO remove test prints

    # constants
    MSG_LOW_LEN = 5
    MSG_HIGH_LEN = 50
    WORD_HIGH_LEN = 25


    # bot messages
    if (msg.author.bot):
        return [True, "bots msg"]
    
    text = msg.content

    # msg length
    if(len(text) < MSG_LOW_LEN or len(text) > MSG_HIGH_LEN):
        return [True, "wrong msg len: "+str(len(text))]

    # words len
    words = text.split()
    for word in words:
        if len(word) > WORD_HIGH_LEN:
            return [True, "wrong word: '"+word+"' len: "+str(len(word))]
    # valid chars
    letters_arr = text.replace(" ", "").lower()
    counter = 0
    for letter in letters_arr:
        if ord(letter) > ord('z') or ord(letter) < ord('a'):
            counter += 1
    if counter > len(letters_arr):
        return [True, "many unsupported characters in msg: "+ letters_arr]

    # emoji
    if(":" in text):
        return [True,"emoji in msg. Msg: "+text]

    return [False, ""]

@client.event
async def on_ready():
    print("We have logged in is {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    for message_item in message_responses:
        if message_item in message.content:
            await message.channel.send(message_responses.get(message_item))
            return

    for message_item in pupickovi_sloveni:
        if message_item in message.content:
            sql = "SELECT hlaska FROM pupik_hlasky ORDER BY RAND() LIMIT 1"
            dbcursor.execute(sql)

            pupik_hlaska = dbcursor.fetchall()

            await message.channel.send("Pupíček: " + pupik_hlaska[0][0])
            return
    
    if message.content.startswith(WAKEUP_CALL):
        channel = message.channel
        await channel.send("fetching...")

        num_of_msg = 0

        all_msgs = await channel.history(limit=200).flatten()

        for msg in all_msgs:
            
            #TODO msg.content use only content in commas
            tmp_arr = msg.content.split('"')
            if len(tmp_arr) == 1:
                msg.content = tmp_arr[0]
            elif len(tmp_arr) == 3:
                msg.content = tmp_arr[1]
                

            if WAKEUP_CALL in msg.content:
                continue
            elif pupik_filter(msg)[0]:
                print("SPAM: "+msg.content)
                continue
            print("HAM: "+msg.content)

            num_of_msg += 1
            member_id = msg.author.id

            sql = "SELECT id, member_id FROM users WHERE member_id = %s"
            val = (str(member_id), )
            dbcursor.execute(sql, val)

            sql_results = dbcursor.fetchall()

            if 0 == len(sql_results):
                name = msg.author.name

                if hasattr(msg.author, 'nick'):
                    nick = msg.author.nick
                else:
                    nick = name

                sql = "INSERT INTO users (name, nick, member_id) VALUES (%s, %s, %s)"
                val = (str(name), str(nick), str(member_id))
                dbcursor.execute(sql, val)

                simposiumdb.commit()

                sql = "SELECT id, member_id FROM users WHERE member_id = %s"
                val = (str(member_id), )
                dbcursor.execute(sql, val)

                sql_results = dbcursor.fetchall()

            sql = "INSERT INTO pupik_hlasky (hlaska, date, author) VALUES (%s, %s, %s)"
            val = (str(msg.content), str(msg.created_at), sql_results[0])
            #dbcursor.execute(sql, val) #TODO: uncomment when spam filter done

            simposiumdb.commit()


        await channel.send("Fetched {:d} new hlášek.".format(num_of_msg))
        return

client.run(config['discord']['TOKEN'])

###


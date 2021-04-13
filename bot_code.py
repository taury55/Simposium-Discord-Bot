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

pupickovniny = [
        "Ten Urgot mě ultnul???",
        "Ten Urgot má lvl 9?",
        "Pupíčku, dáš si rohlíček?",
        "Burp",
        "JAMESSSS, JAMESSSS CARONNNNNNNN",
        "Moje ultina nefunguje... vrrrrrnnnn vrrrrnnnn vhuuum",
        "Ale Jirka Král je lepší.",
        "HROOOOO!",
        "TO PROČ V TÝ BUSHYYY???",
        "To co tam dělaj to Qčka?",
        "Pupajs?",
        "WTF, Nechceš umřít?",
        "Da faaaak?",
        "JEBE TII???",
        "Ježíš ona zase flashla, kolik ona má těch flashů?"
        "Formule Pzke zasahuje... tudum tudum"
        "Ona má zas tu ultinu. Ona má furtttttt!!!",
        "NÉÉÉÉÉÉÉ NÉÉÉÉÉÉÉ HRO!",
        "ne pls xd",
        "xd",
        "Ty seš fakt kvalitní champión!",
        "Jak ho to minulo?!",
        "JAK JSI TO ROZBIL?!?!?!",
        "Už zase?!?!",
        "Oni dohráli... HOVNO",
        "eeeeeeeeeeeeeeee",
        "Hlavně že máš pivo vole.",
        "SVATBA KÁRY",
        "Smrk Smmrrrrrrrrk",
        "To je Čínskej prezident.",
        "WHAAAAA THE FUUUCK!!!",
        "Co spotíš VOLEEEE????",
        "No jasně, že mě vidííím!!!",
        "Prďolaaaa",
        "Dělaš si kokota???",
        "Kéž by.",
        "Ahoooj, ahoj mastře?",
        "Ty seš fakt kvalitní champion kamaráde.",
        "Kam až to letí to tvoje Q.",
        "Ten 'pro play'",
        "Kurwa, zrovna top tier a já mám ping 500 vole.",
        "Já mám dělo z číííííínyyyyy!!!!",
        "NO TAK TY VOLEEEEEEE.",
        "Co to je za bullshit ten champ kámo prostě.",
        "Ohh, ano ty jsi tak dobrá ty píčo.",
        "Achhhhhhhhhh, co to je za damage.",
        "Dáš si oříšek?",
        "Yoooou, what's up my man?",
]

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

def pupik_filter(message):
    return False

@client.event
async def on_ready():
    print("We have logged in is {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    #print("content "+ message.content)
    #print("author "+ message.author.name)
    #print("author id "+ str(message.author.id))
    #print("bot? "+ str(message.author.bot))
    #print("created at "+ str(message.created_at))
    #print("type "+ str(message.type)) # catch only default type

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

    if message.content.startswith("!fetch_pupik"):
        channel = message.channel
        await channel.send("fetching...")

        num_of_msg = 0

        all_msgs = await channel.history(limit=200).flatten()

        for msg in all_msgs:
            if pupik_filter(msg): #TODO: here add spam filter function
                continue

            num_of_msg += 1
            member_id = msg.author.id

            sql = "SELECT member_id FROM users WHERE member_id = %s"
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

            sql = "INSERT INTO pupik_hlasky (hlaska, date, author_id) VALUES (%s, %s, %s)"
            val = (str(msg.content), str(msg.created_at), str(member_id))
            #dbcursor.execute(sql, val) #TODO: uncomment when spam filter done

            simposiumdb.commit()


        await channel.send("Fetched {:d} new hlášek.".format(num_of_msg))
        return

client.run(config['discord']['TOKEN'])

###


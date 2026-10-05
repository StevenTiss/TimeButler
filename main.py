import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

#CURRENT TIME GAP
currentPacificTime = datetime.now(ZoneInfo('America/Los_Angeles'))
currentNZTime = datetime.now(ZoneInfo('Pacific/Auckland'))
time_dif = currentPacificTime.hour - currentNZTime.hour

def append_ampm(extracted_times, combined_matrix, received_message):
    while len(extracted_times) > 0:
        i = extracted_times.pop()
        hours_minutes_suffix = re.findall(r'\d{1,2}', i)
        if len(hours_minutes_suffix) == 1:
            hours_minutes_suffix.append("00")
        if re.findall(r'am', i):
            hours_minutes_suffix.append(" am")
        elif re.findall(r'pm', i):
            hours_minutes_suffix.append(" pm")
        combined_matrix.append(hours_minutes_suffix)
        received_message = received_message.replace(i, "")
    return combined_matrix, received_message

def extract_time(received_message: str):
    
    extracted_times_with_colons = re.findall(r'\d{1,2}:\d{2} pm|\d{1,2}:\d{2}pm|\d{1,2}:\d{2} am|\d{1,2}:\d{2}am|\d{1,2}:\d{2}', received_message)
    extracted_times_with_colons.reverse()

    combined_matrix_of_hours_minutes_suffix = []

    combined_matrix_of_hours_minutes_suffix, received_message = append_ampm(extracted_times_with_colons, combined_matrix_of_hours_minutes_suffix, received_message)

    extracted_times_without_colons = re.findall(r'\d{1,2}am|\d{1,2} am|\d{1,2}pm|\d{1,2} pm', received_message)
    extracted_times_without_colons.reverse()

    append_ampm(extracted_times_without_colons, combined_matrix_of_hours_minutes_suffix, received_message)

    return combined_matrix_of_hours_minutes_suffix

def time_changer(matrix_of_nz_times):
    list_of_pacific_times = []
    for i in range(len(matrix_of_nz_times)):
        list_of_pacific_times.append([int(matrix_of_nz_times[i][0]) + time_dif, matrix_of_nz_times[i][1], matrix_of_nz_times[i][2]])
        if int(matrix_of_nz_times[i][0]) != 12 and int(list_of_pacific_times[i][0]) >= 12:
            if list_of_pacific_times[i][2] == "am":
                list_of_pacific_times[i][2] = "pm"
            elif list_of_pacific_times[i][2] == "pm":
                list_of_pacific_times[i][2] = "am"

        if list_of_pacific_times[i][0] > 12:
            list_of_pacific_times[i][0] -= 12

    response_list = []

    for i in range(len(list_of_pacific_times)):
        response_list.append(str(list_of_pacific_times[i][0]) + ":" + list_of_pacific_times[i][1] + list_of_pacific_times[i][2])

    response_string = ", ".join(response_list)
    return response_string

@bot.event
async def on_ready():
    print(f"{bot.user.name} reporting for duty.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "am nz" in message.content.lower():
        await message.channel.send(f"That's {time_changer(extract_time(message.content.lower()))} Pacific. (probably)")
    elif "pm nz" in message.content.lower():
        await message.channel.send(f"That's {time_changer(extract_time(message.content.lower()))} Pacific. (probably)")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
import modal

bot_image = modal.Image.debian_slim().pip_install("discord")
bot_image = bot_image.pip_install("numpy")
bot_image = bot_image.pip_install("pandas")
bot_image = bot_image.pip_install("yfinance")
bot_image = bot_image.pip_install("python-dotenv")
bot_image = bot_image.pip_install("openai")

stub = modal.Stub("rocky-bot", image=bot_image)


@stub.function(secret=modal.Secret.from_name("my-openai-secret"))
def complete_text(prompt):
    import openai
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
        # temperature=0.75,
        # max_tokens=4096,
        #top_p=1,
        #frequency_penalty=0,
        #presence_penalty=0
        )
    return completion.choices[0].message.content

@stub.function(secret=modal.Secret.from_name("rocky-secret"), timeout = 86400)
def main(image=bot_image):
    import discord
    from discord import app_commands
    import os
    import numpy as np
    import re
    import pandas as pd
    from dotenv import load_dotenv
    import requests
    import yfinance as yf
    import modal
    # print(os.listdir())
    # pokemon = pd.read_csv('pokemon.csv')
    pokemon = None
    # delta_pokemon = pd.read_csv('Insurgence - Sheet1.csv')
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)
    dice_pattern = '^\\$d[0-9]*'
    grouped_expression = '^\\$\\([0-9]*[\\.]?[0-9]*[-|\\+|\\*|/|%][0-9]*[\\.]?[0-9]*\\)$'
    pokemon_pattern = '\\$(Fire|Water|Grass|Normal|Electric|Ice|Fighting|Poison|Ground|Flying|Psychic|Bug|Rock|Ghost|Dark|Dragon|Steel|Fairy)'
    stats_pattern = '\\$stats .*'
    rand_pokemon = '\\$pokemon random [0-9]*'
    rand_pokemon_delta = '\\$pokemon delta random [0-9]*'
    rand_class_pattern = '\\$rand class'
    sandwich = '\\$sandwich'
    request_pattern = "\\$web_request (\\s|\\S)*"
    img_pattern = "src=\"[^\"]*\"|SRC=\"[^\"]*\""  # bizzare bug where (src|SRC) doesn't work, not sure why though, it would simplify the code
    stock_pattern = '\\$stock .*'

    @client.event
    async def on_ready():
        print('We have logged in as {0.user})'.format(client))

    @tree.command(name="rock", description="Testing Rocky", guild=discord.Object(
        id=879815270779203616))  # Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
    async def first_command(interaction):
        await interaction.response.send_message("Hello!")

    @client.event
    async def on_message(message):

        if message.author == client.user:
            return

        if message.content.startswith('$rock'):
            await message.channel.send('You rock!')

        if message.content.startswith('$hello'):
            await message.channel.send('Hello! You rock!')

        if message.content.startswith('$roll'):
            await message.channel.send('Hello! You rock and roll!')

        if message.content.startswith('$d'):
            if (result := re.match(dice_pattern, message.content)) is not None:
                result = int(result.group()[2:])
                await message.channel.send(np.random.randint(1, result))

        if message.content.startswith('$('):
            if (result := re.match(grouped_expression, message.content)) is not None:
                content = message.content
                for i in range(len(content)):
                    if content[i] == '-' or content[i] == '+' or content[i] == '*' or content[i] == '/' or content[
                        i] == '%':
                        left = content[2:i]
                        right = content[i + 1:len(content) - 1]
                        operator = content[i]
                        if operator == "+":
                            try:
                                await message.channel.send(int(left) + int(right))
                            except Exception:
                                await message.channel.send(float(left) + float(right))
                        if operator == "-":
                            try:
                                await message.channel.send(int(left) - int(right))
                            except Exception:
                                await message.channel.send(float(left) - float(right))
                        if operator == "*":
                            try:
                                await message.channel.send(int(left) * int(right))
                            except Exception:
                                await message.channel.send(float(left) * float(right))
                        if operator == "/":
                            try:
                                await message.channel.send(int(left) / int(right))
                            except Exception:
                                await message.channel.send(float(left) / float(right))
                        if operator == "%":
                            try:
                                await message.channel.send(int(left) % int(right))
                            except Exception:
                                await message.channel.send(float(left) % float(right))
        if message.content.startswith('$'):
            if (result := re.match(pokemon_pattern, message.content)) is not None:
                typing = message.content[1:]  # Changed to handle dual typing case
                typed_poke = pokemon[pokemon["typing"] == typing]
                print(typing)
                await message.channel.send(str(typed_poke["name"].values.tolist())[:1999])

            if (result := re.match(rand_pokemon, message.content)) is not None:
                num = int(message.content[16:])
                rand_pokemon_set = set()
                pokemon_names = pokemon["name"].values.tolist()
                if num > len(pokemon_names):
                    await message.channel.send("Not that many pokemon exist!")
                else:
                    rand_pokemon_names = []
                    while len(rand_pokemon_set) < num:
                        rand_pokemon_set.add(np.random.randint(1, len(pokemon_names)))
                    rand_pokemon_set = list(rand_pokemon_set)
                    for i in range(len(rand_pokemon_set)):
                        rand_pokemon_names.append(pokemon_names[rand_pokemon_set[i]])
                    await message.channel.send(rand_pokemon_names[:1999])

            if (result := re.match(rand_pokemon_delta, message.content)) is not None:
                num = int(message.content[22:])
                rand_pokemon_set = set()
                gen_6_mons = pokemon[pokemon["pokedex_id"] <= 721]
                pokemon_names = gen_6_mons["name"].values.tolist()
                # delta_names = delta_pokemon["name"].values.tolist()
                pokemon_names = pokemon_names  # + delta_names
                if num > len(pokemon_names):
                    await message.channel.send("Not that many pokemon exist!")
                else:
                    rand_pokemon_names = []
                    while (len(rand_pokemon_set) < num):
                        rand_pokemon_set.add(np.random.randint(1, len(pokemon_names)))
                    rand_pokemon_set = list(rand_pokemon_set)
                    for i in range(len(rand_pokemon_set)):
                        rand_pokemon_names.append(pokemon_names[rand_pokemon_set[i]])
                    await message.channel.send(rand_pokemon_names[:1999])

            if (result := re.match(stats_pattern, message.content)) is not None:
                name = message.content[7:].capitalize()
                name_pokemon = pokemon[pokemon["name"] == name]
                name_data = name_pokemon.loc[:,
                            ["hp", "attack", "defense", "special_attack", "special_defense", "speed"]].values.tolist()[
                    0]
                # await message.channel.send(name_data)
                await message.channel.send(
                    "hp: %s\nattack: %s\ndefense: %s\nspecial_attack: %s\nspecial_defense: %s\nspeed: %s" % (
                        name_data[0], name_data[1], name_data[2], name_data[3], name_data[4], name_data[5]))

            if (result := re.match(rand_class_pattern, message.content)) is not None:
                rand_classes = ["Artificer", "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin",
                                "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"]
                await message.channel.send(rand_classes[np.random.randint(1, len(rand_classes))])

            if message.content.startswith('$web_request'):
                if (result := re.match(request_pattern, message.content)) is not None:
                    response = requests.get(message.content[13:])
                    stringo = response.content.decode()
                    while (len(stringo) > 0):
                        await message.channel.send(stringo[:1999])
                        stringo = stringo[1999:]

            if message.content.startswith('$img_scrape'):
                response = requests.get(message.content[12:])
                stringo = response.content.decode()
                images = re.findall(img_pattern, stringo)
                for img in images:
                    await message.channel.send(img[5:len(img) - 1])

            if message.content.startswith('$stonks'):
                await message.channel.send("*STONKS!*")

            if message.content.startswith('$sandwich'):
                await message.channel.send("Definition: The existence of grain anywhere")

            if message.content.startswith('$cheese'):
                await message.channel.send("Definition: A grain")

            if message.content.startswith('$chatgpt'):
                prompt_text = message.content[9:]
                chatgpt_output = complete_text.call(prompt_text)
                while (len(chatgpt_output) > 0):
                    await message.channel.send(chatgpt_output[:1999])
                    chatgpt_output = chatgpt_output[1999:]

            if message.content.startswith('$code'):
                prompt_text = message.content[6:]
                prompt_text = "Give me the code for the following: " + prompt_text
                chatgpt_output = complete_text.call(prompt_text)
                while (len(chatgpt_output) > 0):
                    await message.channel.send(chatgpt_output[:1999])
                    chatgpt_output = chatgpt_output[1999:]

            if message.content.startswith('$pokedex'):
                prompt_text = message.content[9:]
                prompt_text = "Return the pokedex entry for: " + prompt_text
                chatgpt_output = complete_text.call(prompt_text)
                while (len(chatgpt_output) > 0):
                    await message.channel.send(chatgpt_output[:1999])
                    chatgpt_output = chatgpt_output[1999:]

            if (result := re.match(stock_pattern, message.content)) is not None:
                stock_name = message.content[7:].upper()
                stock = yf.download(tickers=stock_name, period='1d', interval='1m')
                latest_low = stock.tail(1)["Low"]
                await message.channel.send("Current Low Price of " + stock_name + ": $" + str(latest_low[0]))
                latest_high = stock.tail(1)["High"]
                await message.channel.send("Current High Price of " + stock_name + ": $" + str(latest_high[0]))

            if message.content.startswith('$你叫什么名字') or message.content.startswith('$你叫什么名字?'):
                await message.channel.send("我叫 rocky!")

            if message.content.startswith('$help'):
                help_commands = ""
                help_commands += "$stock STOCK_TICKER: Provides current low and high price of a stock\n"
                help_commands += "$chatgpt PROMPT: Provides chatgpt's interpretation of a given prompt\n"
                help_commands += "$web_request WEBSITE_URL: Provides the data on a given url\n"
                help_commands += "$rand class: Provides a random standard 5e class\n"
                help_commands += "$d<Number>: Provides a random roll of a dice with a certain number, where <Number> is a number from 1 to any greater integer\n"
                help_commands += "$(<Number>+<Number>): will add two numbers\n"
                help_commands += "$(<Number>-<Number>): will subtract two numbers\n"
                help_commands += "$(<Number>*<Number>): will multiply two numbers\n"
                help_commands += "$(<Number>/<Number>): will divide two numbers\n"
                help_commands += "$(<Number>%<Number>): will modulus two numbers\n"
                await message.channel.send(help_commands)

    load_dotenv()
    client.run(os.environ['TOKEN'])


@stub.function()
def local_main():
    while True:
        main.call()


if __name__ == "__main__":
    stub.deploy("zoom")
#local_main()

# Trusted resources pullup with a command, Teach him calculus,

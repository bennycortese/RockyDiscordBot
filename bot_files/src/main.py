import discord
import os
import numpy as np
import re
import pandas as pd
from dotenv import load_dotenv

def main():
    # print(os.listdir())
    pokemon = pd.read_csv('pokemon.csv')
    delta_pokemon = pd.read_csv('Insurgence - Sheet1.csv')
    client = discord.Client()
    dice_pattern = '^\$d[0-9]*'
    grouped_expression = '^\$\([0-9]*[\.]?[0-9]*[-|\+|\*|/|%][0-9]*[\.]?[0-9]*\)$'
    pokemon_pattern = '\$(fire|water|grass|normal|electric|ice|fighting|poison|ground|flying|psychic|bug|rock|ghost|dark|dragon|steel|fairy){1}'
    stats_pattern = '\$stats .*'
    rand_pokemon = '\$pokemon random [0-9]*'
    rand_pokemon_delta = '\$pokemon delta random [0-9]*'
    rand_class_pattern = '\$rand class'

    @client.event
    async def on_ready():
        print('We have logged in as {0.user})'.format(client))

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
            if (result := re.match(pokemon_pattern, message.content) is not None):
                typing = message.content[1:].capitalize()
                typed_poke = pokemon[pokemon["typing"] == typing]
                print(typing)
                await message.channel.send(str(typed_poke["name"].values.tolist())[:1999])

            if (result := re.match(rand_pokemon, message.content) is not None):
                num = int(message.content[16:])
                rand_pokemon_set = set()
                pokemon_names = pokemon["name"].values.tolist()
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

            if (result := re.match(rand_pokemon_delta, message.content) is not None):
                num = int(message.content[22:])
                rand_pokemon_set = set()
                gen_6_mons = pokemon[pokemon["pokedex_id"] <= 721]
                pokemon_names = gen_6_mons["name"].values.tolist()
                delta_names = delta_pokemon["name"].values.tolist()
                pokemon_names = pokemon_names + delta_names
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

            if (result := re.match(stats_pattern, message.content) is not None):
                name = message.content[7:].capitalize()
                name_pokemon = pokemon[pokemon["name"] == name]
                name_data = name_pokemon.loc[:,
                            ["hp", "attack", "defense", "special_attack", "special_defense", "speed"]].values.tolist()[
                    0]
                # await message.channel.send(name_data)
                await message.channel.send(
                    "hp: %s\nattack: %s\ndefense: %s\nspecial_attack: %s\nspecial_defense: %s\nspeed: %s" % (
                        name_data[0], name_data[1], name_data[2], name_data[3], name_data[4], name_data[5]))

            if (result := re.match(rand_class_pattern, message.content) is not None):
                rand_classes = ["Artificer", "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"]
                await message.channel.send(rand_classes[np.random.randint(1, len(rand_classes))])

    load_dotenv()
    client.run(os.environ['TOKEN'])


if __name__ == "__main__":
    main()

# Trusted resources pullup with a command, Teach him calculus,

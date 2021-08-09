import discord
import os
import numpy as np
import re


def main():
    client = discord.Client()
    dice_pattern = '^\$d[0-9]*'
    grouped_expression = '^\$\([0-9]*'
    operation = re.compile(r'(\+\-\*)')
    end_expression = '[0-9]*\)$'

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
                await message.channel.send(result)
                if (operator := re.match(operation, message.content)) is not None:
                    if (result3 := re.match(end_expression, message.content)) is not None:
                        result = int(result.group()[2:])
                        result3 = int(result.group()[:len(result3) - 3])
                        if operator == '+':
                            await message.channel.send(result + result3)
                        if operator == '-':
                            await message.channel.send(result - result3)
                        if operator == '*':
                            await message.channel.send(result * result3)
                        if operator == '/':
                            await message.channel.send(result / result3)
                    else:
                        await message.channel.send("fail 3")
                else:
                    await message.channel.send("fail 2")
            else:
                await message.channel.send("fail 1")

    client.run('Nzc2MDE2MDkwODEwNjc5MzE4.X6uvTQ.d70InigCLLdoAuok6efoIRkazug')


if __name__ == "__main__":
    main()

import discord
import datetime
from datetime import datetime
import io
import codecs
from googlesearch import search
from random import randrange
from discord.ext import commands, tasks
import random

intents = discord.Intents.all()
client = commands.Bot(command_prefix="", intents=intents)

memory = []
mods = []
# mods[0] = mod id
# mods[1] = mod guild id
guild_mc = []
# guild_mc[0] = guild id
# guild_mc[1] = member count channel id


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('Nocap'))

    with open("mods.txt", "r") as f:
        for line in f.readlines():
            mod_str = line.split(',')
            mod = [int(mod_str[0]), int(mod_str[1])]
            mods.append(mod)

    with open("guilds.txt", "r") as f:
        for line in f.readlines():
            guild_str = line.split(',')
            guild = [int(guild_str[0]), int(guild_str[1])]
            guild_mc.append(guild)

    client.load_extension('cogs.custom_commands')
    print(datetime.today())


@client.event
async def on_message_delete(message):
    print(message.author.name + " deleted message")
    memory.append(str(datetime.today()) + "| " + message.author.name + ": " + str(message.content))
    with codecs.open("memory.txt", "w", "utf-8-sig") as temp:
        for line in memory:
            temp.write(line + "\n")


@client.event
async def on_message_edit(before_edit):
    print(before_edit.author.name + " edited message")
    memory.append(str(datetime.today()) + "| " + before_edit.author.name + ": " + str(before_edit.content))
    with codecs.open("memory.txt", "w", "utf-8-sig") as temp:
        for line in memory:
            temp.write(line + "\n")


# member join/leave
@client.event
async def on_member_join(member):
    print(f'{member} has joined the server.')


@client.event
async def on_member_remove(member):
    print(f'{member} has left the server.')


@client.command(brief='add custom command')
async def add_command(ctx, user_input, output):
    result = ""
    if len(user_input) > 20 or len(output) > 1000:
        await ctx.send("too long didn't read")
    python_keywords = ['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue',
                       'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in',
                       'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with',
                       'yield']
    for word in python_keywords:
        if word in user_input or word in output:
            await ctx.send(f'the word "{word}" is not legal, try another word')
            return
    input_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_אבגדהוזחטיכלמנסעפצקרשתץףךןם'
    for char in user_input:
        check = False
        for letter in input_letters:
            if letter == char:
                check = True
        if not check:
            await ctx.send("Please enter valid input")
            return
    output_letters = ' ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.?!@#$%^&*)_(-+=*123456789/\<>,אבגדהוזחטיכלמנסעפצקרשתץףךןם'
    for char in output:
        check = False
        for letter in output_letters:
            if letter == char:
                check = True
        if not check:
            await ctx.send("Please enter valid input")
            return

    with io.open('cogs\custom_commands.py', mode='r', encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        if user_input in line and 'async def' in line:
            await ctx.send('This command already exists!')
            return

    with io.open('cogs\custom_commands.py', mode='w', encoding="utf-8") as f:
        for line in lines:
            if 'def setup(client):' not in line:
                result = result + line
            else:
                break
        f.write(
            result + f'''
    @commands.command()
    async def {user_input}(self, ctx):
        await ctx.send('{output}')

            '''
            + '''
def setup(client):
    client.add_cog(custom_commands(client))
    print('custom_commands loaded')
            '''
        )
    await ctx.send('command added successfully')
    client.reload_extension('cogs.custom_commands')


@client.command(brief='Deletes all custom commands')
async def clear_commands(ctx):
    if [ctx.author.id, ctx.guild.id] in mods:
        with io.open('cogs\custom_commands.py', mode='w', encoding="utf-8") as f:
            f.write('''from discord.ext import commands
class custom_commands(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.command()
    async def does_it_work(self, ctx):
        await ctx.send('it works!')

def setup(client):
    client.add_cog(custom_commands(client))
    print('custom_commands loaded')
            ''')
        await ctx.send("Commands cleared successfully!")
    else:
        await ctx.send("You don't have permission")
        

@client.command(brief='search something on google!')
async def google(ctx, arg):
    links = "**"
    links = links + 'Google results for: ' + arg + '\n' + '=================================================' + '\n'
    count = 1
    for j in search(arg, tld="co.in", num=10, stop=10, pause=2):
        links = links + '(' + str(count) + ')  <' + j + '>\n'
        count = count + 1
    await ctx.send(links + '**')


@client.command(brief='reset all the nicknames in the server')
async def fix_nicks(ctx):
    if [ctx.author.id, ctx.guild.id] in mods:
        for member in ctx.guild.members:
            if member.display_name != member.name:
                try:
                    await member.edit(nick=member.name)
                except:
                    pass
        await ctx.send("All nicknames fixed")
    else:
        await ctx.send("You don't have permission")


@client.command(brief='Tag anyone that has role x or everyone in the server')
async def tag(ctx, victim):
    if [ctx.author.id, ctx.guild.id] in mods:
        result = ""
        if victim == "everyone":
            for member in ctx.guild.members:
                result += member.mention + " "
            await ctx.send(result)
        else:
            role = discord.utils.get(ctx.guild.roles, name=victim)
            for member in ctx.guild.members:
                if role in member.roles:
                    result += member.mention + " "
            await ctx.send(result)
    else:
        await ctx.send("You don't have permission")


@client.command(brief='delete a message by id')
async def delete_msg(ctx, msg_id):
    if [ctx.author.id, ctx.guild.id] in mods:
        async for msg in ctx.channel.history(limit=200):
            if msg.id == int(msg_id):
                await msg.delete()


@client.command(brief='Unscramble a word (argument) ex: ouy -> you')
async def scramble(ctx, word):
    if (len(word)) <= 2:
        await ctx.send("The word is too short!")
    elif (len(word)) >= 30:
        await ctx.send("The word is too long!")
    else:
        # d = enchant.Dict("en_US")
        vocabulary = open('big vocabulary.txt', 'r')
        voc = vocabulary.readlines()
        arr = []
        sorted_word = "".join(sorted(word))
        for v in voc:
            v = v[:-2]
            word = word.lower()
            v = v.lower()
            sorted_v = "".join(sorted(v))
            if sorted_word == sorted_v:
                arr.append(v)
                
        if len(arr) <= 0:
            await ctx.send("Sorry, I didn't find any matching words!")
        else:
            arr.sort()
            arr = list(dict.fromkeys(arr))
            result = ""
            for x in arr:
                result += x + ", "
            result = result[:-2]
            result += "."
            await ctx.send("results: " + result)


@client.command(brief='get a link to a website that can solve minesweeper')
async def minesweeper(ctx):
    await ctx.send("https://mrgris.com/projects/minesweepr/demo/analyzer/")


@client.command(brief='kick a member')
async def kick(ctx, member: discord.User):
    if [ctx.author.id, ctx.guild.id] in mods:
        rnd = random.randint(1, 10)
        if rnd <= 5:
            try:
                await ctx.guild.kick(member)
                await ctx.send("kick success")
            except:
                await ctx.send("kick failed")
        else:
            await ctx.send("kick failed")
    else:
        await ctx.send("You don't have permission")


@client.command(brief='Clear the last x messages')
async def clear(ctx, msg_count):
    if [ctx.author.id, ctx.guild.id] in mods:
        count = int(msg_count)
        if 100 >= count > 0:
            async for msg in ctx.history(limit=count):
                try:
                    await msg.delete()
                except:
                    pass
        else:
            await ctx.send("you can clear between 1 and 100 messages")
    else:
        await ctx.send("you don't have permission")
        

@client.command(brief='Get a random number between a and b')
async def random_num(ctx, a, b):
    int_a = int(min(int(a), int(b)))
    int_b = int(max(int(a), int(b)))
    billion = 1000000000
    if int_b > billion or int_a < (-1)*billion:
        await ctx.send("Those numbers are too long!")
    else:
        result = randrange(int_b-int_a+1)+int_a
        await ctx.send(str(result))


@client.command(brief='grants mod permission to member')
async def add_mod(ctx, member: discord.User):
    if ctx.guild.owner == ctx.author:
        if [member.id, ctx.guild.id] in mods:
            await ctx.send("Member is already a moderator")
        else:
            mods.append([member.id, ctx.guild.id])
            # add mod to files
            with open("mods.txt", "r") as f:
                lines = f.read()
            with open("mods.txt", "w") as f:
                f.write(lines + str(member.id) + "," + str(ctx.guild.id) + '\n')

            await ctx.send("mod added to " + member.name)
    else:
        await ctx.send("Only the server admin can use this")


@client.command(brief='shows a list of mods in this server')
async def print_mods(ctx):
    print_mod = ""
    for mod in mods:
        if mod[1] == ctx.guild.id:
            mod_object = ctx.guild.get_member(mod)
            print_mod += mod_object.name + "\n"
    await ctx.send(print_mod)


@client.command(brief='removes mod permission from member')
async def remove_mod(ctx, member: discord.User):
    if ctx.guild.owner == ctx.author:
        if [member.id, ctx.guild.id] in mods:
            mods.remove([member.id, ctx.guild.id])

            # remove mod from files
            with open("mods.txt", "r") as f:
                lines = f.readlines()
            with open("mods.txt", "w") as f:
                for line in lines:
                    if line.strip("\n") != str(member.id) + "," + str(ctx.guild.id):
                        f.write(line)
            await ctx.send("removed " + member.name + " from mods")
        else:
            await ctx.send("member is not a mod")
    else:
        await ctx.send("Only the server admin can use this")


@client.command(brief='grants mod permission to member')
async def add_member_count(ctx):
    if [ctx.author.id, ctx.guild.id] in mods:
        for guild in guild_mc:
            if guild[0] == ctx.guild.id:
                await ctx.send("Already has a member counter")
                return

        channel = await ctx.guild.create_voice_channel('member_count')
        await channel.edit(name="members-" + str(len(ctx.guild.members)))
        guild_mc.append([ctx.guild.id, channel.id])
        await channel.set_permissions(ctx.guild.default_role, connect=False)

        # add "guild id, channel id" to file
        with open("guilds.txt", "r") as f:
            lines = f.read()
        with open("guilds.txt", "w") as f:
            f.write(lines + str(ctx.guild.id) + "," + str(channel.id) + '\n')
    else:
        await ctx.send("Only moderator can use this")


@client.command(brief='removes the member counter')
async def remove_member_count(ctx):
    if [ctx.author.id, ctx.guild.id] in mods:
        for guild in guild_mc:
            if guild[0] == ctx.guild.id:

                # delete the channel
                channel = ctx.guild.get_channel(guild[1])
                await channel.delete()

                # update array
                guild_mc.remove(guild)

                # update file
                with open("guilds.txt", "r") as f:
                    lines = f.readlines()
                with open("guilds.txt", "w") as f:
                    for line in lines:
                        if line.strip("\n") != str(guild[0]) + "," + str(guild[1]):
                            f.write(line)

                await ctx.send("Member counter removed successfully")
                return
        else:
            await ctx.send("I could not find a member counter")
    else:
        await ctx.send("Only server mods can use this")


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# general commands @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


@client.command(brief='mute a member')
async def mute(ctx, member: discord.Member):
    if [ctx.author.id, ctx.guild.id] in mods:
        await member.edit(mute=True)
        await ctx.send(f'{member.name} muted')
    else:
        await ctx.send("You don't have permission")


@client.command(brief='unmute a member')
async def unmute(ctx, member: discord.Member):
    if [ctx.author.id, ctx.guild.id] in mods:
        await member.edit(mute=False)
        await ctx.send(f'{member.name} unmuted')
    else:
        await ctx.send("You don't have permission")


@client.command(brief='deafen a member')
async def deafen(ctx, member: discord.Member):
    if [ctx.author.id, ctx.guild.id] in mods:
        await member.edit(deafen=True)
        await ctx.send(f'{member.name} defeaned')
    else:
        await ctx.send(f"You don't have permission")


@client.command(brief='undeafen a member')
async def undeafen(ctx, member: discord.Member):
    if [ctx.author.id, ctx.guild.id] in mods:
        await member.edit(deafen=False)
        await ctx.send(f'{member.name} undefeaned')
    else:
        await ctx.send(f"You don't have permission")


@client.command(brief='disconnect a member')
async def disconnect(ctx, member: discord.Member):
    if [ctx.author.id, ctx.guild.id] in mods:
        await member.move_to(None)
        await ctx.send(f'{member.name} disconnected')
    else:
        await ctx.send(f"You don't have permission")


@client.command(brief='unban a member')
async def unban(ctx, member: discord.Member):
    if [ctx.author.id, ctx.guild.id] in mods:
        await unban(member)
    else:
        await ctx.send("You don't have permission")


@client.command(brief='ban a member')
async def ban(ctx, member: discord.Member):
    if [ctx.author.id, ctx.guild.id] in mods:
        await ban(member)
    else:
        await ctx.send("You don't have permission")


@client.command(brief='add a role to input member, ex: role admin bob12')
async def add_role(ctx, role: discord.Role, user: discord.Member):
    if [ctx.author.id, ctx.guild.id] in mods:
        await user.add_roles(role)
        await ctx.send(f"Successfully given {role.mention} to {user.mention}.")


@client.command(brief='remove role from member')
async def remove_role(ctx, role: discord.Role, user: discord.Member):
    if [ctx.author.id, ctx.guild.id] in mods:
        await user.remove_roles(role)
        await ctx.send(f"Successfully removed {role.mention} from {user.mention}.")


@client.command(brief='move a member')
async def move(ctx, member: discord.Member, channel: discord.VoiceChannel):
    if [ctx.author.id, ctx.guild.id] in mods:
        await member.move_to(channel)
    else:
        await ctx.send("You don't have permission")


@client.command(brief='limit a voice channel members, ex: limit General 3')
async def limit(ctx, voice_channel: discord.VoiceChannel, lim):
    if [ctx.author.id, ctx.guild.id] in mods:
        for channel in ctx.guild.channels:
            if channel is voice_channel:
                await channel.edit(user_limit=int(lim))
                await ctx.send(f"'{voice_channel.name}' limit updated to {lim}")
    else:
        await ctx.send("You don't have permission")


@commands.command(pass_context=True, brief='change the name of a member')
async def rename(ctx, member: discord.Member, nick):
    if [ctx.author.id, ctx.guild.id] in mods:
        await member.edit(nick=nick)
        await ctx.send(f'Nickname was changed for {member.mention} ')


@client.command(brief='move a member between server to wake him up!')
async def wakeup(ctx, member: discord.Member):
    if [ctx.author.id, ctx.guild.id] in mods:
        try:
            source_channel = member.voice.channel
        except:
            source_channel = None
        if source_channel is None:
            await ctx.send('Member is not in a voice channel')
        else:
            i = 0
            for channel in ctx.guild.voice_channels:
                if channel is not source_channel and i < 8:
                    await member.move_to(channel)
                    i = i + 1
            await member.move_to(source_channel)
            if ctx.author.id == member.id:
                await ctx.send(f'why would you do that')
            else:
                await ctx.send(f'{member.name} woke up')
    else:
        await ctx.send("You don't have permission")


@client.command(brief='move entire channel')
async def move_channel(self, ctx, start_channel: discord.VoiceChannel, end_channel: discord.VoiceChannel):
    if [ctx.author.id, ctx.guild.id] in mods:
        for member in start_channel.members:
            await self.move(ctx, member, end_channel)
    else:
        await ctx.send("You don't have permission")


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# tasks @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@tasks.loop(seconds=10.0)
async def live_update_member_count():
    for guild in guild_mc:
        channel_found = False
        try:
            channel = client.get_channel(guild[1])
            channel_found = True
        except:
            pass

        if channel_found:
            guild_object = client.get_guild(guild[0])
            try:
                await channel.edit(rename="members-" + str(len(guild_object.members)))
            except:
                print("could not update member count " + str(datetime.today()))
        else:
            guild_mc.remove(guild)
            with open("guilds.txt", "r") as f:
                lines = f.readlines()
            with open("guilds.txt", "w") as f:
                for line in lines:
                    if line.strip("\n") != str(guild[0]) + "," + str(guild[1]):
                        f.write(line)


@live_update_member_count.before_loop
async def before():
    await client.wait_until_ready()

live_update_member_count.start()
client.run('TOKEN')

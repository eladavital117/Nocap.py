from discord.ext import commands
class custom_commands(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.command()
    async def does_it_work(self, ctx):
        await ctx.send('it works!')

def setup(client):
    client.add_cog(custom_commands(client))
    print('custom_commands loaded')
            
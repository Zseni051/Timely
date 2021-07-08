import discord
from discord.ext import commands
from datetime import datetime

import string

class developer(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("developer.py Loaded!")

    async def cog_check(self, ctx):
        if ctx.author.id in self.client.developerid: return True

    # tshutdown
    @commands.command()
    async def shutdown(self, ctx):
        await ctx.send('Shutting down...')
        exit()
    
    # tservers
    @commands.command()
    async def servers(self, ctx):
        activeservers = self.client.guilds

        serverlist = ""
        for guild in activeservers:
            guildname_checked = " "
            for i in guild.name:
                if i in string.ascii_letters or i.isspace():
                    guildname_checked += i
                else:
                    guildname_checked += "_"
            serverlist += f"Name: {guildname_checked}, MemberCount: {guild.member_count}, GuildID: {guild.id}\n"

        with open("result.txt", "w") as file:
            file.write(serverlist)
            
        # send file to Discord in message
        with open("result.txt", "rb") as file:
            await ctx.send("**guild names** only shown in characters `a-z`.\n**Unsupported** characters are displayed as `_`\noutput:", file=discord.File(file, "result.txt"))

    # tserverinvite <id> 
    @commands.command()
    async def serverinvite(self, ctx, target: int=0):
        if target == 0:
            await ctx.send("Give me a guild id")
            return
        targetguild = self.client.get_guild(target)

        link = await targetguild.text_channels[0].create_invite(max_age = 0, max_uses=0)
        await ctx.send(f"Invite for {targetguild.name}: {link}")

    # tleaveguild <id>
    @commands.command()
    async def leaveguild(self, ctx, id: int=0):
        id = id or ctx.guild.id
        targetguild = self.client.get_guild(id)
        await ctx.send(f"Left **{targetguild.name}**")
        await self.bot.leave_guild(targetguild)

    # tembedcolortest <color>
    @commands.command()
    async def embedcolortest(self, ctx, colortest: str="002240"):
        if "#" in colortest:
            colortest = colortest.replace("#", "")
        readableHex = int(colortest, 16)

        em = discord.Embed(title = "Embed Color Test",
                           description = f"Testing: {colortest}\nDefault Color: `#002240`",
                           color = readableHex,
                           timestamp=datetime.utcnow())

        await ctx.send(embed = em)

#####################################################################################################################################
def setup(client):
    client.add_cog(developer(client))
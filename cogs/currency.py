import asyncio
import random
from datetime import datetime
from typing import Optional

import discord
from discord import Member
from discord.ext import commands
from discord.ext.commands import command

from .functions import calc_DHMS_left, basic_embed, open_account, user_died


class currency(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("currency.py Loaded!")
    
    async def cog_check(self, ctx):
        if ctx.guild is not None: return True
        if not ctx.author.bot: return True

    # tbalance <user>
    @commands.command(aliases=['bal'])
    async def balance(self, ctx, target: Optional[Member]):
        cluster = self.client.mongodb["Currency"]["Main"]
        await open_account(self, ctx, ctx.author)
        user = target or ctx.author
        users = cluster.find_one({"id": user.id})
        command_syntax = f"Syntax: {self.client.serverprefix}balance <user>"

        if target is not None:
            targets = cluster.find_one({"id": target.id})
            if targets is None:
                await basic_embed(self, ctx,"", f"<:danger:848526668024250408> User doesn't exist in my database.",self.client.Red,f"{command_syntax}")
                return

        savings_amt = round(users["savings"])
        lifespan_amt = users["lifespan"]
        lifespan_amt = await calc_DHMS_left(lifespan_amt)

        result = f"**Savings:** ${savings_amt}\n**Lifespan:** {lifespan_amt}"

        em = discord.Embed(title = f"{user.name}'s balance",
                           description=result,
                           color = self.client.Yellow,
                           timestamp=datetime.utcnow())

        await ctx.reply(embed = em)

    # tprofile <user>
    @commands.command()
    async def profile(self, ctx, target: Optional[Member]):
        cluster = self.client.mongodb["Currency"]["Main"]
        await open_account(self, ctx, ctx.author)
        user = target or ctx.author
        users = cluster.find_one({"id": user.id})
        command_syntax = f"{self.client.serverprefix}profile <user>"

        if target is not None:
            targets = cluster.find_one({"id": target.id})
            if targets is None:
                await basic_embed(self, ctx,"", f"<:danger:848526668024250408> User doesn't exist in my database.\n{command_syntax}",self.client.Red,"")
                return

        savings_amt = users["savings"]
        lifespan_amt = users["lifespan"]
        lifespan_amt = await calc_DHMS_left(lifespan_amt)
        luck_amt = users["luck"]

        em = discord.Embed(color = self.client.Yellow,
                           timestamp=datetime.utcnow())
        em.set_author(name=f"{user.name}'s profile", icon_url = user.avatar_url)

        result = [(f"**Luck:** {luck_amt}"),
                  (f"**Job:** MgRonald's"),
                  (f"**Savings:** ${savings_amt}"),
                  (f"**Lifespan:** {lifespan_amt}")]

        em.add_field(name="Worth",value=f"{result[0]}\n{result[1]}\n{result[2]}\n{result[3]}",inline=True)
        
        await ctx.reply(embed = em)

    # trich <page>
    @commands.command()
    async def rich(self, ctx, page: int=1):
        await rich_globalrich(self, ctx, "rich", page)

    # tglobalrich <page>
    @commands.command()
    async def globalrich(self, ctx, page: int=1):
        await rich_globalrich(self, ctx, "global", page)

    # tpray
    @commands.command()
    async def pray(self, ctx, target: Optional[Member]):
        if self.client.cooldown.count(f"{ctx.author.id}pray") == 0:
            self.client.cooldown.append(f"{ctx.author.id}pray")
        else:
            await basic_embed(self, ctx,"", f"<:danger:848526668024250408> You are on a 30 second cooldown.",self.client.Red,"")
            return
        cluster = self.client.mongodb["Currency"]["Main"]
        await open_account(self, ctx, ctx.author)
        user = cluster.find_one({"id": ctx.author.id})
        luck = user["luck"]
        time = (random.randint(3600,86400)) # 1hour-1 day
        final_time = (time + (time * luck))
        if final_time > 86400: final_time = 86400
        time_string = await calc_DHMS_left(final_time)
        
        
        if target is not None:
            targets = cluster.find_one({"id": target.id})
            if targets is None:
                await basic_embed(self, ctx,"", f"<:danger:848526668024250408> User doesn't exist in my database.",self.client.Red,"")
                return
            try: await target.send(F"{ctx.author} has prayed for your wellbeing and so God has bestowed upon you an extra **{time_string}**!!")
            except discord.Forbidden: nothing=1
            await ctx.reply(f"God has bestowed upon **{target.name}** an extra **{time_string}**!!")
            
            cluster.update_one({"id":ctx.author.id},{"$set":{"luck":user["luck"]+0.1}})
        else: 
            await ctx.reply(f"God has bestowed upon you an extra **{time_string}**!!")

        target = target or ctx.author

        # update time
        targets = cluster.find_one({"id": target.id})
        new_lifespan_amt = targets["lifespan"] + final_time
        cluster.update_one({"id":target.id},{"$set":{"lifespan":new_lifespan_amt}})

        await asyncio.sleep(30)
        self.client.cooldown.remove(f"{ctx.author.id}pray")

    # tdaily
    @commands.command()
    async def daily(self, ctx):
        cluster = self.client.mongodb["Currency"]["Main"]
        user = ctx.author
        users = cluster.find_one({"id": user.id})
        cooldown = users["daily"]
        if cooldown < 1:
            await open_account(self, ctx, ctx.author)
            user = ctx.author
            await basic_embed(self, ctx,"Daily rewards", f"{user} claimed $100!",self.client.Yellow,"")

            # update values
            users = cluster.find_one({"id": user.id})
            new_savings_amt = users["savings"] + 250
            cluster.update_one({"id":user.id},{"$set":{"savings":new_savings_amt}})
            cluster.update_one({"id":user.id},{"$set":{"daily":86400}})
        else:
            cooldown_string = await calc_DHMS_left(cooldown)
            await basic_embed(self, ctx,"", f"<:danger:848526668024250408> You are on a 1 day cooldown.",self.client.Red,f"{cooldown_string} left")

    # tweekly
    @commands.command()
    async def weekly(self, ctx):
        cluster = self.client.mongodb["Currency"]["Main"]
        user = ctx.author
        users = cluster.find_one({"id": user.id})
        cooldown = users["weekly"]
        if cooldown < 1:
            await open_account(self, ctx, ctx.author)
            user = ctx.author
            await basic_embed(self, ctx,"Weekly rewards", f"{user} claimed $1000!",self.client.Yellow,"")

            # update values
            users = cluster.find_one({"id": user.id})
            new_savings_amt = users["savings"] + 750
            cluster.update_one({"id":user.id},{"$set":{"savings":new_savings_amt}})
            cluster.update_one({"id":user.id},{"$set":{"weekly":604800}})
        else:
            cooldown_string = await calc_DHMS_left(cooldown)
            await basic_embed(self, ctx,"", f"<:danger:848526668024250408> You are on a 1 week cooldown.",self.client.Red,f"{cooldown_string} left")
    
    # tmonthly
    @commands.command()
    async def monthly(self, ctx):
        cluster = self.client.mongodb["Currency"]["Main"]
        user = ctx.author
        users = cluster.find_one({"id": user.id})
        cooldown = users["monthly"]
        if cooldown < 1:
            await open_account(self, ctx, ctx.author)
            user = ctx.author
            await basic_embed(self, ctx,"Monthly rewards", f"{user} claimed $2000!",self.client.Yellow,"")

            # update values
            users = cluster.find_one({"id": user.id})
            new_savings_amt = users["savings"] + 2000
            cluster.update_one({"id":user.id},{"$set":{"savings":new_savings_amt}})
            cluster.update_one({"id":user.id},{"$set":{"monthly":2628000}})
        else:
            cooldown_string = await calc_DHMS_left(cooldown)
            await basic_embed(self, ctx,"", f"<:danger:848526668024250408> You are on a 1 month cooldown.",self.client.Red,f"{cooldown_string} left")

    #twork list
    @commands.command()
    async def worklist(self, ctx):
        em = discord.Embed(title = "List of jobs",
                           colour = self.client.Yellow,
                           timestamp=datetime.utcnow())

        em.add_field(name="MgRonald's",value="aliases: Ronalds, Maccas",inline=False)

        await ctx.reply(embed = em)

    # twork <job> <times>
    @commands.command()
    async def work(self, ctx, job: str=None, worktimes: str="1"):
        if job == None:
            await basic_embed(self, ctx,"", f"Work where?\n-Use the command `worklist` for a list of jobs.",self.client.Yellow,"")
            return
        
        if job not in ("Ronalds","ronalds","Maccas","maccas"):
            await basic_embed(self, ctx,"", f"Thats not a valid job!\n-Use the command `worklist` for a list of jobs.",self.client.Yellow,"")
            return
        
        if worktimes not in ("max","half"):
            worktimes = int(worktimes)
        if self.client.cooldown.count(f"{ctx.author.id}work") == 0:
            self.client.cooldown.append(f"{ctx.author.id}work")
        else:
            await basic_embed(self, ctx,"", f"<:danger:848526668024250408> You are on a 7 second cooldown.",self.client.Red,"")
            return
        cluster = self.client.mongodb["Currency"]["Main"]
        await open_account(self, ctx, ctx.author)
        user = ctx.author

        users = cluster.find_one({"id": user.id})

        if worktimes in ("max","half"):
            worktimescalc = users["lifespan"] / (6*3600)
            lifespan_amt = users["lifespan"] - ((6*3600) * worktimescalc)
            if lifespan_amt < 300:
                worktimescalc = worktimescalc - 1
            if worktimes == "half":
                worktimescalc = worktimescalc/2
            worktimes = int(worktimescalc)
            if worktimes == 0:
                await basic_embed(self, ctx,"", f"<:danger:848526668024250408> You will **DIE!** If you work for that long.",self.client.Red,"")
                return
        worktimes = abs(int(worktimes))

        lifespan_amt = users["lifespan"] - ((6*3600) * worktimes)
        if lifespan_amt < 300:
            await basic_embed(self, ctx,"", f"<:danger:848526668024250408> You will **DIE!** If you work for that long.",self.client.Red,"")
            return
        else:
            luck = users["luck"]
            min = 10
            max = 20

            #calculate savings from work
            work_amt = (random.randint(min,max))
            final_work_amt = (work_amt + (work_amt * luck))
            if final_work_amt > max:
                final_work_amt = max
            final_work_amt = int(final_work_amt * int(worktimes))
            savings_amt = round(users["savings"] + final_work_amt)

            em = discord.Embed(description = f"Worked for: 6h x{worktimes}\nTotal earnings: ${final_work_amt}",
                               colour = self.client.Yellow,
                               timestamp=datetime.utcnow())
            await ctx.reply(embed = em)

            #update values to database
            cluster.update_one({"id":user.id},{"$set":{"savings":savings_amt}})
            cluster.update_one({"id":user.id},{"$set":{"lifespan":lifespan_amt}})

        await asyncio.sleep(7)
        self.client.cooldown.remove(f"{ctx.author.id}work")
    
    # tsteal <user>
    @commands.command(aliases=['rob'])
    async def steal(self, ctx, target: Optional[Member]):
        cluster = self.client.mongodb["Currency"]["Main"]
        await open_account(self, ctx, ctx.author)
        user = ctx.author
        command_syntax = f"Syntax: {self.client.serverprefix}steal <user>"
        
        if target == None: 
            await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> No user was specified.",self.client.Red,f"{command_syntax}") 
            return
        
        users = cluster.find_one({"id": user.id})
        if users["savings"] < 500:
            await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> You need a minimum of $500 to steal from someone.",self.client.Red,"")
            return
        
        targets = cluster.find_one({"id": target.id})
        if targets is None:
            await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> User doesn't exist in my database.",self.client.Red,"")
            return
        
        if target.id == self.client.user.id:
            await ctx.reply("It's not worth it, trust me.")
            return

        if target.id == user.id:
            await ctx.reply("Yeh, because that makes sense.")
            return

        if self.client.cooldown.count(f"{ctx.author.id}steal") == 0:
            self.client.cooldown.append(f"{ctx.author.id}steal")
        else: 
            await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> You are on a 5 minute cooldown.",self.client.Red,"")
            return

        luck = users["luck"]
        # Dertermine if stealing was a success or fail
        stealing_chance = random.randint(1,100)
        final_stealing_chance = stealing_chance + (stealing_chance * luck)
        if final_stealing_chance > 80: # 20% chance
            # Calculate stolen ammount
            max = targets["savings"]
            stealmorethanhalf_chance = random.randint(1,100)
            stealmorethanhalf_chance = stealmorethanhalf_chance + (stealmorethanhalf_chance * luck)
            if stealmorethanhalf_chance > 95: stolen_percentage = random.randint(50,100) # 5% chance
            else: stolen_percentage = random.randint(1,49)
            stole_amt = int(max * stolen_percentage)
            if stole_amt > max:
                stole_amt = max

            # Update user's and target's values
            savings_amt = users["savings"] + stole_amt - 1000
            target_savings_amt = targets["savings"] - stole_amt
            cluster.update_one({"id":user.id},{"$set":{"savings":savings_amt}})
            cluster.update_one({"id":target.id},{"$set":{"savings":target_savings_amt}})

            await ctx.reply(f"You stole **${stole_amt}** from {target}")
            try: await target.send(f"{ctx.author} has stolen from you **${stole_amt}**")
            except discord.Forbidden: nothing = 1
        else:
            prison_sentence = 5 #days
            prison_sentence_seconds = 86400 * prison_sentence

            await ctx.reply(f"You got caught and spent {prison_sentence} days in prison")

            # Update user's values
            lifespan_amt = users["lifespan"] - prison_sentence_seconds
            if lifespan_amt < 1:
                await user_died(self, ctx, ctx.author)
                return
            cluster.update_one({"id":user.id},{"$set":{"lifespan":lifespan_amt}})
        
        await asyncio.sleep(300)
        self.client.cooldown.remove(f"{ctx.author.id}steal")
    
    #tgive <user> <amount>
    @commands.command()
    async def give(self, ctx, target: Optional[Member], ammount: str="0"):
        cluster = self.client.mongodb["Currency"]["Main"]
        await open_account(self, ctx, ctx.author)
        user = ctx.author
        command_syntax = f"Syntax: {self.client.serverprefix}give <user> <amount>"

        if target == None:
            await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> No user was specified.",self.client.Red,f"{command_syntax}")
            return
        
        if ammount == "0":
            await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> No ammount was specified.",self.client.Red,f"{command_syntax}")
            return

        users = cluster.find_one({"id": user.id})
        if ammount == "half": 
            ammount = users["savings"]/2
        elif ammount == "max":
            ammount = users["savings"]
        else:
            ammount = abs(int(ammount))
        
        if users["savings"] < ammount:
            await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> You don't have that much money.",self.client.Red,"")
            return

        targets = cluster = self.client.mongodb["Currency"]["Main"].find_one({"id": target.id})
        if targets is None:
                await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> User doesn't exist in my database.",self.client.Red,"")
                return
        
        if target.id == user.id:
            await ctx.reply("Yeh, because that makes sense.")
            return

        if self.client.cooldown.count(f"{ctx.author.id}give") == 0:
            self.client.cooldown.append(f"{ctx.author.id}give")
        else: 
            await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> You are on a 7 second cooldown.",self.client.Red,"")
            return
        
        
        user_savings_amt = users["savings"] - ammount
        target_savings_amt = targets["savings"] + ammount
        cluster.update_one({"id":user.id},{"$set":{"savings":user_savings_amt}})
        cluster.update_one({"id":target.id},{"$set":{"savings":target_savings_amt}})

        await ctx.reply(f"You gave {target} **${ammount}**")
        try: await target.send(f"{ctx.author} has given you **${ammount}**")
        except discord.Forbidden: nothing = 1

        await asyncio.sleep(7)
        self.client.cooldown.remove(f"{ctx.author.id}give")

        # twar <bet>
    
    #tgamble <user> <amount>
    @commands.command(aliases=['bet'])
    async def gamble(self, ctx, target: Optional[Member], bet: int=0):
        command_syntax = f"Syntax: {self.client.serverprefix}gamble <user> <amount>"
        if target == None:
            await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> No user was specified.",self.client.Red,f"{command_syntax}")
            return

        if bet == 0:
            await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> No ammount was specified.",self.client.Red,f"{command_syntax}")
            return

        user = ctx.author
        cluster = self.client.mongodb["Currency"]["Main"]
        await open_account(self, ctx, ctx.author)
        users = cluster.find_one({"id": user.id})

        if users["savings"] < bet:
            await basic_embed(self, ctx,f"", f"You don't have that much money",self.client.Yellow,"")
            return
        
        await basic_embed(self, ctx,f"", f"{target.mention} Do you wish to gamble with {user.mention}?\n`Yes/No`",self.client.Yellow,"5 secconds to respond")
        def check(m):
            return m.author == target and m.content in ("yes","Yes")
        try:
            response = await self.client.wait_for('message', check=check, timeout=5)
        except asyncio.TimeoutError:
            await basic_embed(self, ctx,f"", f"{target} took to long to answer.",self.client.Yellow,"")
            return

        if response.content not in ("yes","Yes"):
            await basic_embed(self, ctx,f"", f"gambling session canceled",self.client.Yellow,"")
            return
        
        await open_account(self, ctx, target)
        targets = cluster.find_one({"id": target.id})
        if int(targets["savings"]) < bet:
            await basic_embed(self, ctx,f"", f"{target} has insufficient funds",self.client.Yellow,"")
            return


        if self.client.cooldown.count(f"{ctx.author.id}gamble") == 0:
            self.client.cooldown.append(f"{ctx.author.id}gamble")
        else: 
            await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> You are on a 10 second cooldown.",self.client.Red,"")
            return
        
        # calculate win/loss/tie
        user_card_value = random.randint(1,13)
        user_card_value = user_card_value + (user_card_value * (users["luck"]/2))
        if user_card_value > 13:
            user_card_value = 13
        target_card_value = random.randint(1,13)
        target_card_value = target_card_value + (target_card_value * (targets["luck"]/2))
        if target_card_value > 13:
            target_card_value = 13
        
        user_card = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        user_card_index = int(user_card_value)
        target_card = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        target_card_index = int(target_card_value)
        types = [":hearts:", ":spades:", ":clubs:", ":diamonds:"]
        embed = [f"{user_card[user_card_index - 1]} of {random.choice(types)}",
                 f"{target_card[target_card_index - 1]} of {random.choice(types)}"]
        
        if user_card_value < target_card_value:
            if user_card_value == target_card_value:
                embed.append(f"Both parties walked away empty handed")
                embed.append("Tied!")
            else:
                win = 1
                embed.append(f"{target.mention} obtained ${bet} from {user.mention}!")
                embed.append(f"{target.name} Won!")
        else:
            win = 2
            embed.append(f"{user.mention} obtained ${bet} from {target.mention}!")
            embed.append(f"{user.name} Won!")
        
        em = discord.Embed(title = embed[3],
                           description = "",
                           colour = self.client.Yellow,
                           timestamp=datetime.utcnow())

        em.add_field(name=f"{user.name}'s Card",value=f"{embed[0]}")
        em.add_field(name=f"{target.name}'s Card",value=f"{embed[1]}")
        em.add_field(name=f"Outcome",value=f"{embed[2]}", inline=False)
        await ctx.send(embed = em)

        # update values
        if win == 1: 
            cluster.update_one({"id":target.id},{"$set":{"savings":targets["savings"] - bet}}) #update targets savings
            cluster.update_one({"id":user.id},{"$set":{"savings":users["savings"] + bet}}) #update users savings
        elif win == 2:
            cluster.update_one({"id":target.id},{"$set":{"savings":targets["savings"] - bet}}) #update targets savings
            cluster.update_one({"id":user.id},{"$set":{"savings":users["savings"] + bet}}) #update users savings
        
        await asyncio.sleep(10)
        self.client.cooldown.remove(f"{ctx.author.id}gamble")
#####################################################################################################################################
########################################################## D E V L O P E R ##########################################################
########################################################### C O M A N D S ###########################################################
#####################################################################################################################################
    # teditusercurrency
    @commands.command()
    async def editusercurrency(self, ctx, target: Optional[Member], type: str="", edit_int: int=0):
        command_syntax = f"Syntax: {self.client.serverprefix}editusercurrency <user> <type> <amount>"
        if ctx.author.id in self.client.developerid:
            edit_int = int(edit_int)
            
            if None in (target, type) or edit_int == 0:
                await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> Incorrect args, use the example below.",self.client.Red,f"{command_syntax}")
                return

            cluster = self.client.mongodb["Currency"]["Main"]
            targets = cluster.find_one({"id": target.id})
            if targets is None:
                await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> User doesn't exist in my database.",self.client.Red,"")
                return
            if type == "savings" or "lifespan":
                target_savings_amt = targets[type] + edit_int
                try:
                    cluster.update_one({"id":target.id},{"$set":{type:target_savings_amt}})
                except OverflowError:
                    await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> OverflowError.\nTry a smaller number maybe.",self.client.Red,"")
                    return
                await basic_embed(self, ctx,f"", f"<:info:848526617449070633> You successfully edited {target}'s {type} by {edit_int}",self.client.Blue,"")
            else: 
                await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> Incorrect type.",self.client.Red,"")
        return

    # topenaccountcurrency
    @commands.command()
    async def openaccountcurrency(self, ctx, target: Optional[Member]):
        if ctx.author.id in self.client.developerid:
            command_syntax = f"Syntax: {self.client.serverprefix}openaccountcurrency <user>"
            if target is None:
                await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> No user was specified.",self.client.Red,f"{command_syntax}")
                return

            cluster = self.client.mongodb["Currency"]["Main"]
            userdata = cluster.find_one({"id": target.id})
            if userdata is None:
                await open_account(self, ctx, target)

                await basic_embed(self, ctx,f"", f"<:info:848526617449070633> An account was oppened for {target}",self.client.Blue,"")
                return
            await basic_embed(self, ctx,f"", f"<:danger:848526668024250408> {target} already has an account",self.client.Red,"")

#####################################################################################################################################
async def rich_globalrich(self, ctx, type, page):
    page = abs(int(page))
    if page > 99: page = 99
    cluster = self.client.mongodb["Currency"]["Main"]
    list_of_users = cluster.find().sort("savings", -1)
    rich_string = ""
    cycle_int = 0
    for x in list_of_users:
        if "savings" in x:
            savings = x["savings"]
            if savings != 0:
                richuser = await self.client.fetch_user(x['id'])
                if type == "global" or richuser in ctx.guild.members: 
                    cycle_int = cycle_int + 1
                    if cycle_int > ((page*10) - ((page-1)*10)) or page == 1:
                        rich_string += f"**${savings}** - {richuser}\n"
                    if cycle_int == int(page*10): break
    if rich_string == "":
        await ctx.send("No one with money here.")
        return
        
    em = discord.Embed(color=self.client.Yellow)
    if type == "global": em.add_field(name=f"Richest users in **TimelyBot**", value=rich_string, inline=False)
    else: em.add_field(name=f"Richest users in **{ctx.guild.name}**", value=rich_string, inline=False)

    em.set_footer(text=f"Page: {page}")
    em.timestamp = datetime.utcnow()
        
    await ctx.send(embed=em)

#####################################################################################################################################
def setup(client):
    client.add_cog(currency(client))

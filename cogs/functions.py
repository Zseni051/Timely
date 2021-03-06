import discord
from datetime import datetime

#####################################################################################################################################
########################################################## C U R R E N C Y ##########################################################
######################################################### F U N C T I O N S #########################################################
#####################################################################################################################################
async def calc_DHMS_left(lifespan_amt):
    if lifespan_amt == 0:
        return 0
    lifespan_amt_days = int(lifespan_amt/86400)
    lifespan_amt_hours = int((lifespan_amt - (lifespan_amt_days * 86400))/3600)
    lifespan_amt_minutes = int((lifespan_amt - (lifespan_amt_days * 86400) - (lifespan_amt_hours * 3600))/60)
    lifespan_amt_seconds = int(lifespan_amt - (lifespan_amt_days * 86400) - (lifespan_amt_hours * 3600) - (lifespan_amt_minutes * 60))

    result = []
    loopcycleint = 0
    loopcycleint2 = 0
    break_at = 2
    appendcalc = [lifespan_amt_days,lifespan_amt_hours,lifespan_amt_minutes,lifespan_amt_seconds]
    for time in appendcalc:
        loopcycleint = loopcycleint + 1
        if time != 0:
            loopcycleint2 = loopcycleint2 + 1
            if loopcycleint == 1: 
                type = "days"
                result.append(f"{time} {type}")
            if loopcycleint == 2: 
                if time == 1: type = "hour"
                else: type = "hours"
                if loopcycleint2 == break_at: 
                    result.append(f" and {time} {type}")
                    break
                result.append(f"{time} {type}")
            if loopcycleint == 3: 
                type = "minutes"
                if loopcycleint2 == break_at: 
                    result.append(f" and {time} {type}")
                    break
                result.append(f"{time} {type}")
            if loopcycleint == 4: 
                type = "seconds"
                if loopcycleint2 == break_at: 
                    result.append(f" and {time} {type}")
                    break
                result.append(f"{time} {type}")
    result = " ".join(result)
    return result

async def open_account(self, ctx, user):
    cluster = self.client.mongodb["Currency"]["Main"]
    userdata = cluster.find_one({"id": user.id})

    DefaultTime = self.client.DefaultTime
    Alive = False
    if userdata is None:
        users = {"id": user.id, "savings": 0, "lifespan": DefaultTime,"luck": 0,
                 "commands_used": 0, "stolen": 0,
                 "daily": 0, "weekly": 0, "monthly": 0,
                 "pray": 0}
        cluster.insert_one(users)
        Alive = True
    else:
        if userdata["lifespan"] == -666: 
            Alive = True
    if Alive == True:
        em = discord.Embed(title = f"The clock is ticking {user.name}!",
                           description = f"Start using various commands to gain more time, you only have **{int(DefaultTime/86400)} days** left!",
                           color = self.client.Blue,
                           timestamp=datetime.utcnow())
        try: await user.send(embed = em)
        except: 
            if ctx != None: await ctx.send(embed = em)
        cluster.update_one({"id":user.id},{"$set":{"lifespan":DefaultTime}})
    return True

async def user_died(self, ctx, user):
    cluster = self.client.mongodb["Currency"]["Main"]
    await open_account(self, ctx, user)

    em = discord.Embed(title = f"{user} Died!.",
                   description = "-You met the end of your lifespan. \n-You lost all your items and savings. \n-You get to keep whatever was hidden in your treasure chest.",
                   color = self.client.Red,
                   timestamp=datetime.utcnow())
    try: await user.send(embed = em)
    except: 
        if ctx != None: await ctx.send(embed = em)
    cluster.update_one({"id":user.id},{"$set":{"savings":0}})
    cluster.update_one({"id":user.id},{"$set":{"lifespan":-666}})
    return

#####################################################################################################################################
########################################################### G E N E R A L ###########################################################
######################################################### F U N C T I O N S #########################################################
#####################################################################################################################################
def user_avatar_url(user):
    try: user_avatar_url = user.avatar.url
    except: user_avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
    return user_avatar_url

def basic_embed(title, description,color, footer: str=""):
    em = discord.Embed(title = title,
                       description = description,
                       color = color)
    if footer is not None:
        em.set_footer(text=footer)
    em.timestamp = datetime.utcnow()
    return em


class View_Timeout(discord.ui.View):
    def __init__(self, timeout):
        super().__init__(timeout=timeout)
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)

class ButtonItem(discord.ui.Button):
    """Create a basic button.
    
    Function must look like:
        1: :code:`function(self, emoji, interaction, arg)`
            2: :code:`do stuff here`
            3: :code:`return arg`"""
    def __init__(self, self2, emoji, function, arg):
        self.self2 = self2
        self.function = function
        self.arg = arg
        super().__init__(emoji=emoji, style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        self.arg = await self.function(self.self2, self, interaction, self.arg)

class DropdownItem(discord.ui.Select):
    """Create a basic dropdown menu.
    
    Function must look like:
        1: :code:`function(self, emoji, interaction, arg)`
            2: :code:`do stuff here`
            3: :code:`return arg`"""
    def __init__(self, self2, placeholder, min, max, selects, function, arg):
        self.self2 = self2
        self.function = function
        self.arg = arg
        options = []
        for x in selects:
            options.append(discord.SelectOption(label=x))
        super().__init__(placeholder=placeholder, min_values=min, max_values=max, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.arg = await self.function(self.self2, self, interaction, self.arg)
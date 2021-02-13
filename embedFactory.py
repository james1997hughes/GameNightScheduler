import discord
import discord.ext
import datetime

def embedFactory(eventName, desc, game, unixTime, mentions, creator, footerText):
    friendlyTime = ""
    try:
        friendlyTime = datetime.datetime.fromtimestamp(int(unixTime)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        friendlyTime = "Error"
    myEmbed = discord.Embed(
        title=eventName,
        description=desc)
    myEmbed.colour = discord.Colour.random()
    myEmbed.add_field(name="Time",
                      value=friendlyTime,
                      inline=False)
    myEmbed.add_field(name="Mentions",
                      value=mentions,
                      inline=False)
    myEmbed.set_footer(text=footerText)
    myEmbed.set_author(name=game, icon_url="https://store-images.s-microsoft.com/image/apps.45782.9007199266731945.debbc4f1-cde0-491b-8c6f-b6b015eecab6.4716cccc-5f37-4bb5-9db1-0c1dbc99003f?mode=scale&q=90&h=200&w=200&background=%23000000")

    return myEmbed
 
import discord
import discord.ext
import datetime
import sqlite3
import logging

def getAttendees(active, cursor, eventId, serverId):
    logging.info("in getmentions")
    statement = f'''SELECT eu.userId, eu.userName FROM events_users eu 
                    JOIN events e on eu.fk_events = e.id 
                    JOIN servers s on s.id = e.fk_servers
                    WHERE e.event_id = {eventId} AND s.id = {serverId}'''
    results = cursor.execute(statement).fetchall()
    logging.info(statement)
    logging.info(results)
    mentions = ""
    if (len(results) < 1):
        return "Nobody is attending..."
    try:
        for result in results:
            if active:
                mentions += f"<@!{result[0]}> "
            else:
                mentions += f"{result[1]} "
    except:
        mentions = "Nobody is attending..."
    return mentions

def embedFactory(eventName: str, desc: str, game: str, unixTime: int, creator: str, footerText: str, eventId: int, serverId: int, preview: bool, mention: bool):
    conn = sqlite3.connect('schedulerData.db')
    cursor = conn.cursor()
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
    logging.info("Before IF")
    if not preview:
        if(mention):
            #also todo is the cleanup for above refactor, testing joining and describe shows correct members, implement leaving,
            #implement time retrying on schedule, implement rescheduling (voting maybe? or just owner). Once this basic functionality
            #complete, tidy up code and make reasonably clean.
            myEmbed.add_field(name="Attendees",
                            value=getAttendees(True, cursor, eventId, serverId),
                            inline=False)
        else:
            myEmbed.add_field(name="Attendees",
                            value=getAttendees(False, cursor, eventId, serverId),
                            inline=False)
    myEmbed.set_footer(text=footerText)
    myEmbed.set_author(name=game, icon_url="https://store-images.s-microsoft.com/image/apps.45782.9007199266731945.debbc4f1-cde0-491b-8c6f-b6b015eecab6.4716cccc-5f37-4bb5-9db1-0c1dbc99003f?mode=scale&q=90&h=200&w=200&background=%23000000")
    logging.info(myEmbed.to_dict())
    return myEmbed
 
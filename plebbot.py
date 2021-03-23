import discord
import re
import urllib.request;
import urllib.error;
import urllib.parse;
import random;

TOKEN = '<INSERT TOKEN HERE>';
gumbootURL = 'https://www.google.com/search?q=gumboot&client=firefox-b-d&tbs=qdr:m&tbm=isch'
imageURL = 'https://www.google.com/search?q=\n0\n&client=firefox-b-d&tbm=isch'
gumbootFile = 'gumboot'
imageFIle = 'image'
weatherRootURL = 'http://www.bom.gov.au/\n0\n/forecasts/towns.shtml'
weatherTownURL = 'http://www.bom.gov.au/places/\n1\n/\n0\n/'
weatherStates = ['nsw', 'vic', 'qld', 'wa', 'sa', 'tas', 'act', 'nt']
townsRe = r"""id=.*?"/
0
/forecasts/([A-z]+)\.shtml">([A-z ]+)</a></td>"""
observationRe = r'<li *class="summary" *id="summary-1">(.*?)id="summary-2"'
forecastRe = r'<div class="forecasts">((.*?<dl class="forecast-summary">.*?</dl>){7})'
commandRe = r'^ *\\plebbot *';

client = discord.Client();

@client.event
async def on_message(message):
    print("M: "+message.content);
    if (message.author == client.user):
        return;

    #check for command and split args
    if (isCommand(message.content)):
        args = splitArgs(message.content);
        print("COM: " + str(args));

        #hello command
        if (args[0] == 'hello'):
            msg = '{0.author.mention} you are a gumboot'.format(message);
            await message.channel.send(msg);

        #shutdown command
        if (args[0] == 'shutdown'):
            msg = '{0} shutting down...'.format(message.author.mention);
            await message.channel.send(msg);
            await client.close();
        
        #gumboot command
        if (args[0] == 'gumboot'):
            await CommandGumboot(message);

        #weather command
        if (args[0] == 'weather'):
            msg = await CommandWeather(args);
            await message.channel.send(msg);
            
        #the any image request (use at your own risk!)
        if (args[0] == 'img'):
            res = await CommandImage(args);
            if (res[1] is not None):
                #then we have a discord file, send it
                await message.channel.send(res[0], file=res[1]);
            else:
                await message.channel.send(res[0]);            

async def CommandGumboot(message):
    #https://www.google.com/search?q=gumboot&client=firefox-b-d&tbs=qdr:w,itp:photo&tbm=isch
    download = DownloadSite(gumbootURL);
    if (download[0] is not None):
        await message.channel.send(download[0]);
    else:
        page = download[1].decode('utf-8');
        #parse the page to find the image urls
        #imgURLs = re.findall(r'src="data:image[^"]*"', page);
        #print(page);
        imgURLs = re.findall(r'"ou":"[^"]*', page);
        print("Got " + str(len(imgURLs)) + " images");
        imgURL = imgURLs[random.randrange(len(imgURLs))];
        imgURL = re.sub(r'^"ou":"', '', imgURL)
        print(imgURL);
        imgURL = re.sub(r'\\u00([0-9a-fA-F])', r'%\1', imgURL)
        imgURL = re.sub(r'%26', r'&', imgURL);
        imgURL = re.sub(r'%3[dD]', r'=', imgURL);
        http = re.search(r'https?://', imgURL);
        if (http is not None):
            http = http.group(0);
            imgURL = imgURL[len(http):];
        #imgURL = urllib.parse.quote(imgURL);
        print(http + imgURL);
        #save the image so we can upload it to discord
        download = DownloadSite(http+imgURL);
        if (download[0] is not None):
            await message.channel.send(download[0]);
        else:
            #get the file extension
            ext = re.search(r'([^.]*)\?[^?]*$', imgURL)
            #ext = re.findall(r'[^.]*$', imgURL);
            if (ext is None):
                ext = "jpg"
            else:
                ext = ext.group(1);
            imgF = open(gumbootFile+"."+ext, "wb");
            imgF.write(download[1]);
            imgF.close();

            #now send it
            dfile = discord.File(gumbootFile+"."+ext);
            await message.channel.send("Enjoy your random gumboot", file=dfile)
            
async def CommandImage(args):
    if (len(args) < 2):
        return ("img <query>", None)
    #get the thing the user wants a picture of
    query = ' '.join(args[1:])
    #convert it to a http safe string
    safeQuery = urllib.parse.quote(query);
    url = re.sub('\n0\n', safeQuery, imageURL);
    print(url);
    #get an image url
    download = DownloadSite(url);
    if (download[0] is not None):
        return (download[0], None)
    imgURL = extractRandUrl(download);
    #download the image
    download = DownloadSite(imgURL);
    if (download[0] is not None):
        return (download[0], None);

    #get the file extension
    ext = re.search(r'([^.]*)\?[^?]*$', imgURL)
    #ext = re.findall(r'[^.]*$', imgURL);
    if (ext is None):
        ext = "jpg"
    else:
        ext = ext.group(1);
    imgF = open(gumbootFile+"."+ext, "wb");
    imgF.write(download[1]);
    imgF.close();

    #now send it
    dfile = discord.File(gumbootFile+"."+ext);
    return ("Enjoy your random " + query, dfile);
    #await message.channel.send("Enjoy your random gumboot", file=dfile)

    
    #return "hi"
    
def extractRandUrl(download):
    if (download[0] is not None):
        return [];
    page = download[1].decode('utf-8');
    #parse the page to find the image urls
    #imgURLs = re.findall(r'src="data:image[^"]*"', page);
    #print(page);
    imgURLs = re.findall(r'"ou":"[^"]*', page);
    print("Got " + str(len(imgURLs)) + " images");
    imgURL = imgURLs[random.randrange(len(imgURLs))];
    imgURL = re.sub(r'^"ou":"', '', imgURL)
    print(imgURL);
    imgURL = re.sub(r'\\u00([0-9a-fA-F])', r'%\1', imgURL)
    imgURL = re.sub(r'%26', r'&', imgURL);
    imgURL = re.sub(r'%3[dD]', r'=', imgURL);
    http = re.search(r'https?://', imgURL);
    if (http is not None):
        http = http.group(0);
        imgURL = imgURL[len(http):];
    return http + imgURL;

async def CommandWeather(args):
    #weather <state> <town/warning>
    #1 arg, only the weather arg, give a help message
    numArgs = len(args);
    if (numArgs == 1):
        return WeatherHelpMessage("Available States:", weatherStates);

    if (numArgs > 3):
        return WeatherHelpMessage(None, None);
    
    #2 args, we were possibly given a state
    if (numArgs >= 2):
        if (args[1] not in weatherStates):
            #a bad state
            msg = "'"+args[1] + "' is not a state\nAvailable States:"
            return WeatherHelpMessage(msg, weatherStates);
        
        if (numArgs == 2):
            #only a valid state, give the list of valid towns
            towns = WeatherGetTowns(args[1])
            if (towns[0] is not None):
                return towns[0];
            #the list of towns is a list of tuples, so make a single list of key words
            townids = [];
            for town in towns[1]:
                townids.append(town[0]);
            print(str(townids))
            return WeatherHelpMessage("Available Towns:", townids);

    #3 args, we were given a possible town
    #if we get here then the state has already been checked
    if (numArgs >= 3):
        print("wtf")
        towns = WeatherGetTowns(args[1]);
        if (towns[0] is not None):
            return towns[0];
        towns = towns[1]; #(id, name)
        town = [i for i in towns if i[0] == args[2]];

        #if there is something in town, then the name is valid
        if (town == []):
            #we were given a bad town give the help message
            townIDs = [];
            for t in towns:
                townIDs.append(t[0]);
            msg = "'"+args[2] + "' is not a town\nAvailable Towns:"
            return WeatherHelpMessage(msg, townIDs);
        
        #we have a good state and town, look up the weather
        town = town[0];
        return WeatherInTown(args[1], town[0], town[1]);




#(Error|None, (Towns)|None)
#Towns = (id, name)
def WeatherGetTowns(state):
    if (state not in weatherStates):
        return ("Internal Error - Bad State", None);

    wURL = re.sub(r'\n0\n', state, weatherRootURL);
    print(wURL);
    download = DownloadSite(wURL);
    if (download[0] is not None):
        return ("Internal Error - Towns Download - " + download[0], None);
    
    #there is a page to apply some regex to
    page = download[1].decode('utf-8');
    regex = re.sub(r'\n0\n', state, townsRe);
    towns = re.findall(regex, page);
    towns = sorted(towns);
    return (None, towns);

#Weather help message
def WeatherHelpMessage(helpExtra, helpList):
    msg = "weather <state> <town>\n";
    if (helpExtra is not None):
        msg += helpExtra+"\n";
    if (helpList is not None):
        for item in helpList:
            msg += item + " "
    return msg;

def WeatherInTown(state, townID, townName):
    #just assume that the state and town exist
    wURL = re.sub(r'\n0\n', townID, weatherTownURL);
    wURL = re.sub(r'\n1\n', state, wURL);
    #print(wURL);
    download = DownloadSite(wURL);
    if (download[0] is not None):
        return "Internal Error - Weather Download - " + download[0]
    
    page = download[1].decode('utf-8');
    #get the observation information
    obsInfo = re.search(observationRe, page, flags=re.DOTALL);
    #get the forecast
    foreInfo = re.search(forecastRe, page, flags=re.DOTALL);

    #start to fill in weather info
    currTemp = "??"
    obsLoc = "??"
    humidity = "??"
    windSpeed = "??"
    currRain = "??"
    currMin = "??"
    currMax = "??"
    #(day, tmin, tmax, rain, rain chance)
    forecast = []

    #process the obs
    if (obsInfo is not None):
        obsInfo = obsInfo.group(1);
        #current temp
        res = re.search(r'<li class="airT">([0-9.]+)', obsInfo, flags=re.DOTALL)
        if (res is not None):
            currTemp = res.group(1) + " C";
        #observation location
        res = re.search(r'<p class="station-name"><a.*?>(.*?)</a>', obsInfo, flags=re.DOTALL);
        if (res is not None):
            obsLoc = res.group(1);
        #humidity
        res = re.search(r'<td>(.*?)</td><th>Humidity', obsInfo, flags=re.DOTALL);
        if (res is not None):
            humidity = res.group(1);
        #windSpeed
        res = re.search(r'<td data-kmh="(.*?)"', obsInfo, flags=re.DOTALL);
        if (res is not None):
            windSpeed = res.group(1) + "km/h";
        #min so far
        res = re.search(r'<li class="extT">.*?Lowest <span class="temp">([0-9.]+)', obsInfo, flags=re.DOTALL);
        if (res is not None):
            currMin = res.group(1) + " C";
        #max so far
        res = re.search(r'<li class="extT">.*?Highest <span class="temp">([0-9.]+)', obsInfo, flags=re.DOTALL);
        if (res is not None):
            currMax = res.group(1) + " C";

    #now process the forecast
    if (foreInfo is not None):
        foreInfo = foreInfo.group(1);
        #grab the 7 forecast summary sections
        foreSum = re.findall(r'<dl class="forecast-summary">(.*?)</dl>', foreInfo, flags=re.DOTALL);

        if (len(foreSum) == 7):
            #process the first entry, since this would be todays stuff
            forecastToday = foreSum[0];
            #print(forecastToday);
            res = re.search(r'>([^>]*?)</dd>\s*$', forecastToday, flags=re.DOTALL);
            if (res is not None):
                currRain = res.group(1);

            #now for the rest of the days
            for i in foreSum[1:]:
                #(day, tmin, tmax, rain, rain chance)
                day = tmin = tmax = rain = rainch = "??";

                #the day of the forecast
                res = re.search(r'<dt class="date">[^<]*<[^>]*>\s+(.*?)\s+<', i, flags=re.DOTALL);
                if (res is not None):
                    day = res.group(1);
                #minimum temperature
                res = re.search(r'<dd class="min">([0-9.]+)', i, flags=re.DOTALL);
                if (res is not None):
                    tmin = res.group(1) + " C";
                #maximum temperature
                res = re.search(r'<dd class="max">([0-9.]+)', i, flags=re.DOTALL);
                if (res is not None):
                    tmax = res.group(1) + " C";
                #rain description
                res = re.search(r'<dd class="summary">([^<]+)<[^>]+>[^<]*[^>]*rain range', i, flags=re.DOTALL);
                if (res is not None):
                    rain = res.group(1);
                #rain chance
                res = re.search(r'rain pop">[^<]*<[^>]+>[^<]+<dd class="pop">([0-9.%]+)', i, flags=re.DOTALL);
                if (res is not None):
                    rainch = res.group(1);

                forecast.append((day, tmin, tmax, rain, rainch));
        else:
            print("Got " + str(len(foreSum)) + "forecast days")

    #print(currTemp);
    #print(obsLoc);
    #print(humidity);
    #print(windSpeed);
    #print(currRain);
    #print(currMin);
    #print(currMax);
    #print(forecast);

    msg = "**"+townName + ", " + state.upper() + "**\n";
    msg += "**"+currTemp+"** ("+obsLoc+")\n";
    msg += "Min: " + currMin + "   Max: " + currMax + "   Rain: " + currRain + "\n";
    msg += "Wind: " + windSpeed + "   Humidity: " + humidity + "\n";
    msg += "\n**Forecast**\n";

    start = True;
    for i in forecast:
        if (not start):
            msg += "\n--------------------\n";
        start = False;
        #(day, tmin, tmax, rain, rain chance)
        msg += "__"+i[0]+"__      " + i[1] + " - " + i[2] + "\n";
        msg += i[3] + " (" + i[4] + ")"
    return msg;


#(Error|None, Bytes|None)
def DownloadSite(url):
    response = "";
    tries = 0;
    while (tries < 3):
        try:
            rec = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'});
            r = urllib.request.urlopen(rec);
            break;
        except urllib.error.HTTPError:
            response = "404 Error, probably"
            tries += 3;
            break;
        except:
            response = "Timeout, Probably"
            tries += 1;
            
    if (tries >= 3):
        return (response, None);
        
    return (None, r.read());
    
#returns a list of argments to the command
def splitArgs(command):
    #remove any extra space or the bot command symbol
    command = re.sub(r'^ +| +$|' + commandRe, "", command.lower());
    #split the command based on white space
    return re.split(r' +', command);

#checks if a string can be a command
def isCommand(command):
    res = re.findall(commandRe, command);
    return len(res) == 1;

@client.event
async def on_ready():
    print('Logged in as ' + client.user.name + " ("+ str(client.user.id) + ") ")
    status = discord.Activity(name="YOU SLEEP", type=discord.ActivityType.watching)
    await client.change_presence(status=discord.Status.online, activity=status)

# @client.event
# async def on_typing(channel, user, when):
    # if (channel.name != 'bot'):
        # return;
    # await channel.send(user.mention + " What are you typn'?")

client.run(TOKEN)
print("Shutdown cleanly");

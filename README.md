# Gumboot and Weather Forcast Bot
A simple bot capable of serving pictures or the weather forecast to users on request. It utilises the discord bot API, web requests and lots of regex for scraping data. It pulls the weather data from the BOM and retrieves images from google search. An action is directed at the bot by using its command sequence followed by the desired action. For example, "\plebbot gumboot" will ask the bot to serve a random image of a gumboot.

## How to use
In order to use this bot, you will need to create your own bot token. This will enable the bot to join your discord server and for you to interact with it. Add this token to the bot at the top of the python file. Additionally, the bot requires the "discord" python library to be installed. Once complete, you will need to run the bot using python. This can be on your local machine or on a remote server.\
`$ python plebbot.py`

## Serving images
Currently, the image serving capacity of the bot is limited to pictures of gumboots only as there is no check on what image the user is requesting. However, the code for serving any image is implemented and can be used (at your own risk!). When an image is requested, the bot performs a google image search and randomly selects an image from top results and posts it in the same channel it was requested from.\
To request an image of a gumboot: `\plebbot gumboot`\
To request a specified image: `\plebbot img <image>`

## Serving the weather
The bot supports obtaining the weather for many locations within Australia (any location the BOM has weather data for). The channel the weather is requested from is where the bot will post the result.\
To request the weather: `\plebbot weather <state> <town>`\
In the above command, both the state and town can be omitted in which case the bot will return valid states or towns. Otherwise, the 7-day weather forecast for the given location will be returned. An example is below.
```
Melbourne, VIC
12.1 C (Melbourne (Olympic Park))
Min: 8.2 C   Max: 12.5 C   Rain: Mostly cloudy.
Wind: 7km/h   Humidity: 80%\

Forecast
Thu 4 Jul      6 C - 15 C
Morning fog then mostly sunny. (5%)
--------------------
Fri 5 Jul      5 C - 18 C
Mostly sunny. (0%)
--------------------
Sat 6 Jul      8 C - 18 C
Partly cloudy. (10%)
--------------------
Sun 7 Jul      12 C - 16 C
Showers. (90%)
--------------------
Mon 8 Jul      8 C - 16 C
Shower or two. (50%)
--------------------
Tue 9 Jul      8 C - 16 C
Shower or two. (60%)
```
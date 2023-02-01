'''/////////////////////////////////////////////////////////
File name: bot.py
File function: react to commands that users indicate about
the direction of the fastest road in car, taking into
account the state of traffic in real time, from two points
in the city of Barcelona, provided by igo.py.
Date: 20_05_2021
/////////////////////////////////////////////////////////'''

############################################################
#                       IMPORTS
############################################################

# implements pseudo-random number generators for various distributions.
import random
# access functionalities dependent on the Operating System
import os
# code and data structures related to the acquisition and storage of graphs
# corresponding to maps, congestion, and route calculations.
import igo
# retrieve, model, analyze, and visualize street networks from OpenStreetMap
import osmnx as ox
# connects to Open Street Maps to generate maps with lines and markers
from staticmap import StaticMap, CircleMarker, Line
# import Telegram's API
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
# display the current date
import datetime

############################################################
#                CONSTANTS AND VARIABLES
############################################################
# The place we will be treat in this file is Barcelona
PLACE = 'Barcelona, Catalonia'
# Name of the file where we will save the graph
GRAPH_FILENAME = 'barcelona.graph'
# Size of the images that will be saved
SIZE = 800
# URL from where we can get data from Barcelona's streets
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
# URL from where we can get data from Barcelona's congestions
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'

# When starting the program does once:
# Download graph
graph = igo.get_graph()
# Download highways
highways = igo.download_highways(HIGHWAYS_URL)
# Download congestions
congestions = igo.download_congestions(CONGESTIONS_URL)
# Save the start time of the igraph creation
START_TIME = datetime.datetime.now()
# Create a graph with congestion and itime attributes.
IGRAPH = igo.build_igraph(graph, highways, congestions)


############################################################
#                       FUNCTIONS
############################################################

def start(update, context):
    '''----------------------------------------------------
    * Name: start
    * Function: Greets and starts the conversation. It will
                run when the bot receives the /start
                message.
    * Parameters: update and context: objects that allow us
                  to have more details of the user
                  information and perform actions with the
                  bot.
    * Return: A message greeting the user.
              A message to the terminal indicating who have
              started using IGo.
    ----------------------------------------------------'''
    # Print on the terminal a message indicating who have started using IGo.
    print(update.effective_chat.first_name + " is using IGo.")
    # Send a message greeting the user
    message = "Hi, " + update.effective_chat.first_name
    message += "! 👋 I am IGo. Click /help and I will let you now which are "
    message += "my main functions."
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
        )


def help(update, context):
    '''---------------------------------------------------
    * Name: help
    * Function: Offers help on available orders.
    * Parameters: update and context: objects that allow
                  us to have more details of the user
                  information and perform actions with
                  the bot.
    * Return: A message with the possible commands and
              their definitions.
              A message to the terminal indicating that
              help have been requested.
    ---------------------------------------------------'''
    # Print on the terminal a message to indicate who has requested help
    print(update.effective_chat.first_name + " is asking for help.")

    message = "I am a bot with commands: \n/start - starts the "
    message += "conversation. \n/help - offers help on available orders."
    message += "\n/author - shows the name of the project's authors."
    message += "\n/where - shows the actual position of the user. This "
    message += "function is called every time the user arrives a new "
    message += "localitzacion. \n/pos - sets the user's current position to a "
    message += "false position.\n/go destination - shows to the user a map to "
    message += "get from their current position to destination point chosen "
    message += "for the shortest path according to the concept of speed."
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
        )


def author(update, context):
    '''---------------------------------------------------
    * Name: author
    * Function: Shows the name of the project's authors.
    * Parameters: update and context: objects that allow
                  us to have more details of the
                  userinformation and perform actions
                  with the bot.
    * Return: A message with the name of the authors.
              A message to the terminal indicating
              authors have been asked.
    ---------------------------------------------------'''
    # Print on the terminal a message indicating who has asked for the authors
    print(update.effective_chat.first_name + " is asking for the authors.")

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🖋️My authors are Valèria Caro Via and Esther Fanyanàs Ropero."
        )


def location(update, context):
    '''---------------------------------------------------
    * Name: location
    * Function: When a user sends a location it takes the
                position and saves it.
    * Parameters: update and context: objects that allow
                us to have more details of the user
                information and perform actions with the
                bot.
    * Return: A message to the terminal with the location.
    ---------------------------------------------------'''
    # Take the location coordinates
    lat, lon = update.message.location.latitude, update.message.location.longitude
    context.user_data['location'] = [lat, lon]
    # Print on the terminal a message to indicate who has requested author
    print(update.effective_chat.first_name + " is in:")
    print(context.user_data['location'])


def where(update, context):
    '''----------------------------------------------------
    * Name: where
    * Function: Shows the actual position of the user.
                This function is called every time the
                user arrives a new localitzacion.
    * Parameters: update and context: objects that allow
                us to have more details of the user
                information and perform actions with the
                bot.
    * Return: A message with the coordinates and an image
              of the user's current position.

    ----------------------------------------------------'''
    # Print on the terminal a message indicating the user who wants to know
    # her/his position
    message = update.effective_chat.first_name
    message += " wants to know her/his position."
    print(message)

    try:
        if type(context.user_data['location']) == list:
            lat, lon = context.user_data['location']
        # If the locations are not given as a list, will force it looks
        # like them.
        else:
            location = context.user_data['location'].replace("(", "[")
            location = location.replace(")", "]")
            lat, lon = ox.geocode(location)
        # Create a map and put a point in the location coordinates
        file = "%d.png" % random.randint(1000000, 9999999)
        map = StaticMap(500, 500)
        map.add_marker(CircleMarker((lon, lat), 'blue', 10))
        image = map.render()
        image.save(file)
        # Send a message with the location coordinates
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='You are in the coordinates %f %f' % (lat, lon))
        # Send a map with the location
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(file, 'rb'))
        os.remove(file)

    except Exception as e:
        # In case there is any error with the location or it has not been sent,
        # it will be notified
        print(e)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='💣 Please, first you need to send me your location.')


def pos(update, context):
    '''---------------------------------------------------
    * Name: pos
    * Function: Sets the user's current position to a
                false position.
    * Parameters: update and context: objects that allow
                us to have more details of the user
                information and perform actions with the
                bot.
    * Return: A message saying the location where the path
              will start.
              A message to the terminal indicating the
              position has been falsified.
    ---------------------------------------------------'''
    try:
        # Print on the terminal a message indicating the position has been
        # falsified
        message = update.effective_chat.first_name
        message += " has falsified the position."
        print(message)
        # Saves the source location falsified by the user
        context.user_data['location'] = update.message.text[5:] + ", Barcelona"
        # Send a message saying the new location
        message2 = "You are starting the route from "
        message2 += str(context.user_data['location']) + "📍"
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message2
        )

    except Exception as e:
        # In case there is any error with new location or it is not valid, it
        # will be notified
        print(e)
        message = "💣 You need to introduce a valid location."
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )


def go(update, context):
    '''---------------------------------------------------
    * Name: go
    * Function: Shows the user a map to get from their
                current position to destination point
                chosen for the shortest path according to
                the concept of speed.
    * Parameters: update and context: objects that allow
                us to have more details of the user
                information and perform actions with the
                bot.
    * Return: A message and an image with the shortest
              path with ispeeds.
    ---------------------------------------------------'''
    try:
        # Print on the terminal a message indicating the user has
        # started a route with Igo
        print(update.effective_chat.first_name + " has started a route.")

        # Take the destination of the path sent by the user
        context.user_data['destination'] = update.message.text[4:] + ", Barcelona"

        # Send a message saying that the path will be shown
        message = "Let's go! 🚘 The fastest path to go from "
        message += str(context.user_data['location'])
        message += " to "
        message += str(context.user_data['destination'])
        message += " is:"
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
        # Send a message indicating that the procedure is taking place
        message2 = "...Calculating the fastest route... "
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message2
        )

        # Get 'intelligent path' between two addresses and plot it into a
        # PNG image
        context.user_data['path'] = igo.get_shortest_path_with_ispeeds(IGRAPH, context.user_data['location'], context.user_data['destination'])
        # Plot the path in the screen
        igo.plot_path(IGRAPH, context.user_data['path'], SIZE)
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open('path.png', 'rb'))
        os.remove('path.png')

    except Exception as e:
        # In case there is any error with the destination sent, it will be
        # notified
        print(e)
        message = "💣 Your destination is incorrect or your location is "
        message += "not valid."
        context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message
        )


############################################################
#                         MAIN
############################################################

# Declares a constant with the access token that reads from token.txt
TOKEN = open('token.txt').read().strip()

# Creates objects to work with Telegram
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Indicates when the bot receives one command that function is executed
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('author', author))
dispatcher.add_handler(MessageHandler(Filters.location, location))
dispatcher.add_handler(CommandHandler('pos', pos))
dispatcher.add_handler(CommandHandler('where', where))
dispatcher.add_handler(CommandHandler('go', go))

# Before starting the command go, check if the congestions are updated
if CommandHandler('go', go):
    # Takes the time when the command /go is sent
    current_time = datetime.datetime.now()
    # Compares if more than 5 minuts have passed since the last update
    if (current_time - START_TIME > datetime.timedelta(minutes=5)):
        # Downloads the current congestions
        congestions = igo.download_congestions(CONGESTIONS_URL)
        # Creates a new igraph
        IGRAPH = igo.build_igraph(graph, highways, congestions)
        # Last update time
        START_TIME = current_time

# Start the bot
updater.start_polling()
updater.idle()

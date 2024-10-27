# Basic ideas that will not change:
#       Consumes one or more rabbitmq exchanges dedicated to logging
#       Behaves as a simple pipeline between the rabbitmq feed and a .csv file

# Needs the following input for each logging instance:
#       1) the part number and serial number of the battery being logged
#       2) the requested filename
#       3) the name of the logging exchange for the battery (maybe?)



# A couple of ways to think about this:

# 1) A single object which is the master of ALL logging
#       - Singleton object
#       - Receives the go-ahead to monitor a given exchange from the flask interface (the log box is checked)
#       - Starts and manages a new thread
#       - Thread appends/creates .csv file with the CSV headers
#       - Thread begins consuming rabbitmq exchange for the battery it's told to with the file name provided
#       - If data is no longer being received, stops logging
#       - Resumes logging if data comes back on
#       - Receives the kill call from the flask interface (the log box is unchecked)
#       - Kills that specific thread


# 2) One instance of this object is created for every battery
#       - Part of the battery class
#       - Inherits from the threading.Thread class
#       - Battery receives the go ahead and kill commands from the flask interface
#       - Battery instantiates its own logging by starting this separate LogManager thread
#       - Thread appends/creates .csv file with the CSV headers
#       - Thread begins consuming rabbitmq exchange for the battery it's told to with the file name provided
#       - If data is no longer being received, stops logging
#       - Resumes logging if data comes back on
#       - Kills that specific thread when the kill command is received


# I'm not sure which one I like more...
# Is it the battery's responsibility to log its own data?
# Or should that data be delegated to a singleton LogManager who oversees all things log-related?
# I lean more towards the singleton option. That's what I'll try to do here. We'll see how complicated it is.


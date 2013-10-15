mumo-opcommand
==============

MuMo module - Temporarily add user or remove user to/from a group via GUI command line. 

The purpose of this module is to build a GUI command line interface into the mumble client where users in configurable groups (like admin) could grant a user temporary access to any group in a specific channel, or the root channel of the server. The concept is simular to that of issuing commands on IRC.

Features:
- Can allow any number of groups the ability to run each command
- The commands to add or remove access to the groups are customizable
- The message the server displays when adding or removing a user with the command is customizable
- Access can be either granted to the channel the command was executed in, or the root channel
- Access is temporary, which means it is removed once a user disconnects from the server
- Commands can be used to grant or remove access to a specific online user with '!command <user>', or the command initiator with just !command


Use cases:
- Using !op/!deop to grant temporary admin-like access to channels
- Using it as a !voice like command to add a user into a group used for command comms via whisper


This module should be considered beta for the moment, but is currently being actively used/tested. 

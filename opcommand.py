#!/usr/bin/env python
# -*- coding: utf-8
#//////////////////////////////////////////////////////////////////////////////
# opcommand.py - Temporarily add user or remove user to/from a group via command line. 
#
# Allows groups to add users to groups temporarily via command line. Similar
# to the /mode +o IRC command. Great for giving special temporary command rights.
#///////////////////////////////////////////////////////////////////////////////
## Copyright (C) 2013 Exploding Fist <expfist@custodela.com>
## Referenced code by Stefan Hacker <dd0t@users.sourceforge.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Neither the name of the Mumble Developers nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# `AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE FOUNDATION OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#-------------------------------------------------------- -----------------------
# Configuration management
#///////////////////////////////////////////////////////////////////////////////
#
# Module created by: Exploding Fist <expfist@custodela.com>
#
#///////////////////////////////////////////////////////////////////////////////
# Imports
from mumo_module import (commaSeperatedIntegers, commaSeperatedStrings,
                         MumoModule)
import re
#
#///////////////////////////////////////////////////////////////////////////////
# Module configuration
opcommand = {} # Module memory (dictionary)

class opcommand(MumoModule):
    default_config = {'opcommand':(
                                ('servers', commaSeperatedIntegers, []),
                                ),
                      lambda x: re.match('command_\d+', x):(
                                ('command', str, '!op'),
                                ('remCommand', str, '!deop'),
                                ('group', str, 'admin'),
                                ('root', int, 0),
                                ('addMessage', str, 'Adding user %s to group temporarily'),
                                ('removeMessage', str, 'Removing user %s from the group'),
                                ('acl', commaSeperatedStrings, []),
                                )
                    }

#
#///////////////////////////////////////////////////////////////////////////////
# Module Initialization

    def __init__(self, name, manager, configuration = None):
        MumoModule.__init__(self, name, manager, configuration)
        self.murmur = manager.getMurmurModule()
        
    def connected(self):
        manager = self.manager()
        log = self.log()
        log.debug("Register for Server callbacks")
        commands = 0
        servers = self.cfg().opcommand.servers
        if not servers:
            servers = manager.SERVERS_ALL
        manager.subscribeServerCallbacks(self, servers)
        while commands < 1000:
            # Get commnads to listen for
            try:
                commands = commands + 1
                comm = getattr(self.cfg(), 'command_%d' % commands)
                # Store config reference into memory
                setattr(opcommand, comm.command, 'command_%d' % commands)
                setattr(opcommand, comm.remCommand, 'command_%d' % commands)
                log.debug("Listening for command %s" % comm.command)
            except:
                commands = 1000
             
    def disconnected(self): pass
    
#
#///////////////////////////////////////////////////////////////////////////////
# Call back functions

    def userTextMessage(self, server, user, message, current=None):
        manager = self.manager()
        log = self.log()
        words = re.split(ur"[\u200b\s]+", message.text, flags=re.UNICODE)
        match = 0
        try:
            reference = getattr(opcommand, "%s" % words[0])
            match = 1
        except:
            match = 0
        # Load referenced configuration data
        op = getattr(self.cfg(), '%s' % reference)
        if match:
            giveOps = ''
            try:
                if words[1]:
                    giveOps = words[1]
            except:
                giveOps = user.name
            # Does user exist?
            getID = [giveOps]
            userID = server.getUserIds(getID)
            # Get caller ID too
            getID = [user.name]
            callerID = server.getUserIds(getID)
            if (userID[giveOps] < 1):
                log.debug("User %s failed a command for %s, as they do not exist.", user.name, giveOps)
                server.sendMessageChannel(user.channel, 0, 'User %s does not exist, or is not registered.' % giveOps)
            else:
                # Is the user connected?
                userlist = server.getUsers()
                #log.debug("Channel: %s", userlist)
                
                userOnline = 0
                targetSession = 0
                for users in userlist:
                    if (userlist[users].userid == userID[giveOps]):
                        targetSession = userlist[users].session
                        userOnline = 1
                if userOnline:
                    # Where do we apply the permission?
                    if op.root:
                        chan = 0
                    else:
                        chan = user.channel
                        
                    # Check if group exists
                    groupList = server.getACL(chan)
                    grp = {}
                    hasAccess = 0
                    for group in groupList[1]:
                        # Check if target group exists on target channel
                        if (group.name == op.group):
                            groupExists = 1
                            grp = group
                        # Check if caller has access to issue command
                        for acl in op.acl:
                            if (acl == group.name):
                                for members in group.members:
                                    if (members == callerID[user.name]):
                                        hasAccess = 1
                    if hasAccess:
                        if groupExists:                        
                            # Adding a user
                            if (op.command == words[0]):
                                log.info("User %s is adding user %s to group %s with command %s",  user.name, giveOps, op.group, words[0])
                                server.addUserToGroup(chan,targetSession,op.group)
                                try: 
                                    server.sendMessageChannel(user.channel, 0, op.addMessage % giveOps)
                                except:
                                    log.error("Message for command %s is invalid and does not contain the required variable character" % words[0])
                            # Removing a user
                            else:
                                log.info("User %s is removing user %s from group %s with command %s",  user.name, giveOps, op.group, words[0])
                                server.removeUserFromGroup(chan,targetSession,op.group)
                                try: 
                                    server.sendMessageChannel(user.channel, 0, op.removeMessage % giveOps)
                                except:
                                    log.error("Message for command %s is invalid and does not contain the required variable character" % words[0])
                            
                        else:
                            server.sendMessageChannel(user.channel, 0, 'Command failed because the group \'%s\' does not exist on this channel.' % op.group)
                            log.error("User %s attempted to add user %s to group %s with command %s, but it does not exist on channel %s",  user.name, giveOps, op.group, words[0], chan)
                    else:
                        log.info("User %s attempted to execute command %s on user %s, but does not have access", user.name, words[0], giveOps)
                        server.sendMessageChannel(user.channel, 0, 'You do not have permission to execute this command')
                else: 
                    server.sendMessageChannel(user.channel, 0, 'User %s is not online.' % giveOps)
                    log.debug("User %s is offline",  giveOps)
                

    
    def userStateChanged(self, server, state, context = None):pass      
    def userConnected(self, server, state, context = None):pass  
    def userDisconnected(self, server, state, context = None): pass
    def channelCreated(self, server, state, context = None): pass
    def channelRemoved(self, server, state, context = None): pass
    def channelStateChanged(self, server, state, context = None): pass
#
#///////////////////////////////////////////////////////////////////////////////

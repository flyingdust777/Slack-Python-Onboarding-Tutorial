# -*- coding: utf-8 -*-
"""
Python Slack Bot class for use with the pythOnBoarding app
"""
import os

from slackclient import SlackClient

# To remember which teams have authorized your app and what tokens are
# associated with each team, we can store this information in memory on
# as a global object. When your bot is out of development, it's best to
# save this in a more persistant memory store.
authed_teams = {}


class Bot(object):
    """ Instanciates a Bot object to handle Slack onboarding interactions."""
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "come_back_here"
        self.emoji = ":robot_face:"
        # When we instantiate a new bot object, we can access the app
        # credentials we set earlier in our local development environment.
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      # Scopes provide and limit permissions to what our app
                      # can access. It's important to use the most restricted
                      # scope that your app will need.
                      "scope": "users.profile:read"}
        self.oauth
        self.verification = os.environ.get("VERIFICATION_TOKEN")

        # NOTE: Python-slack requires a client connection to generate
        # an oauth token. We can connect to the client without authenticating
        # by passing an empty string as a token and then reinstantiating the
        # client with a valid OAuth token once we have one.
        self.client = SlackClient("")
        # We'll use this dictionary to store the state of each message object.
        # In a production envrionment you'll likely want to store this more
        # persistantly in  a database.
        self.messages = {}

    def auth(self, code):
        """
        Authenticate with OAuth and assign correct scopes.
        Save a dictionary of authed team information in memory on the bot
        object.

        Parameters
        ----------
        code : str
            temporary authorization code sent by Slack to be exchanged for an
            OAuth token

        """
        # After the user has authorized this app for use in their Slack team,
        # Slack returns a temporary authorization code that we'll exchange for
        # an OAuth token using the oauth.access endpoint
        auth_response = self.client.api_call(
                                "oauth.access",
                                client_id=self.oauth["client_id"],
                                client_secret=self.oauth["client_secret"],
                                code=code
                                )
        # To keep track of authorized teams and their associated OAuth tokens,
        # we will save the team ID and bot tokens to the global
        # authed_teams object
        team_id = auth_response["team_id"]
        authed_teams[team_id] = {"bot_token":
                                 auth_response["access_token"]}
        # Then we'll reconnect to the Slack Client with the correct team's
        # bot token
        self.client = SlackClient(authed_teams[team_id]["bot_token"])

    def bring_back_user(self, user_id, channel, token):
        """
        Create and send an onboarding welcome message to new users. Save the
        time stamp of this message on the message object for updating in the
        future.

        Parameters
        ----------
        team_id : str
            id of the Slack team associated with the incoming event
        user_id : str
            id of the Slack user associated with the incoming event

        """
        # We'll use the message object's method to create the attachments that
        # we'll want to add to our Slack message. This method will also save
        # the attachments on the message object which we're accessing in the
        # API call below through the message object's `attachments` attribute.
        text = "Hey... get back here <@" + str(user_id) + ">"
        self.client.api_call(
                             "chat.postMessage",
                             channel=channel,
                             token=token,
                             username=self.name,
                             icon_emoji=self.emoji,
                             text=text
        )
        self.client.api_call("channels.invite", token=token, channel=channel, user=user_id)

import cherrypy
from scripts.channel import Channel
from scripts.controller import Controller
from scripts.database import DatabaseController
from scripts.translator import Translator


class Chat(Controller):
    def __init__(self):
        self.channels = {'global': Channel('global', 'system', ['*'])}
        self.translator = Translator()
        self.db = DatabaseController()
        self.db.create_table('global')

    @cherrypy.expose(alias='create')
    @cherrypy.tools.json_out()
    def new_channel(self, **params):

        if 'channel' not in params:
            return self.error(message='No channel name given')
        elif 'white_list' not in params:
            return self.error(message='No white_list given')
        elif 'username' not in cherrypy.session:
            return self.error(message='You must be logged into to create channels')

        channel_name = params['channel']
        user = cherrypy.session['username']
        channel = Channel(channel_name, user, [params['white_list']])

        if channel_name in self.channels:
            return self.error(message='Channel name already exists')

        self.channels[channel_name] = channel
        self.db.create_table(channel_name)

        return self.ok()

    @cherrypy.expose(alias='delete')
    @cherrypy.tools.json_out()
    def delete_channel(self, **params):
        if 'channel' not in params:
            return self.error(message='no channel name provided')
        if 'username' not in cherrypy.session:
            return self.error(message='you must be logged in to delete channels')

        user = cherrypy.session['username']
        channel_name = params['channel']

        if channel_name not in self.channels:
            return self.error(message='channel does not exist')
        elif self.channels[channel_name].creator is not user:
            return self.error(message='only the channel creator can delete the channel')

        del self.channels[channel_name]
        return self.ok()

    @cherrypy.expose(alias='join')
    @cherrypy.tools.json_out()
    def join_channel(self, **params):

        if 'channel' not in params:
            return self.error(message='no channel name provided')
        if 'username' not in cherrypy.session:
            return self.error(message='you must be logged in to join channels')

        channel_name = params['channel']
        user = cherrypy.session['username']

        if channel_name not in self.channels:
            return self.error(message='Channel does not exist')
        elif user in self.channels[channel_name].user_log:
            return self.error(message='You are already in this channel')

        self.channels[channel_name].add_user(user)
        return self.ok()

    @cherrypy.expose(alias='leave')
    @cherrypy.tools.json_out()
    def leave_channel(self, **params):

        if 'channel' not in params:
            return self.error(message='no channel name provided')
        if 'username' not in cherrypy.session:
            return self.error(message='you must be logged in to join channels')

        channel_name = params['channel']
        user = cherrypy.session['username']

        if user not in self.channels[channel_name].user_log:
            return self.error(message='You are not in this channel')

        self.channels[channel_name].remove_user(user)
        return self.ok()

    @cherrypy.expose(alias='message')
    @cherrypy.tools.json_out()
    def new_message(self, **params):

        if 'channel' not in params:
            return self.error(message='no channel name provided')
        elif 'message' not in params:
            return self.error(message='no message provided')
        if 'username' not in cherrypy.session:
            return self.error(message='you must be logged in to send messages')

        user = cherrypy.session['username']
        channel_name = params['channel']
        message = params['message']

        if channel_name not in self.channels:
            return self.error(message='channel does not exist')

        self.channels[channel_name].add_message(
            text=message, author=user, channel=channel_name)
        return self.ok()

    @cherrypy.expose(alias='update')
    @cherrypy.tools.json_out()
    def get_updates(self, **params):
        if 'channel' not in params:
            return self.error(message='no channel name provided')
        elif 'language' not in params:
            return self.error(message='no target language provided')
        elif 'index' not in params:
            return self.error(message='no index provided')
        elif 'username' not in cherrypy.session:
            return self.error(message='you must be logged in to get messages')

        channel_name = params['channel']
        index = int(params['index'])
        target_language = params['language']

        if channel_name not in self.channels:
            return self.error(message='channel does not exist')

        data = self.channels[channel_name].get_messages(
            channel=channel_name, index=index)

        def translate_messages(data):
            for message in data:
                message['message'] = self.translator.translate_text(
                    message['message'], target_language)

        translate_messages(data)
        return self.ok(data=data)

    @cherrypy.expose(alias='list')
    @cherrypy.tools.json_out()
    def channel_list(self, **_params):
        if 'username' not in cherrypy.session:
            return self.error(message='you must be logged in to get channels')

        list = [channel for channel in self.channels
                if '*' in self.channels[channel].white_list or
                cherrypy.session['username'] in self.channels[channel].white_list]
        return self.ok(data=list)

    @cherrypy.expose(alias='whitelist')
    @cherrypy.tools.json_out()
    def channel_white_list(self, **params):
        if 'channel' not in params:
            return self.error(message='no channel name provided')

        return self.ok(data=self.channels[params['channel']].white_list)

    @cherrypy.expose(alias='add_to_whitelist')
    @cherrypy.tools.json_out()
    def add_to_whitelist(self, **params):

        if 'username' not in params:
            return self.error(message='no username provided')
        elif 'channel' not in params:
            return self.error(message='no channel name provided')
        elif 'username' not in cherrypy.session:
            return self.error(message='you must be logged in to edit white lists')

        chan = self.channels[params['channel']]
        if cherrypy.session['username'] not in chan.white_list:
            return self.error(message='you do not have permission to edit this whitelist')

        if params['username'] not in chan.white_list:
            chan.white_list.append(params['username'])
            return self.ok()
        else:
            return self.error(message='user is already in whitelist')

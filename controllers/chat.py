import cherrypy
from scripts.channel import Channel
from scripts.controller import Controller
from scripts.database import DatabaseController
from scripts.translator import Translator


class Chat(Controller):
    def __init__(self):
        self.channels = {'global': Channel('global', 'system')}
        self.translator = Translator()
        self.db = DatabaseController()
        self.db.create_table('global')

    @cherrypy.expose(alias='create')
    @cherrypy.tools.json_out()
    def new_channel(self, **params):
        if 'channel' not in params:
            return self.error(message='No channel name given')
        elif 'username' not in cherrypy.session:
            return self.error(message='You must be logged into to create channels')

        channel_name = params['channel']
        user = cherrypy.session['username']
        channel = Channel(channel_name, user)

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

        user = cherrypy.session['username']
        channel_name = params['channel']
        message = params['message']
        target_language = cherrypy.session['language']

        if channel_name not in self.channels:
            return self.error(message='channel does not exist')

        translated_message = self.translator.translate_text(
            message, target_language)

        self.channels[channel_name].add_message(
            text=translated_message, author=user, channel=channel_name)
        return self.ok()

    @cherrypy.expose(alias='update')
    @cherrypy.tools.json_out()
    def get_updates(self, **params):

        if 'channel' not in params:
            return self.error(message='no channel name provided')

        channel_name = params['channel']
        index = int(params['index'])

        if channel_name not in self.channels:
            return self.error(message='channel does not exist')

        data = self.channels[channel_name].get_messages(
            channel=channel_name, index=index)

        target_language = cherrypy.session['language']

        for message in data:
            message = list(message)
            message[1] = self.translator.translate_text(
                message[1], target_language)

        return self.ok(data=data)

    @cherrypy.expose(alias='language')
    @cherrypy.tools.json_out()
    def change_language(self, **params):
        if 'language' not in params:
            return self.error(message='no target language provided')

        cherrypy.session['language'] = params['language']
        return self.ok()

    @cherrypy.expose(alias='list')
    @cherrypy.tools.json_out()
    def channel_list(self, **_params):
        list = [channel for channel in self.channels]
        return self.ok(data=list)

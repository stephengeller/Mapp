import cherrypy
from unittest import TestCase
from controllers.session import Session
from controllers.chat import Chat, Channel


class TestSession(TestCase):

    username = 'test'
    session = None

    def setUp(self):
        cherrypy.session = {}
        self.session = Session()

    def tearDown(self):
        pass

    def test_login_with_no_username(self):
        response = self.session.login()
        self.assertEqual(response['code'], 1)
        self.assertEqual(response['message'], 'no username provided')
        self.assertFalse('username' in cherrypy.session)

    def test_login_when_already_logged_in(self):
        cherrypy.session['username'] = 'test'
        response = self.session.login(username=self.username)
        self.assertEqual(response['code'], 1)
        self.assertEqual(response['message'], 'already logged in')

    def test_valid_login(self):
        response = self.session.login(username=self.username)
        self.assertEqual(response['code'], 0)
        self.assertEqual(response['message'], '')

        self.assertEqual(cherrypy.session['username'], self.username)
        self.assertTrue(self.username in self.session.users)

    def test_logout(self):
        cherrypy.session['username'] = self.username
        self.session.users.append(self.username)
        self.session.logout()
        self.assertFalse(self.username in self.session.users)
        self.assertFalse('username' in cherrypy.session)

    def test_get_users(self):
        self.session.users.append(self.username)
        response = self.session.get_users()
        self.assertEqual(response['code'], 0)
        self.assertEqual(response['message'], '')
        self.assertEqual(response['data'], [self.username])

    def test_purge_user(self):
        cherrypy.tree.mount(Chat, '/chat')
        root = cherrypy.tree.apps['/chat'].root
        root.channels = {}
        root.channels['testChan'] = Channel('testChan', 'test', ['test'])
        root.channels['testChan'].user_log.append('test')
        self.session._purge_user('test')
        self.assertEqual(len(root.channels['testChan'].user_log), 0)
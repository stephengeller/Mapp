import cherrypy
from os import getcwd


class Server:

    def __init__(self, site_map):

        """
        Handles cherrypy.
        :param config: the site map. key = route, value = class
        """
        self.site_map = site_map
        self.tree = cherrypy.tree
        self.engine = cherrypy.engine

    def app_config(self):
        return {
            '/static': {
                "tools.staticdir.on": True,
                "tools.staticdir.dir": "%s/public" % getcwd()
            }
        }

    def build(self):

        """
        Build the routes from the config dictionary passed into constructor
        :return: no return value
        """
        for item in self.site_map:
            app = self.site_map[item]()
            self.tree.mount(app, item, self.app_config())

    def start(self):

        """
        start the cherrypy server
        :return: no return value
        """
        self.engine.start()
        self.engine.block()

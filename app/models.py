import datetime
import json

from flask import url_for

# temp hacks
initial = enumerate(json.loads(open('first.json').read()))
count = 0
# # # # # # #

class Post():
    """The unit of work a journalist produces."""

    def __init__(self, json_d):
        # because of dict.. #
        global count
        self.id = count
        count += 1
        # # # # # # # # # # #
        self.update(json_d)

    def update(self, json_d):
        self.title = json_d.get('title', None)
        self.created = datetime.datetime.now()
        self.body = json_d.get('body', None)

    def to_dict(self):
        clean = dict()
        clean["title"] = self.title
        clean["created"] = self.created.isoformat()
        clean["body"] = self.body
        clean["url"] = url_for('single_post', post_id=self.id, _external=True)
        return clean

    @staticmethod
    def api():
        """Returns a dict that describes the class to the api """
        url = url_for('all_posts', _external=True)
        return { "url": url }

datastore = { i: Post(x) for (i, x) in initial} # a dict of post objects

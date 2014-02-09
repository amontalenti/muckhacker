import datetime
import json

from flask import url_for

class PostEncoder(json.JSONEncoder):
    """Custom Json encoder for our post class, calls to_dict on obj"""
    def default(self, obj):
        if isinstance(obj, Post):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)

class Post():
    """The unit of work a journalist produces."""

    def __init__(self, json=False, bson=False):
        if json:
            self.update(json)
        elif bson:
            self.id = str(bson['_id']) 
            self.title = bson['title']
            self.created = bson['created']
            self.body = bson['body']
        else:
            print "How?"
            quit()

    def __repr__(self):
        return "<{}, {}, {}>".format(self._id, self.title, self.created)

    def __str__(self):
        return str(self.to_dict())

    def update(self, json_d):
        self.title = json_d.get('title', None)
        self.created = datetime.datetime.now()
        self.body = json_d.get('body', None)

    def to_dict(self):
        """Generates a dict that json.dumps turns into an external object"""
        clean = dict()
        clean["title"] = self.title
        clean["created"] = self.created.isoformat()
        clean["body"] = self.body
        clean["url"] = url_for('single_post', post_id=self.id, _external=True)
        return clean

    def to_bson(self):
        """The format we store our data in Mongo in."""
        to_store = dict(title=self.title, 
                        created=self.created,
                        body=self.body)
        return to_store

    @staticmethod
    def api():
        """Returns a dict that describes the class for the api """
        url = url_for('all_posts', _external=True)
        return { "url": url }

if __name__ == "__main__":
    from pymongo import MongoClient
    db = (MongoClient())['tarsands']
    initial = map(lambda d: Post(json=d), json.loads(open('first.json').read()))
    ret = db.posts.insert(map(lambda p: p.to_bson(), initial))
    print db.posts.find_one()['_id']

import datetime
import json

from flask import url_for
from werkzeug import check_password_hash, generate_password_hash

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
            raise ValueError("Need initialization values, dude")

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
        clean["url"] = url_for('api.single_post', post_id=self.id, _external=True)
        clean["id"] = self.id
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
        url = url_for('api.all_posts', _external=True)
        return { "url": url }

class User(): 
    """Login to admin side of MuckHacker
    NOTE: self.id must be set manually on object creation"""
    def __init__(self, username, hashed_pw, _id=None):
        """initialization comes from a bson dict"""
        self.username = username
        self.password = hashed_pw
        if _id is not None:
            self.id = str(_id)

    def to_bson(self):
        return dict(username=self.username, password=self.password)

    def set_password(self, password):
        self.password = generate_password_hash(password, 
                                # run 2000 iterations of sha1 in pkdf2
                                method='pbkdf2:sha1:2000')
        
    def check_password(self, password):
        challenge_pw = password.strip()
        return check_password_hash(self.password, challenge_pw)

    @classmethod
    def authenticate(cls, db, username, password):
        rdict = db.users.find_one({'username': username})
        if rdict is None:
            return None, False
        user = User(rdict['username'],
                    rdict['password'],
                    rdict['_id'])
        print user.password
        return user, user.check_password(password)

    #Flask user-auth handles
    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True # going off of reference...

    def __str__(self):
        return "<{self.id}, {self.username}, {self.password}>".format(self=self)


if __name__ == "__main__":
    from pymongo import MongoClient
    db = (MongoClient())['tarsands']
    db.posts.drop()
    db.users.drop()
    initial = map(lambda d: Post(json=d), json.loads(open('first.json').read()))
    ret = db.posts.insert(map(lambda p: p.to_bson(), initial))

    owner = User("nskelsey", "temp")
    owner.set_password("ninechars")
    db.users.insert(owner.to_bson())
    

    print ret
    print db.users.find_one()

    

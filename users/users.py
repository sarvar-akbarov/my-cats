import requests
import pickle
import re
import os.path
import os

class Users:

    # constuctor
    def __init__(self, *args):
        if len(args) > 1:
            for key, value in args.items():
                setattr(self, key, value)
        else:
            self.id = args[0]
            self.filename = 'users/user_datas/' + str(self.id) + '.txt'
            self.favourites = []
            # initialize other attributes
            self.write({})


    """working client side"""
    # status
    def joined(self):
        return os.path.isfile(self.filename)
    
    # read data
    def read(self):
        with open(self.filename, 'rb') as handle:
            data = handle.read()
        # reconstructing the data as dictionary
        d = pickle.loads(data)
        return d

    # get new user template
    def template(self, user):
        return {'id': user.id, 'name': user.first_name, 'favourites': []}

    # write data, if not exist create a new, otherwise update old data
    def write(self, data):
        if self.joined():
            old = self.read()
            old.update(data)
        else:
            old = data
        # serializing dictionary
        file = open(self.filename, "wb")
        pickle.dump(old, file)
        # closing the file
        file.close()
        for key, value in old.items():
            setattr(self, key, value)

 
 
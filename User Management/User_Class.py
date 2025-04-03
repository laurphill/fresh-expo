# A class to define the log-in capability and various functions a user can access
#Set up class for data storage table
class User:
    # Constructor
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

    #Mutators/Accessors
    @property
    def username(self):
        return self._username
    
    @username.setter
    def username(self, value):
        # Check username requirements
        expletives = ["bad_words"]
        if value in expletives:
            print("Error: Username cannot contain expletives")
        elif len(value) > 10:
            print("Error: Username cannot be more than 10 characters")
        elif False:
            pass
        else:
            self.username = value

    @property
    def password(self):
        return self._username
    
    @password.setter
    def password(self, value):
        # Check password requirements
        bad_passwords = ["1234", f"{self.username}"]
        if value in bad_passwords:
            print("Error: Password is weak. Please provide a password with ...")
        elif len(value) > 15:
            print("Error: Password cannot be more than 15 characters")
        elif False:
            pass
        else:
            self.password = value
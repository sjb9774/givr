import random

class Giveaway:

    def __init__(self, users):
        self.users = users

    def draw(self, n):
        choosable_users = self.users[:]
        chosen_users = []
        for x in range(n):
            chosen_one = choosable_users[random.randrange(0, len(choosable_users))]
            chosen_users.append(chosen_one)
            choosable_users.remove(chosen_one)
        return chosen_users

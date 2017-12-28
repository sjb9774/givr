from givr.logging import get_logger
import random

logger = get_logger(__name__)


class Giveaway:

    def __init__(self, users=None):
        self.users = users
        logger.debug("New Giveaway created")

    def draw(self, n):
        choosable_users = self.users[:]
        chosen_users = []
        for x in range(n):
            chosen_one = choosable_users[random.randrange(0, len(choosable_users))]
            chosen_users.append(chosen_one)
            choosable_users.remove(chosen_one)
        logger.info("Giveaway selected users {users}".format(users=str(chosen_users)))
        return chosen_users

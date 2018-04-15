"""This module creates objects needed to simulate collecting world cup stickers."""
from collections import defaultdict
import numpy as np
from itertools import combinations


class Person(object):
    """An individual collecting the sticker album.

    This module is only called by the Economy object defined below.
    
    Input:
        endowment, int: The number of stickers the person starts with
        n_stickers, int: The number of total stickers in the album
    """

    def __init__(self, endowment, n_stickers):

        self.album = set()
        self.repeats = defaultdict(int)
        self.is_finished = False
        self.money_spent = 0
        self.n_stickers = n_stickers
        self.buy_pack(stickers_per_pack=endowment)

    def finished(self):
        if len(self.album) == self.n_stickers:
            self.is_finished = True

    def update_collection(self, stickers_giving, stickers_receving):
        """Update album and repeat counts after trading.

        Add new stickers to album and remove traded ones from repeats
        dictionary. 
        """

        for sticker in stickers_receving:
            self.album.add(sticker)
        
        for sticker in stickers_giving:
            self.repeats[sticker] -= 1
        
        self.finished()
    
    
    def buy_pack(self, stickers_per_pack=5):
        """Add new cards in pack to either album or repeats."""

        self.money_spent += 1
        new_pack = np.random.choice(range(self.n_stickers), stickers_per_pack,
                                    replace=True)
        for sticker in new_pack:
            if sticker not in self.album:
                self.album.add(sticker)
            else:
                self.repeats[sticker] += 1
        
        self.finished()

class Economy(object):
    """Defines a trading economy of world cup stickers. 

    Input:
        n_friends, int: Number of people the simulation will track.
                        Simulation ends when all finish album.
        starting_endowment, int: Number of stickers each collector starts with.
        n_randos, int: Number of strangers each collector can 
                       trade with after trading with friends.
        stickers_per_pack, int: Number of stickers that come in each pack.
        n_stickers_in_album, int: Number of stickers in the album.
    """

    def __init__(self, n_friends, starting_endowment,
                 n_randos=5, stickers_per_pack=5,
                 n_stickers_in_album=682):
        self.n_friends = n_friends
        self.n_randos = n_randos
        self.stickers_per_pack = stickers_per_pack
        self.finishers = set()
        self.n_stickers = n_stickers_in_album
        self.create_people(n_friends, starting_endowment)
    
    def create_people(self, n_friends, endowment):
        """Initialize Person objects and add to dictionary."""
        members = {}
        for i in range(n_friends):
            members["id"+str(i)] = Person(endowment,
                                          n_stickers=self.n_stickers)
        self.members = members

    
    def trade(self, person1, person2):
        """Trade stickers between two people.

        Input:
            person1, Person: person object.
            person2, Person: person object.
        Output:
            tuple: if_traded - Boolean, person1, person2 updated after trading

        """
        person2_can_give = set(k for k in person2.repeats if person2.repeats[k] > 0)
        person1_can_give = set(k for k in person1.repeats if person1.repeats[k] > 0)
        person1_can_receive = person2_can_give.difference(person1.album)
        person2_can_receive = person1_can_give.difference(person2.album)

        if len(person1_can_receive) > 0 and len(person2_can_receive) > 0:
            person1.update_collection(person2_can_receive, person1_can_receive)
            person2.update_collection(person1_can_receive, person2_can_receive)
            return True, person1, person2
        else:
            return False, person1, person2
    
    def update_member(self, person_id, person):
        if person.is_finished:
            self.finishers.add(person)
        self.members[person_id] = person
    
    def round_of_trade(self, rando_endowment=500):
        """Carry out a round of trade.
        
        Input:
            rando_endowment: number of stickers each stranger
                             starts with.
        """
        have_traded = set()

        # Trade with friends.
        for id1, id2 in combinations(self.members, 2):
            person1 = self.members[id1]
            person2 = self.members[id2]
            if any([person1.is_finished, person2.is_finished]):
                continue
            they_traded, person1, person2 = self.trade(person1, person2)
            if they_traded:
                have_traded.add(id1)
                have_traded.add(id2)
                person1.finished()
                person2.finished()
                self.update_member(id1, person1)
                self.update_member(id2, person2)

        # Trade with randos.
        for person_id in self.members:
            person = self.members[person_id]
            if person.is_finished:
                continue
            for _ in range(self.n_randos):
                rando = Person(endowment=rando_endowment,
                               n_stickers=self.n_stickers)
                traded, person, _ = self.trade(person, rando)
                if traded:
                    have_traded.add(person_id)
                    person.finished()
                    self.update_member(person_id, person)

        # People who haven't traded buy a pack
        did_not_trade =  set(self.members).difference(have_traded)
        for person_id in did_not_trade:
            person = self.members[person_id]
            person.buy_pack(stickers_per_pack=self.stickers_per_pack)
            person.finished()
            self.update_member(person_id, person)

    def run_simulation(self, rando_endowment, n_logging):
        n_rounds = 0
        n_finished = sum(self.members[p].is_finished for p in self.members)
        while(n_finished < self.n_friends):
            if n_rounds % n_logging == 0:
                n_finishers = len(self.finishers)
                money_spent = sum(self.members[id].money_spent for id in self.members)
                print("Round {}: number of finishers is {}.\n".format(n_rounds, n_finishers))
                print("Round {}: total money spent is {}.".format(n_rounds, money_spent))
            self.round_of_trade(rando_endowment)
            n_finished = sum(self.members[p].is_finished for p in self.members)
            n_rounds += 1



    


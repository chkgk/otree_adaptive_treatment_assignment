from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)

import random

author = 'Christian König gen. Kersting'

doc = """
Adaptive weighted treatment assignment
"""


class Constants(BaseConstants):
    name_in_url = 'adaptive_assignment_demo'
    players_per_group = None
    num_rounds = 1

    treatment_names = ['A', 'B', 'C']  # define treatment names here, can be more than 2

    # adaptation strength
    # values smaller 1 decrease the weight given to the treatment with the fewest players
    # values larger 1 increase the weight given to the treatment with the fewest players
    # A value of 2 seems to work quite well
    # 
    # I suggest to run "otree test adaptive_assignment_demo 100" a couple of times with different values and
    # check the output. It prints player counts, adjusted player counts, and resulting weights for each new player.

    adaptation_strength = 2

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    treatment_name = models.StringField()
    completed_experiment = models.BooleanField(initial=False)

    def set_treatment(self):
        # we need two dictionaries to track how many participants are playing and how many have completed each treatment
        # both are initialized to zero
        treatment_counts = dict()
        for treatment_name in Constants.treatment_names:
            treatment_counts[treatment_name] = 0

        # count the number of participants per treatment that have a treatment assigned and are playing / have completed
        for player in self.subsession.get_players():
            if player.treatment_name:
                treatment_counts[player.treatment_name] += 1

        # we now find the numbers of players missing in each treatment for a uniform distribution
        max_players = max(treatment_counts.values())

        # for the first player to start the experiment, max_players is zero. Thus we simply randomize treatments
        if max_players == 0:
            self.treatment_name = random.choice(Constants.treatment_names)
            return  # and we return so the rest of the function is not executed

        # now we want to calculate weights for randomized treatment assignment
        # to gain control over how strongly the assignment reacts to the treatment with the lowest number of players
        # we artificially reduce the number of players in this treatment even further. The strength is controlled
        # by the constant "adaptation_strength"

        # find the treatment with the fewest participants
        treatment_with_fewest_participants = min(treatment_counts, key=treatment_counts.get)

        # artificially adjust the number even further down
        adjusted_treatment_counts = treatment_counts.copy()
        adjusted_treatment_counts[treatment_with_fewest_participants] *= 1 / Constants.adaptation_strength

        # now we calculate treatment randomization weights based on the adjusted treatment counts
        num_players = sum(treatment_counts.values())
        treatment_weights = dict()
        for treatment_name in Constants.treatment_names:
            treatment_weights[treatment_name] = 1 - (adjusted_treatment_counts[treatment_name] / num_players)

        # only print debug output when participant is a bot / test case
        if self.participant._is_bot:
            print('player counts:', treatment_counts, 'adjusted counts:', adjusted_treatment_counts, 'weights:', treatment_weights)

        self.treatment_name = random.choices(
            population=list(treatment_weights.keys()),
            weights=list(treatment_weights.values()),
            k=1
        )[0]
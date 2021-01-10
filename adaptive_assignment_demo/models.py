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
    weighted_assignment_threshold = 4  # weight until this threshold before starting weighted assignment of treatments


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    treatment = models.StringField()

    def completed_experiment(self):
        return self.participant._index_in_pages >= self.participant._max_page_index 

    def set_treatment(self):
        # fill a dictionary with the players by treatment
        treatment_players = {treatment_name: [] for treatment_name in Constants.treatment_names}
        for player in self.subsession.get_players():
            if player.treatment:
                treatment_players[player.treatment].append(player)

        # count playing and completed players by treatment
        playing, completed = dict(), dict()
        for name in Constants.treatment_names:
            completed[name] = len([player for player in treatment_players[name] if player.completed_experiment()])
            playing[name] = len([player for player in treatment_players[name] if not player.completed_experiment()])

        # until enough players completed the experiment, we randomize
        num_completed = sum(completed.values())
        if num_completed <= Constants.weighted_assignment_threshold:
            self.treatment = random.choice(Constants.treatment_names)
            return  # make sure to end execution of the function here

        # Now that more than the threshold has completed the experiment, it is time to adjust the weighting
        # Idea: Calculate the inverse distribution of the completed and use it as a weighting function
        # for the random treatment assignment.
        inverse_completed = dict()
        delta = 0.0001  # typically used to avoid division by zero
        for name in Constants.treatment_names:
            inverse_completed[name] = 1 / (completed[name] + delta)

        # normalize
        normalization_sum = sum(inverse_completed.values())
        for name in Constants.treatment_names:
            inverse_completed[name] /= normalization_sum

        # assign treatments based on the inverse of the distribution of players who have completed the experiment
        print('currently completed:', completed, 'resulting weights:', inverse_completed)
        self.treatment = random.choices(
            population=list(inverse_completed.keys()),
            weights=list(inverse_completed.values()),
            k=1
        )[0]

        # Note: There is a weakness to this method. Lets assume there are 3 treatments.
        # Initially, all treatments are equally likely to be assigned.
        # As soon as the first player completes the experiment, the weighting starts.
        # Lets assume the first player to finish is in treatment A.
        # Thus, the weights shift such that A, B, C are now assigned with probabilities [0, 0.5, 0.5].
        # These stay the same until the next player completes the experiment.
        # The problem is, that it takes time for players to reach the end of the experiment.
        # During the time it takes the next person to finish, we only assign treatments B and C in this example.
        # Then, suddenly, a wave of those B and C players arrive at the end of the experiment.
        #
        # Now, A will look under-sampled and the weights shift accordingly.
        # There are multiple ways to solve the issue:
        # A naive way is implemented here. We only start weighted assignment once a threshold is reached.
        #
        # A better way would be to also take the distribution of treatments among those players into account,
        # that are currently playing, but have not yet completed the experiment.
        # The problem then is, that you would have to track whether they are still "active" or
        # whether they have dropped out (could set a dropped-out flag if they ever miss a timeout).
        # It will also be difficult to "tune" the method to strike a good balance between achieving the goal
        # of an equal number of participants in each treatment (completed) and the aggressiveness of the weighting.

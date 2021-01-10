from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class GamePage1(Page):
    def vars_for_template(self):
        # this function is reliably called when the page is loaded
        # we use it to make sure the treatment is set when the participant arrives on the first page

        if not self.player.treatment:
            self.player.set_treatment()

        # return any variables for the template as usual. I leave it empty for now.
        return {}


class GamePage2(Page):
    pass


page_sequence = [GamePage1, GamePage2]

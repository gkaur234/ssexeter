from otree.api import *


doc = """
Implementation of contest games with selectable contest success function
"""


class C(BaseConstants):
    NAME_IN_URL = 'contest'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES

class SetupRound(WaitPage):
    pass

class Intro(Page):
    pass

class Decision(Page):
    pass

class WaitForDecision(WaitPage):
    pass

class Outcome(Page):
    pass

class Endblock(Page):
    pass



page_sequence = [
    SetupRound,
    Intro,
    Decision,
    WaitForDecision,
    Outcome,
    Endblock,
]

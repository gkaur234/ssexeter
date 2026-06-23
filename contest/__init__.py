from otree.api import *


doc = """
Implementation of contest games with selectable contest success function
"""


class C(BaseConstants):
    NAME_IN_URL = 'contest'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 3
    ENDOWMENT = Currency(10)
    COST_PER_TICKET = Currency(0.50)
    PRIZE = Currency(8)


class Subsession(BaseSubsession):
    is_paid = models.BooleanField()

    def setup_round(self):
        self.is_paid = self.round_number % 2 == 1 # paying the odd number round as we have already decided we will pay for the odd number rounds only without telling the participant
        for group in self.get_groups():
            group.setup_round()


class Group(BaseGroup):
    prize = models.CurrencyField()
    csf = models.StringField()

    def setup_round(self):
        self.prize = C.PRIZE
        self.csf = self.session.config["csf"]
        for player in self.get_players():
            player.setup_round()

    def determine_outcome_share(self):
        total = sum(player.tickets_purchased for player in self.get_players())
        for player in self.get_players():
            try:
                player.prize_won = player.tickets_purchased / total      # what would happen if nobody purchased any tickets ~0
            except ZeroDivisionError:
                player.prize_won = 1 / len(self.get_players())
            player.earnings = ((
                player.endowment -
                player.tickets_purchased * player.cost_per_ticket) +
                self.prize * player.prize_won
            )
            if self.subsession.is_paid: # if this round is being paid, this round's earning must be added to the total earning
                player.payoff = player.earnings

    def determine_outcome_allpay(self):
        for player in self.get_players():
            if player.tickets_purchased > player.coplayer.tickets_purchased:
                player.prize_won = 1
            elif player.tickets_purchased < player.coplayer.tickets_purchased:
                player.prize_won = 0
            else:
                player.prize_won = 0.5
            player.earnings = ((
                player.endowment -
                player.tickets_purchased * player.cost_per_ticket) +
                self.prize * player.prize_won
            )
            if self.subsession.is_paid:  # if this round is being paid, this round's earning must be added to the total earning
                player.payoff = player.earnings


    def determine_outcome(self):
        if self.csf == "share":
            self.determine_outcome_share()
        elif self.csf == "allpay":
            self.determine_outcome_allpay()



class Player(BasePlayer):
    endowment = models.CurrencyField()
    cost_per_ticket = models.CurrencyField()
    tickets_purchased = models.IntegerField()
    prize_won = models.FloatField()
    earnings = models.CurrencyField()

    def setup_round(self): # this is a function you can call w a specific play
        self.endowment = self.session.config.get("contest_endowment", C.ENDOWMENT)
        self.cost_per_ticket = C.COST_PER_TICKET

    @property
    def coplayer(self):
        return self.group.get_player_by_id(3 - self.id_in_group)

    @property
    def max_tickets_affordable(self):
        return int(self.endowment / self.cost_per_ticket) # dividing currency by currency gives a
                                                          # currency recognized by otree






# PAGES

class SetupRound(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession):
        subsession.setup_round()

class Intro(Page):
    pass

class Decision(Page):
    form_model = "player"
    form_fields = ["tickets_purchased"]

    @staticmethod
    def error_message(player, values):
        if values["tickets_purchased"] < 0:
            return "You must buy a positive number of tickets"

        if values ["tickets_purchased"] > player.max_tickets_affordable:
            return(
                f"Buying {values["tickets_purchased"]} tickets would cost "
                f"{values['tickets_purchased'] * player.cost_per_ticket} "
                f"which is more than your endowment of {player.endowment}."
            )

        return None


class WaitForDecision(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession):
        for group in subsession.get_groups():
            group.determine_outcome()

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

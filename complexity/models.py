from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from .fields import LotteryField
import random

author = 'Philipp Chapkovski'

doc = """
R.Duch, D. Landa project on complexity
"""


class Constants(BaseConstants):
    name_in_url = 'complexity'
    players_per_group = 2
    assert players_per_group == 2, 'Number of players should be 2 for correct role assignemnt'
    num_rounds = 10
    num_first_part = 5
    assert num_first_part < num_rounds, 'First set of decisions should be less then total number of rounds'
    pweights = [99, 5]
    prob = pweights[0] / sum(pweights)  # probability of success if P1 invests
    p1endowment = 300
    lotterycost = 150
    retention_prize = 900
    guess_prize = 140
    success_prize = 280


class Subsession(BaseSubsession):
    def creating_session(self):
        self.group_randomly(fixed_id_in_group=True)


LOTTERYOUTCOMES = ((True, 'Success'), (False, 'Failure'),)
RETAININGCHOICES = (
    (0, 'NEVER Retain Player 1'),
    (1, 'Retain Player 1 if Success on BOTH Tasks'),
    (2, 'Retain Player 1 if Success on Task 1, OR on Task 2, OR on BOTH Task 1 AND Task 2'),
    (3, 'Retain Player 1 if Success on Task 1'),
    (4, 'Retain Player 1 if Success on Task 2'),
    (5, 'ALWAYS Retain Player 1'),
)


class Group(BaseGroup):
    task1decision = LotteryField(doc='lottery decision of P1 - task 1',
                                 verbose_name="""
                                 Do you want to pay the cost on Task 1 — the cost 
                                 is 150 ECUs and the chance of Success is 5 out of 10"""
                                 )
    task2decision = LotteryField(doc='lottery decision of P1 - task 2',
                                 verbose_name="""
                                         Do you want to pay the cost on Task 2 — the cost 
                                         is 150 ECUs and the chance of Success is 5 out of 10"""
                                 )
    # in outcome we use choices just for get_foo_display method later on
    task1outcome = models.BooleanField(doc=' outcome of task 1',
                                       choices=LOTTERYOUTCOMES)
    task2outcome = models.BooleanField(doc='outcome of task 2',
                                       choices=LOTTERYOUTCOMES)
    task1guess = LotteryField(doc='P2 guess of lottery decision of P1 - task 1',
                              verbose_name='Player 1 will pay the cost on Task 1'
                              )
    task2guess = LotteryField(doc='P2 guess of lottery decision of P1 - task 2',
                              verbose_name='Player 1 will pay the cost on Task 2'
                              )
    retaining = models.IntegerField(doc='retaining/firing decision of P2 regarding P1',
                                    choices=RETAININGCHOICES,
                                    verbose_name='Choose a decision rule for Retaining or Firing Player 1',
                                    widget=widgets.RadioSelect)

    def get_retention_decision(self):
        return {
            0: False,
            1: self.task1outcome + self.task2outcome == 2,
            2: self.task1outcome + self.task2outcome >= 1,
            3: self.task1outcome,
            4: self.task2outcome,
            5: True,
        }[self.retaining]

    def set_outcome(self):
        self.task1outcome = self.task1decision * random.choices(LOTTERYOUTCOMES, weights=Constants.pweights)[0][0]
        self.task2outcome = self.task2decision * random.choices(LOTTERYOUTCOMES, weights=Constants.pweights)[0][0]

    def get_sum_guess_prize(self):
        return ((self.task1decision == self.task1guess) + (
            self.task2decision == self.task2guess) * Constants.guess_prize)

    def set_payoff(self):
        self.set_outcome()
        P1 = self.get_player_by_role('P1')
        P2 = self.get_player_by_role('P2')
        sum_success = (self.task1outcome + self.task2outcome) * Constants.success_prize
        sum_guess = self.get_sum_guess_prize()
        P2.payoff = sum_success + sum_guess
        P1.payoff = (Constants.p1endowment - (self.task1decision + self.task2decision) * Constants.lotterycost +
                     self.get_retention_decision() * Constants.retention_prize)

class Player(BasePlayer):
    """we defining role simply as: at the first part of the study odd players are P1s, and at the
    second half: even players become P1s"""

    def role(self):
        if bool(self.round_number <= Constants.num_first_part) ^ bool(self.id_in_group % 2 == 0):
            return "P1"
        else:
            return "P2"

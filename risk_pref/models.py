from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from django.db import models as djmodels
import random

author = 'Philipp Chapkovski'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'risk_pref'
    players_per_group = None
    num_rounds = 1
    risk_choices_A = (1, .8)
    risk_choices_B = (1.95, .05)
    min_perc = 10
    max_perc = 101
    step = 10
    lotteries = list(range(min_perc, max_perc, step))
    probs = [.1, .9]


class Subsession(BaseSubsession):
    def creating_session(self):
        for p in self.get_players():
            p.selected_lottery = random.choice(Constants.lotteries)
            for i in Constants.lotteries:
                p.risks.create(left_col=i, right_col=Constants.max_perc - i - 1)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    dump_risk = models.StringField(doc='to store the list of risk decisions')
    rand = models.FloatField(doc='random defining which of two options in a chosen lottery will work')
    selected_lottery = models.IntegerField(doc='which specific lottery is chosen for payment')
    def get_decision_as_dict(self):
        lottery = self.risks.get(left_col=self.selected_lottery, )
        if lottery.answer:
            choice = 'B'
        else:
            choice = 'A'
        lottery_num = Constants.lotteries.index(self.selected_lottery)
        return {'answer':choice,
                'selected_lot': lottery_num}
    def set_payoff(self):
        lottery = self.risks.get(left_col=self.selected_lottery, )
        self.rand = random.random()
        if self.rand * 100 < lottery.left_col:
            if lottery.answer:
                payoff = Constants.risk_choices_B[0]
            else:
                payoff = Constants.risk_choices_A[0]
        else:
            if lottery.answer:
                payoff = Constants.risk_choices_B[1]
            else:
                payoff = Constants.risk_choices_A[1]
        # the following is NOT the safest way of doing it, but works for now (insturctions should be
        # rewritten in ECUs
        self.payoff = payoff / self.session.config['real_world_currency_per_point']


class Risk(djmodels.Model):
    player = models.ForeignKey(Player, related_name="risks")
    left_col = models.IntegerField()
    right_col = models.IntegerField()
    answer = models.BooleanField(null=True,
                                 doc='False - option A, True - option B',
                                 widget=widgets.RadioSelectHorizontal)

    def __str__(self):
        answer_to_str = None
        if self.answer == True:
            answer_to_str = 'Option B'
        elif self.answer == False:
            answer_to_str = 'Option A'
        return 'choosing between option A({}) and B({}) with the probs {}/{} {} was chosen'.format(
            Constants.risk_choices_A, Constants.risk_choices_B, self.left_col, self.right_col, answer_to_str,
        )

from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from .fields import LotteryField
import random

author = 'Philipp Chapkovski'

doc = """
R.Duch, D. Landa project on die_game
"""


def get_practice_rounds(num_practice, num_first_part):
    first_set = list(range(1, num_practice + 1))
    second_set = list(range(num_first_part + 1, num_first_part + num_practice + 1))
    return first_set + second_set


def get_last_n_rounds(n, num_first_part, num_rounds):
    first_set = list(range(num_first_part - n + 1, num_first_part + 1))
    second_set = list(range(num_rounds - n + 1, num_rounds + 1))
    return first_set + second_set


class Constants(BaseConstants):
    name_in_url = 'complexity'
    players_per_group = 2
    assert players_per_group == 2, 'Number of players should be 2 for correct role assignemnt'
    num_rounds = 20
    num_first_part = 10
    num_second_part = num_rounds - num_first_part
    # how many practice rounds we have
    num_practice = 0
    # when the second decision (guess) about p1 decision is shwon
    num_second_dec = 3
    assert num_first_part < num_rounds, 'First set of decisions should be less then total number of rounds'
    assert num_practice < num_first_part and num_practice < num_second_part, 'training rounds number should be ' \
                                                                             'strictly less than total number of rounds'
    assert num_first_part - num_practice >= num_second_dec and num_second_part - num_practice >= num_second_dec
    practice_rounds = get_practice_rounds(num_practice, num_first_part)
    p2_second_decision_rounds = get_last_n_rounds(num_second_dec, num_first_part, num_rounds)
    pweights = [5, 5]
    tot_prop = sum(pweights)
    prob = round(pweights[0] / sum(pweights), 2)  # probability of success if P1 invests
    p1endowment = 300
    lotterycost = 150
    retention_prize = 900
    guess_prize = 140
    success_prize = 500
    roles_dict = {
        'P1': 'Player 1',
        'P2': 'Player 2',
    }
    RETAININGCHOICES = (
        (0, 'NEVER Reward Player 1'),
        (1, 'Reward Player 1 if Success on BOTH Tasks'),
        (2, 'Reward Player 1 if Success on Task 1, OR on Task 2, OR on BOTH Task 1 AND Task 2'),
        (3, 'Reward if Success on a single Task (Task 1 or Task 2)'),
        (4, 'ALWAYS Reward Player 1'),
    )


class Subsession(BaseSubsession):
    def creating_session(self):
        self.group_randomly(fixed_id_in_group=True)
        if self.round_number == 1:
            for p in self.session.get_participants():
                pround1 = random.randint(1, Constants.num_first_part)
                pround2 = random.randint(Constants.num_first_part + 1, Constants.num_rounds)
                p.vars['paying_rounds'] = [pround1, pround2]


LOTTERYOUTCOMES = ((True, 'Success'), (False, 'Failure'),)

P1DecisionSTRING = """
Do you want to pay the cost on Task {task}? The cost is {lotterycost}. 
If you paid, the changes of success on that task is {success_p} out of {totp}.
 If you don’t, the outcome will be failure"""


def get_decision_string(task):
    return P1DecisionSTRING.format(
        lotterycost=c(Constants.lotterycost),
        success_p=Constants.pweights[0],
        totp=sum(Constants.pweights),
        task=task
    )


class Group(BaseGroup):
    task1decision = LotteryField(doc='lottery decision of P1 - task 1',
                                 verbose_name=get_decision_string(1),
                                 )
    task2decision = LotteryField(doc='lottery decision of P1 - task 2',
                                 verbose_name=get_decision_string(2),
                                 )
    # in outcome we use choices just for get_foo_display method later on
    task1outcome = models.BooleanField(doc=' outcome of task 1',
                                       choices=LOTTERYOUTCOMES)
    task2outcome = models.BooleanField(doc='outcome of task 2',
                                       choices=LOTTERYOUTCOMES)
    task1guess = LotteryField(doc='P2 guess of lottery decision of P1 - task 1',
                              verbose_name='Player 1 will pay the cost on Task 1',
                              third_person=True,
                              )
    task2guess = LotteryField(doc='P2 guess of lottery decision of P1 - task 2',
                              verbose_name='Player 1 will pay the cost on Task 2',
                              third_person=True,

                              )
    retaining = models.IntegerField(doc='retaining/firing decision of P2 regarding P1',
                                    choices=Constants.RETAININGCHOICES,
                                    verbose_name='Choose a decision rule for Rewaring or No Rewarding of Player 1',
                                    widget=widgets.RadioSelect)

    def get_retention_decision(self):
        return {
            0: False,
            1: self.task1outcome + self.task2outcome == 2,
            2: self.task1outcome + self.task2outcome >= 1,
            3: self.task1outcome + self.task2outcome == 1,
            4: True,
        }[self.retaining]

    def set_outcome(self):
        self.task1outcome = self.task1decision * random.choices(LOTTERYOUTCOMES, weights=Constants.pweights)[0][0]
        self.task2outcome = self.task2decision * random.choices(LOTTERYOUTCOMES, weights=Constants.pweights)[0][0]

    def get_sum_guess_prize(self):
        return ((self.task1decision == self.task1guess) + (
            self.task2decision == self.task2guess)) * Constants.guess_prize

    def set_payoff(self):
        self.set_outcome()
        P1 = self.get_player_by_role('P1')
        P2 = self.get_player_by_role('P2')
        sum_success = (self.task1outcome + self.task2outcome) * Constants.success_prize
        sum_guess = self.get_sum_guess_prize()
        P2.payoff = sum_success + sum_guess
        P1.payoff = (Constants.p1endowment - (self.task1decision + self.task2decision) * Constants.lotterycost +
                     self.get_retention_decision() * Constants.retention_prize)

    def set_final_payoff(self):
        assert self.round_number == Constants.num_rounds, 'You should not call this method before the final round'
        for p in self.get_players():
            paying_rounds = p.participant.vars['paying_rounds']
            for r in p.in_all_rounds():
                r.temp_payoff = r.payoff
                if r.round_number not in paying_rounds:
                    r.payoff = 0





class Player(BasePlayer):
    """we defining role simply as: at the first part of the study odd players are P1s, and at the
    second half: even players become P1s"""
    temp_payoff = models.CurrencyField(doc='to store all interim payoffs')

    def role(self):
        roles = list(Constants.roles_dict.keys())
        if bool(self.round_number <= Constants.num_first_part) ^ bool(self.id_in_group % 2 == 0):
            return roles[0]
        else:
            return roles[1]

    def get_role_name(self):
        return Constants.roles_dict[self.role()]

    def get_another_role(self):
        roles = list(Constants.roles_dict.keys())
        another_role = list((set(roles) - set([self.role()])))[0]
        return Constants.roles_dict[another_role]

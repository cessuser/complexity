from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)


author = 'Philipp Chapkovski'

doc = """
R.Duch, D. Landa project on die_game
"""


class Constants(BaseConstants):
    name_in_url = 'risk_pref'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass

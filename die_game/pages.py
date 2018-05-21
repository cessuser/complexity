from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from otree.forms.widgets import _CurrencyInput

class Instructions(Page):
    def vars_for_template(self):
        return {'curname':_CurrencyInput.CURRENCY_SYMBOL}


class DiceRolling(Page):
    form_model = 'player'
    form_fields = ['dice']

    def before_next_page(self):
        self.player.set_payoff()


class DiceRollingResults(Page):
    ...



page_sequence = [
    Instructions,
    DiceRolling,
    DiceRollingResults,

]

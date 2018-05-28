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

class FinalResults(Page):
    def vars_for_template(self):
        print(self.participant.vars[self.player.session_id]['part2_payoff'])
        return {
            'modules1_chosen_round': self.participant.vars[self.player.session_id]['part1_chosenRounds'][0],
            'modules2_chosen_round': self.participant.vars[self.player.session_id]['part1_chosenRounds'][1],
            'modules1_payoff': self.participant.vars[self.player.session_id]['part1_payoff'][0],
            'modules2_payoff': self.participant.vars[self.player.session_id]['part1_payoff'][1],
            'modules3_payoff': self.participant.vars[self.player.session_id]['part2_payoff'],
            'modules4_payoff': self.participant.vars[self.player.session_id]['part3_payoff'],
            'total_payoff': self.participant.vars[self.player.session_id]['part1_payoff'][0] +
                            self.participant.vars[self.player.session_id]['part1_payoff'][1] +
                            self.participant.vars[self.player.session_id]['part2_payoff'] +
                            self.participant.vars[self.player.session_id]['part3_payoff']
        }


class DiceRollingResults(Page):
    ...



page_sequence = [
    Instructions,
    DiceRolling,
    DiceRollingResults,
    FinalResults
]

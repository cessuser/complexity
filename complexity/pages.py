from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class CustomPage(Page):
    role = None
    first_page = None
    form_model = 'group'

    def is_displayed(self):
        if self.role is None:
            self.role = self.player.role()
        if self.first_page is None:
            self.first_page = self.round_number

        return self.first_page == self.round_number and self.player.role() == self.role


class P1Page(CustomPage):
    role = 'P1'


class P2Page(CustomPage):
    role = 'P2'


class Intro(CustomPage):
    first_page = True


class Intro2(CustomPage):
    first_page = True


class P1Instructions(P1Page):
    first_page = True


class P1Example(P1Page):
    first_page = True


class P2Instructions(P2Page):
    first_page = True


class P2Example(P2Page):
    first_page = True


class SwitchRoles(CustomPage):
    def is_displayed(self):
        # we show the swtich role page only as the first page  between role switching
        return self.round_number == Constants.num_first_part + 1


class P1Decision(P1Page):
    form_fields = ['task1decision', 'task2decision']


class P2FirstDecision(P2Page):
    form_fields = ['retaining']


class P2SecondDecision(P2Page):
    form_fields = ['task1guess', 'task2guess']


class BeforeOutcomeWP(WaitPage):
    def after_all_players_arrive(self):
        self.group.set_payoff()


class Outcome(CustomPage):
    def vars_for_template(self):
        retention_gain = self.group.get_retention_decision() * Constants.retention_prize
        task1cost = - Constants.lotterycost * self.group.task1decision
        task2cost = - Constants.lotterycost * self.group.task2decision
        sum_task_success_gain = (self.group.task1outcome + self.group.task2outcome) * Constants.success_prize
        sum_guess_gain = self.group.get_sum_guess_prize()
        return {
            'retention_gain': retention_gain,
            'task1cost': task1cost,
            'task2cost': task2cost,
            'sum_task_success_gain': sum_task_success_gain,
            'sum_guess_gain': sum_guess_gain,
        }


class FinalResults(CustomPage):
    def is_displayed(self):
        return super().is_displayed() and self.round_number == Constants.num_rounds


page_sequence = [
    # SwitchRoles,
    # Intro,
    # Intro2,
    # P1Instructions,
    # P1Example,
    # P2Instructions,
    # P2Example,
    P1Decision,
    P2FirstDecision,
    P2SecondDecision,
    BeforeOutcomeWP,
    Outcome,
    # FinalResults
]

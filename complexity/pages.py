from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


def vars_for_all_templates(self):
    return {'role1': Constants.roles_dict['P1'],
            'role2': Constants.roles_dict['P2'], }


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
    def is_displayed(self):
        # we show the swtich role page only as the first page  between role switching
        return super().is_displayed() and (self.round_number == Constants.num_first_part + 1 or self.round_number == 1)


class P1Example(P1Page):
    first_page = True


class P2Instructions(P2Page):
    def is_displayed(self):
        # we show the swtich role page only as the first page  between role switching
        return super().is_displayed() and (self.round_number == Constants.num_first_part + 1 or self.round_number == 1)


class P2Example(P2Page):
    first_page = True


class SwitchRoles(CustomPage):
    def is_displayed(self):
        # we show the swtich role page only as the first page  between role switching
        return self.round_number == Constants.num_first_part + 1

    def vars_for_template(self):
        chosen_round = self.participant.vars['paying_rounds'][0]
        return {'chosen_payoff': self.player.in_round(chosen_round).payoff}


class P1Decision(P1Page):
    form_fields = ['task1decision', 'task2decision']


class P2FirstDecision(P2Page):
    form_fields = ['retaining']


class P2SecondDecision(P2Page):
    def is_displayed(self):
        print('AAAA',self.round_number)
        print('BBBB', Constants.p2_second_decision_rounds)
        return super().is_displayed() and self.round_number in Constants.p2_second_decision_rounds

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
    def before_next_page(self):
        if self.round_number==Constants.num_rounds:
            self.group.set_final_payoff()


class FinalResults(CustomPage):
    def is_displayed(self):
        return super().is_displayed() and self.round_number == Constants.num_rounds

    def vars_for_template(self):
        chosen_round1 = self.participant.vars['paying_rounds'][0]
        chosen_round2 = self.participant.vars['paying_rounds'][1]
        return {
            'chosen_round1': chosen_round1,
            'chosen_round2': chosen_round2,
            'first_pay': self.player.in_round(chosen_round1).payoff,
            'second_pay': self.player.in_round(chosen_round2).payoff,
            # 'paying_round2': chosen_round - Constants.num_first_part,
        }


page_sequence = [
    SwitchRoles,
    Intro,
    Intro2,
    P1Instructions,
    # P1Example,
    P2Instructions,
    # P2Example,
    P2FirstDecision,
    WaitPage,
    P1Decision,

    P2SecondDecision,
    BeforeOutcomeWP,
    Outcome,
    FinalResults
]

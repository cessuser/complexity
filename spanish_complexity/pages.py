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
        print('AAAA', self.round_number)
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
        if self.round_number == Constants.num_rounds:
            self.group.set_final_payoff()


class ShuffleWaitPage(WaitPage):
    wait_for_all_groups = True
    def after_all_players_arrive(self):
        self.subsession.do_shuffle()


class FinalResults(CustomPage):
    def is_displayed(self):
        return super().is_displayed() and self.round_number == Constants.num_rounds

    def vars_for_template(self):
        chosen_round1 = self.participant.vars['paying_rounds'][0]
        chosen_round2 = self.participant.vars['paying_rounds'][1]
        firstPay = self.player.in_round(chosen_round1).payoff / 1.0
        secondPay = self.player.in_round(chosen_round2).payoff / 1.0
        self.participant.vars[self.player.session_id] = {
            'part1_chosenRounds':[chosen_round1, chosen_round2],
            'part1_payoff': [firstPay, secondPay],
        }
        return {
            'chosen_round1': chosen_round1,
            'chosen_round2': chosen_round2,
            'first_pay': firstPay,
            'second_pay': secondPay,
            # 'paying_round2': chosen_round - Constants.num_first_part,
        }

class Quiz(CustomPage):
    def is_displayed(self):
        return super().is_displayed() and self.round_number == 1

    def vars_for_template(self):
        questions = [
            {
                'id': 'question_1',
                'content': '1. Suponga que el Jugador 1 elige pagar el costo en la Tarea 1 pero no hacerlo en la Tarea 2',
                'choices': [],
                'answer': '',
                'desc': ''
            },
            {
                'id': 'question_1.a',
                'content': '    a. ¿Cuál es la probabilidad de que el resultado en al menos una de las tareas sea Fracaso?',
                'choices': [
                    'i. 5 de 10',
                    'ii. 0 de 10',
                    'iii. 10 de 10',
                    'iv. Ninguna de las anteriores'
                ],
                'answer': 'iii',
                'desc': 'La respuesta correcta es iii (10 de 10) ya que no pagar el costo en la Tarea 2 garantiza que la Tarea 2 será un Fracaso.'
            },
            {
                'id': 'question_1.b',
                'content': '    b. ¿Cuál es la probabilidad de que el resultado de al menos una de las Tareas sea Exitoso?',
                'choices': [
                    'i. 5 de 10',
                    'ii. 0 de 10',
                    'iii. 10 de 10',
                    'iv. Ninguna de las anteriores'
                ],
                'answer': 'i',
                'desc': 'La respuesta correcta es i (5 de 10), ya que no pagar el costo de la Tarea 2 garantiza el Fracaso en la tarea 2, solo podría ser Exisosa la Tarea 1 y eso tiene una probabilidad de 5 de 10 de suceder.'
            },
            {
                'id': 'question_1.c',
                'content': '    c. Suponga que el Jugador 2 ha establecido una regla según la que el Jugador 1 será recompensado si sólo si, el resultado de Ambas Tareas es Exitoso. ¿Cuál es la probabilidad de que el jugador 1 sea recompensado?',
                'choices': [
                    'i. 5 de 10',
                    'ii. 0 de 10',
                    'iii. 10 de 10',
                    'iv. Ninguna de las anteriores'
                ],
                'answer': 'ii',
                'desc': 'La respuesta correcta es ii (0 de 10), porque no pagar el costo en la Tarea 2, garantiza que el resultado de esa tarea sea un Fracaso.'
            },
            {
                'id': 'question_1.d',
                'content': '    d. Suponga que el Jugador 2 ahora ha establecido una regla en la que el Jugador 1 será recompensado si sólo si, el resultado es Exitoso en al menos una Tarea. ¿Cuál es la probabilidad de que el Jugador sea recompensado ahora?',
                'choices': [
                    'i. 5 de 10',
                    'ii. 0 de 10',
                    'iii. 10 de 10',
                    'iv. Ninguna de las anteriores'
                ],
                'answer': 'i',
                'desc': 'La respuesta correcta es i (5 de 10), ya que no pagar el costo en la Tarea 2 garantiza un Fracaso en la Tarea 2. Sólo la tarea 1 puede ser exitosa y eso será con una probabilidad de 5 de 10.'
            },
            {
                'id': 'question_2',
                'content': '2. Suponga que la regla del jugador 2 es recompensar al Jugador 1 si y sólo si, el resultado de Ambas, Tarea 1 y Tarea 2, es Exitoso.',
                'choices': [],
                'answer': '',
                'desc': ''
            },
            {
                'id': 'question_2.a',
                'content' : '   a. ¿Cuál es el máximo pago que el Jugador 1 puede recibir?',
                'choices': [
                    'i. 600 ECU',
                    'ii. 750 ECU',
                    'iii. 900 ECU',
                    'iv. 1200 ECU'
                ],
                'answer': 'iii',
                'desc': 'La respuesta correcta es iii (900 ECU). Dado que no pagar el costo en una determinada tarea garantiza que la tarea sea un Fracaso, para obtener recompensa, Según la regla anunciada, el Jugador 1 debe pagar el costo en Ambas Tareas. Si es que obtiene una recompensa, el pago sería de 300 ECU (Inicial) - 150 ECU (por la primera tarea) – 150 ECU (por la segunda tarea) + 900 ECU (recompensa)=900 ECU'
            },
            {
                'id': 'question_2.b',
                'content': '   b. ¿Cuál sería el mínimo pago que el Jugador 1 podría recibir?',
                'choices': [
                    'i. 900 ECU',
                    'ii. 200 ECU',
                    'iii. 750 ECU',
                    'iv. 0 ECU'
                ],
                'answer': 'iv',
                'desc': 'La respuesta correcta es iv (0 ECU). Este sería el pago si el jugador 1 decide pagar el costo en Ambas tareas, pero el resultado en una o ambas es Fracaso. En ese caso, el Jugador no recibiría recompense. Sus pagos entonces, serían 300 ECU (Inicial) – 150 ECU (por la primera tarea) – 150 ECU (por la segunda tarea) + 0 ECU (Sin recompensa)=0 ECU'
            },
            {
                'id': 'question_2.c',
                'content': '   c. ¿Cuál es el pago mínimo que el Jugador 1 podría garantizarse a sí mismo? ',
                'choices': [
                    'i. 150 ECU',
                    'ii. 300 ECU',
                    'iii. 900 ECU',
                    'iv. 0 ECU'
                ],
                'answer': 'ii',
                'desc': 'La respuesta correcta es ii (300 ECU). Este sería el pago si es que el Jugador 1 elige no pagar el costo en ninguna tarea.'
            }


        ]
        return {
            'questions': questions
        }


page_sequence = [
    SwitchRoles,
    Intro,
    Intro2,
    P1Instructions,
    # P1Example,
     P2Instructions,
    # # P2Example,
    Quiz,
    P2FirstDecision,
    WaitPage,
    P1Decision,

    P2SecondDecision,
    BeforeOutcomeWP,
    Outcome,
    FinalResults,
    ShuffleWaitPage
]

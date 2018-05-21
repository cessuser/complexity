from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from .forms import RiskFormSet


class Intro(Page):
    pass


class RiskElicitation(Page):
    def get_queryset(self):
        return self.player.risks.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = RiskFormSet(instance=self.player, queryset=self.get_queryset())
        return context

    def post(self):
        self.object = self.get_object()
        self.form = self.get_form(
            data=self.request.POST, files=self.request.FILES, instance=self.object)
        context = super().get_context_data()

        formset = RiskFormSet(self.request.POST, instance=self.player, queryset=self.get_queryset())
        context['formset'] = formset
        if not formset.is_valid():
            self.form.add_error(None, 'all fields are required!')
            context['form'] = self.form
            return self.render_to_response(context)
        formset.save()
        return super().post()

    def before_next_page(self):
        answers = str([int(i) for i in self.player.risks.all().values_list('answer', flat=True)])
        self.player.dump_risk = answers
        self.player.save()
        self.player.set_payoff()


page_sequence = [
    RiskElicitation
]

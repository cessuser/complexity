from otree.api import models,widgets


LOTTERYCHOICES = ((False, 'No'), (True, 'Yes'))

class LotteryField(models.BooleanField):

    description = "field for lotter choices and guesses"

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = widgets.RadioSelectHorizontal
        kwargs['choices'] = LOTTERYCHOICES
        super().__init__(*args, **kwargs)
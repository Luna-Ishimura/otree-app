from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'simple_tg'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 5
    ENDOWMENT = 100
    BC_RATIO =3


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    send_amount = models.CurrencyField(min=0, max=100)
    send_back_amount = models.CurrencyField()


class Player(BasePlayer):
    pass

# FUNCTIONS
def multiplying_send_amount(send_amount: int):
    return send_amount * C.BC_RATIO

def calculate_sender_payoff(send_amount: int, send_back_amount: int):
    return C.ENDOWMENT - send_amount + send_back_amount

def calculate_sendbacker_payoff(send_amount: int, send_back_amount: int):
    return multiplying_send_amount(send_amount)-send_back_amount

def set_payoffs(group: Group):
    group.get_player_by_id(1).payoff = calculate_sender_payoff(
        group.send_amount, group.send_back_amount
    )
    group.get_player_by_id(2).payoff = calculate_sendbacker_payoff(
        group.send_amount, group.send_back_amount
    )
    
# PAGES
class Send(Page):
    form_model = "group"
    form_fields = ["send_amount"]
    
    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1
        
    @staticmethod
    def vars_for_template(player: Player):
            return {"endowment": C.ENDOWMENT}
    
class WaitSend(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2
class Sendback(Page):
    form_model = "group"
    form_fields = ["send_back_amount"]
    template_name = "simple_tg/Sendback.html"
    
    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2
    
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return{"multiplyed_send_amount": multiplying_send_amount(group.send_amount)}
        
class WaitSendbacker(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1

class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return{
            "payoff": player.payoff,
            "bc_ratio": C.BC_RATIO,
            "send_amount": group.send_amount,
            "multiplyed_send_amount": multiplying_send_amount(group.send_amount),
            "send_back_amount": group.send_back_amount,
            "total_send_amount":group.get_player_by_id(1).payoff,
            "total_received_amount":group.get_player_by_id(2).payoff,
        }

page_sequence = [
    Send,
    WaitSend,
    Sendback,
    WaitSendbacker,
    ResultsWaitPage,
    Results,
]
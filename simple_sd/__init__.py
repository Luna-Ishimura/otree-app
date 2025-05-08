from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'simple_sd'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1
    BC_RATIO = 3


class Subsession(BaseSubsession):
    def creating_session(self):
        if self.session.config.get("players_per_group"):
            self.session.config["players_per_group"]=C.PLAYERS_PER_GROUP
            

class Group(BaseGroup):
    def set_payoffs(group: BaseGroup):
        players = group.get_players()
        
        num_cooperators = sum({p.decision =="協力" for p in players})
        group_payoff = num_cooperators * C.BC_RATIO
        for p in players:
            p.payoff = group_payoff / C.PLAYERS_PER_GROUP
            p.group_num_cooperators = num_cooperators

class Player(BasePlayer):
    decision = models.StringField(
        choices=['協力', '非協力'],
        widget = widgets.RadioSelectHorizontal,
        doc = """プレイヤーが協力するかどうか"""
    )
    group_num_cooperators = models.IntegerField(doc="グループ内の協力者数")


# PAGES
class MyPage(Page):
    form_model = 'player'
    form_fields =['decision']


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = Group.set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group_players = player.get_others_in_group()
        return{
            "player": player,
            "num_cooperators": player.group_num_cooperators,
            "group_players": group_players,
            "total_players": len(group_players),
            "payoff": player.payoff
        }


page_sequence = [MyPage, ResultsWaitPage, Results]

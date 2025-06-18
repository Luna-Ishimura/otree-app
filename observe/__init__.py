from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'observe'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 3
    task_texts = [
        "Statistics are like a drunk with a lamppost: used more for support than illumination.",
        "Don't cross your bridges before you get to them.",
        "Llanfairpwllgwyngyllgogerychwyrndrobwyllllantysiliogogogoch"
        ]

import random

class Subsession(BaseSubsession):
    def creating_session(self):
        print(f"Round {self.round_number} - copying roles from round 1")
        if self.round_number ==1 or 'shuffled_texts' not in self.session.vars:
            self.session.vars['shuffled_texts'] = random.sample(C.task_texts, len(C.task_texts))
        
        round_index = self.round_number-1
        selected_text = self.session.vars['shuffled_texts'][round_index]
        
        if self.round_number == 1:
            players = self.get_players()
            random.shuffle(players)
        
            group_matrix = []
            i=0
            while i + 1 < len(players):
                typist = players[i]
                observer = players[i+1]
            
                typist.custom_role='typist'
                observer.custom_role = 'observer'
            
                typist.has_observer = True
                typist.is_evaluated = True

                observer.has_observer = False
                observer.is_evaluated = False

                typist.task_text = selected_text
                observer.task_text = selected_text

                group_matrix.append([typist, observer])
                i += 2

            if i < len(players):
                solo = players[i]
                solo.custom_role = 'typist'
                solo.has_observer = False
                solo.is_evaluated = False
                solo.task_text = selected_text
                group_matrix.append([solo])  
            
            self.set_group_matrix(group_matrix)
        
        else:
            for p in self.get_players():
                p1 = p.in_round(1)
                p.custom_role = p1.custom_role
                p.has_observer = p1.has_observer
                p.is_evaluated = p1.is_evaluated
                p.task_text = self.session.vars['shuffled_texts'][self.round_number - 1]
                
            for g in self.get_groups():
                g.has_observer = any(p.custom_role == 'observer' for p in g.get_players())
                g.save()


    
class Group(BaseGroup):
    latest_typing_duration = models.FloatField(initial=0)
    has_observer = models.BooleanField(initial=False)
    
    def get_player_by_role(self, role):
        for p in self.get_players():
            if p.get_role() == role:
                return p
        return None

class Player(BasePlayer):
    task_text = models.StringField()
    typed_text = models.LongStringField()
    start_time = models.FloatField(initial=0)
    end_time = models.FloatField()
    typing_duration = models.FloatField()
    
    comment = models.LongStringField(blank=True)
    star_rating = models.IntegerField(
        choices=[1,2,3,4,5],
        blank=False,
        label="このタイピングの出来を星で評価してください（1〜5）"
    )
    reaction = models.StringField(blank = True)
    observer_comment = models.LongStringField(blank=True)
    observer_reaction = models.StringField(
        choices=['👍','🥰','🙂','😔','😢'],
        blank = True
    )
    observer_star_rating = models.IntegerField(
        choices=[5,4,3,2,1])
    
    custom_role = models.StringField(null=True, blank=True)
    has_observer = models.BooleanField()
    is_evaluated = models.BooleanField()
    
    def get_role(self):
        return "typist" if self.id_in_group == 1 else "observer"
    
    
# PAGES
class TypingPage(Page):
    form_model = 'player'
    form_fields = ['typed_text', 'start_time', 'end_time']
    
    def is_displayed(self):
        return self.get_role() == "typist"
    
    def vars_for_template(player):
        return{
            'task_text':C.task_texts[player.round_number - 1]
        }
        
    def error_message(player, values):
        task_text = C.task_texts[player.round_number - 1]  # 課題文の取得
        typed = values['typed_text']
        if typed != task_text:
            return "課題文と完全に一致するように入力してください。"
        
    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.end_time is not None and player.start_time is not None:
            player.typing_duration = player.end_time - player.start_time
        else:
            player.typing_duration = 0 
        
class WaitTypist(WaitPage):
    wait_for_all_groups = False

    def is_displayed(self):
        typist = self.group.get_player_by_id(1)
        typed = typist.field_maybe_none('typed_text')
        return self.get_role() == "observer" and (typed in [None, ""])
    
    def after_all_players_arrive(self):
        pass  # なくてもOKだけど一応書いておく

    
class ObserverPage(Page):
    form_model = 'player'
    form_fields = ['observer_comment', 'observer_star_rating', 'observer_reaction']
    
    def is_displayed(self):
        typist = self.group.get_player_by_id(1)
        typed = typist.field_maybe_none('typed_text')
        return self.get_role() == "observer" and typed not in [None, ""]
    
    
    def vars_for_template(self):
        task_text = C.task_texts[self.round_number - 1]
        typist = self.group.get_player_by_id(1)
        duration = typist.field_maybe_none('typing_duration')
        if duration is None:
            duration = 0
        typed = typist.field_maybe_none('typed_text') or ""
        
        char_count = len(typed) if typed else 1  # 0除算防止！
        
        seconds_per_char = duration / char_count if char_count > 0 else 0
        
        return{
            'task_text':task_text,
            'typing_duration':duration,
            'typed_text':typed,
            'seconds_per_char': round(seconds_per_char, 2), 
        }
    
class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        # 観察者の評価をタイピストに渡す
        for group in self.subsession.get_groups():
            typist = group.get_player_by_role('typist')
            observer = group.get_player_by_role('observer')
            typist.observer_comment = observer.observer_comment
            typist.observer_star_rating = observer.observer_star_rating
            typist.observer_reaction = observer.observer_reaction



class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.get_role() == 'typist'
    
    def vars_for_template(self):
        
        typist = self.group.get_player_by_role('typist')
        observer = self.group.get_player_by_role('observer')
        duration = typist.field_maybe_none('typing_duration') or 0
        typed = typist.field_maybe_none('typed_text') or ""
        
        has_observer = bool(self.group.has_observer)
        
        context = {
            'task_text': C.task_texts[self.round_number - 1],
            'typing_duration': duration,
            'typed_text': typed,
            'has_observer': self.group.has_observer,
            }
        
        if self.group.has_observer:
            observer = self.group.get_player_by_role('observer')
            context.update({
            'observer_comment': observer.field_maybe_none('observer_comment') or "",
            'observer_star_rating': observer.field_maybe_none('observer_star_rating') or '評価なし',
            'observer_reaction': observer.field_maybe_none('observer_reaction') or "なし",
        })
            
        return context

page_sequence = [TypingPage,WaitTypist, ObserverPage, ResultsWaitPage, Results]

#!/usr/bin/env python


NAME, NAME_MARKER, KILLS, BONUS, TIME, TIME_FORMAT = 'NAME', '"', 'KILLS', 'BONUS', 'TIME', 'hh:mm'

class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        """String representation of the class instance.
        """
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()


class Lexer(object):    
    def __init__(self, text):
        self.text = text
        self.index = 0
        self.current_char = self.text[self.index]
    
    def skipWhitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
        
    def advance(self, steps=1):
        self.index += steps
        if self.index > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.index]
        
    def get_player_name(self):
        self.advance()
        name = ''
        while self.current_char is not NAME_MARKER:
            name += self.current_char
            self.advance()
        self.advance()
        return name

    def get_time(self):
        self.advance()
        time_end = self.index + len(TIME_FORMAT)
        self.advance(len(TIME_FORMAT))
        return self.text[self.index:time_end]

    def get_bonus(self):
        self.advance()
        bonus = ''
        while self.current_char.isdigit():
            bonus += self.current_char
            self.advance()
        return int(bonus)

    def eat(self, keyword):
        eaten = False
        if self.text[self.index:self.index+len(keyword)] == keyword:
            self.advance(len(keyword))
            eaten = True
        return eaten
           
    def readKeyword(self):
        while self.current_char.isalpha():
            if self.eat(KILLS):
                return Token(KILLS, KILLS)
            elif self.eat(BONUS):
                return Token(BONUS, self.get_bonus())
            elif self.eat(TIME):
                return Token(TIME, self.get_time())

    def error(self):
        raise Exception('invalid character: {}'.format(self.current_char))
        
    def get_next_token(self):
        while self.current_char is not None:
            
            if self.current_char.isspace():
                self.skipWhitespace()
                continue
            
            if self.current_char == NAME_MARKER:
                return Token(NAME, self.get_player_name())
                
            if self.current_char.isalpha():
                return self.readKeyword()

            self.error()


            
class Interpreter(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')
        
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def kill_event(self, player_dict, event_players):
        while self.current_token.type == NAME:
            event_players.append(self.current_token.value)
            self.eat(NAME)
        for player in event_players[1:]:
            player_dict[event_players[0]].killed(player_dict[player])
            
            
    def event(self, player_dict):
        event_players = []
        while self.current_token.type in (NAME, KILLS):
            token = self.current_token
            if token.type == NAME:
                event_players.append(token.value)
                self.eat(NAME)
            if token.type == KILLS:
                self.eat(KILLS)
                self.kill_event(player_dict, event_players)
   

#!/usr/bin/env python
import sys

ALSO, EVENT, NAME, NAME_MARKER, COMMENT_MARKER, KILLS, BONUS, TIME, TIME_FORMAT, DATE, DATE_FORMAT = 'ALSO', 'EVENT', 'NAME', '"', '#', 'KILLS', 'BONUS', 'TIME', 'hh:mm', 'DATE', 'dd.mm.yy' 

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
    def __init__(self, text, name_set):
        self.names = name_set
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
        while self.current_char not in (NAME_MARKER, None):
            name += self.current_char
            self.advance()
        self.advance()
        name = name.strip()
        if name in self.names:
            return name
        sys.exit('Reading unknown name: {}'.format(name)) 

    def get_time(self):
        self.advance()
        time_end = self.index + len(TIME_FORMAT)
        time = self.text[self.index:time_end]
        self.advance(len(TIME_FORMAT))
        return time
    
    def get_date(self):
        self.advance()
        date_end = self.index + len(DATE_FORMAT)
        date = self.text[self.index:date_end]
        self.advance(len(DATE_FORMAT))
        return date

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
            elif self.eat(EVENT):
                return Token(EVENT, EVENT)
            elif self.eat(ALSO):
                return Token(ALSO, ALSO)
            elif self.eat(BONUS):
                return Token(BONUS, self.get_bonus())
            elif self.eat(TIME):
                return Token(TIME, self.get_time())
            elif self.eat(DATE):
                return Token(DATE, self.get_date())
        self.error()

    def error(self):
        error_char = self.current_char
        error_str = 'Error with character %s on line %s' % (error_char, self.text)
        sys.exit(error_str)
        
    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char == COMMENT_MARKER:
                break
            
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
        self.event_dict = {}
        self.players = []

    def error(self):
        raise Exception('Invalid syntax after {}'.format(self.current_token))
        
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def event_players(self):
        while self.current_token is not None and self.current_token.type == NAME:
            self.players.append(self.current_token.value)
            self.eat(NAME)
                    
    def event(self):
        while self.current_token is not None:
            if self.current_token.type in (NAME, KILLS, EVENT, BONUS, ALSO):
                token = self.current_token
                if token.type == NAME:
                    self.players = [token.value]
                    self.eat(NAME)
                elif token.type in (KILLS, EVENT, BONUS):
                    self.eat(token.type)
                    self.event_players()
                    self.event_dict[token] = self.players
                elif token.type == ALSO:
                    self.eat(ALSO)
                    self.players = []
            elif self.current_token.type in (TIME, DATE):
                self.event_dict[self.current_token.type] = self.current_token.value
                self.eat(self.current_token.type)
            else:
                self.error()

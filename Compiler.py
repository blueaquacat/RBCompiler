from collections import OrderedDict
import string

LINE,ID,CONST,IF,GOTO = "#line","#id","#const","#if","#goto"
PRINT,STOP = "#print","#stop"
PLUS = MINUS = LESS = EQUAL = "#op"
EOF = '#EOF'

tag = {'#line':'10','#id':'11','#const':'12','#if':'13','#goto':'14','#print':'15',
       '#stop':'16','#op':'17'}

upper = string.ascii_uppercase
const_range = [str(e) for e in range(0,101)]
num_range = [str(e) for e in range(1,1001)]

#Token class for storing type and value of the token
class Token(object):
    def __init__(self,type,value):
        self.type = type
        self.value = value

    def __str__(self):
        return '{'+self.type+','+repr(self.value)+'}'

    def __repr__(self):
        return self.__str__()

RESERVED_KEYWORDS = {
    'IF': Token(IF, '0'),'GOTO': Token(GOTO, '0'),
    'PRINT': Token(PRINT, '0'),'STOP': Token(STOP, '0')
}

class Lexer(object):
    def __init__(self,text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit()\
              and int(self.current_char) <= 1000:
            result += self.current_char
            self.advance()
        token = Token('#const', result)
        return token

    def ident(self):
        result = ''
        while self.current_char is not None and self.current_char in upper\
              and result not in RESERVED_KEYWORDS:
            result += self.current_char
            self.advance()
        token = RESERVED_KEYWORDS.get(result.upper(), Token(ID,result))
        return token

    def get_next_token(self):
        while self.current_char is not None:
            #if next input_char is whitespace
            if self.current_char.isspace():
                self.skip_whitespace()

            #if next input_char is ID
            if self.current_char in upper:
                return self.ident()

            #if next input_char is number
            if self.current_char.isdigit():
                return self.number()
            
            #if next input_char is plus sign
            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '1')

            #if next input_char is minus sign
            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '2')

            #if next input_char is less than
            if self.current_char == '<':
                self.advance()
                return Token(LESS, '3')

            #if next input_char is equal sign
            if self.current_char == '=':
                self.advance()
                return Token(EQUAL, '4')

            self.error()
        return Token(EOF, None)

class Parser(object):
    def __init__(self,lexer,token_list):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.token_list = token_list

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            print(self.current_token)
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()
        return

    def pgm(self):
        """pgm := line pgm | EOF"""
        if self.current_token.type == EOF:
            return 
        elif self.current_token.type == CONST:
            self.line_type()
            self.token_list.append('\n')
            self.pgm()
        return

    def line_type(self):
        num = self.current_token.value
        self.current_token = Token(LINE,num)
        self.eat(LINE)
        self.token_list.append(tag.get('#line'))
        self.token_list.append(str(num))
        self.stmt()
        return

    def stmt(self):
        if self.current_token.type == ID:
            self.asgmnt()
        elif self.current_token.type == IF:
            self.if_type()
        elif self.current_token.type == PRINT:
            self.print()
        elif self.current_token.type == GOTO:
            self.goto()
        elif self.current_token.type == STOP:
            self.stop()
        else:
            self.error()
        return

    def asgmnt(self):
        word = self.current_token.value
        if word in upper:
            self.eat(ID)
            self.token_list.append(tag.get('#id'))
            self.token_list.append(str(upper.index(word)+1))
        op = self.current_token.type
        self.eat(EQUAL)
        self.token_list.append(tag.get('#op'))
        self.token_list.append('4')
        self.exp()
        return

    def exp(self):
        self.term()
        self.exp2()    
        return

    def exp2(self):
        if self.current_token.type == PLUS:
            self.eat(PLUS)
            self.token_list.append(tag.get('#op'))
            self.token_list.append('1')
            self.term()
        elif self.current_token.type == MINUS:
            self.eat(MINUS)
            self.token_list.append(tag.get('#op'))
            self.token_list.append('2')
            self.term()
        return
        
    def term(self):
        word = self.current_token.value
        if word in upper:
            self.eat(ID)
            self.token_list.append(tag.get('#id'))
            self.token_list.append(str(upper.index(word)+1))
        elif word in const_range:
            self.eat(CONST)
            self.token_list.append(tag.get('#const'))
            self.token_list.append(str(word))
        return

    def if_type(self):
        self.eat(IF)
        self.token_list.append(tag.get('#if'))
        self.token_list.append('0')
        self.cond()
        num = self.current_token.value
        if num in num_range:
            self.current_token = Token(GOTO,num)
            self.eat(GOTO)
            self.token_list.append(tag.get('#goto'))
            self.token_list.append(str(num))
        return

    def cond(self):
        self.term()
        self.cond2()
        return
        
    def cond2(self):
        if self.current_token.type == LESS:
            self.eat(LESS)
            self.token_list.append(tag.get('#op'))
            self.token_list.append('3')
            self.term()
        elif self.current_token.type == EQUAL:
            self.eat(EQUAL)
            self.token_list.append(tag.get('#op'))
            self.token_list.append('4')
            self.term()
        return
        
    def print(self):
        self.eat(PRINT)
        self.token_list.append(tag.get('#print'))
        self.token_list.append('0')
        word = self.current_token.value
        self.eat(ID)
        if word in upper:
            self.token_list.append(tag.get('#id'))
            self.token_list.append(str(upper.index(word)+1))
        return

    def goto(self):
        self.eat(GOTO)
        self.token_list.append(tag.get('#goto'))
        num = self.current_token.value
        if num in num_range:
            self.current_token = Token(LINE,num)
            self.eat(LINE)
            self.token_list.append(num)
        return

    def stop(self):
        self.eat(STOP)
        self.token_list.append(tag.get('#stop'))
        self.token_list.append('0')
        return   

    def parse(self):
        self.pgm()
        if self.current_token.type != EOF:
            self.error()
        return self.token_list
    
file = input().strip('\n')
try: 
    text = open(file).read()
    print('Token sequence:')
except Exception as e:
    print(e)
    
token_list = []
lexer = Lexer(text.strip('\n\t\r'))
parser = Parser(lexer,token_list)
token_list = parser.parse()
token_list.append('0')
print('B_code:')
char = ""
for token in token_list:
    if token == '\n':
        char += token
    else: 
        char += (token+' ')
print(char)

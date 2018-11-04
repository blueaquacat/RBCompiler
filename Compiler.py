from collections import OrderedDict
import string

#B_code type
tag = {'#line':'10','#id':'11','#const':'12','#if':'13','#goto':'14','#print':'15',
       '#stop':'16','#op':'17'}

upper = string.ascii_uppercase  #upper is A..Z
const_range = [str(e) for e in range(0,101)] # const_range is range of CONST [0...100]
num_range = [str(e) for e in range(1,1001)]  # num_range is range of 'line_num [1...1000]

#Token class for storing type and value of the token
class Token(object):
    def __init__(self,type,value):
        self.type = type
        self.value = value

    def __str__(self):
        return '{'+self.type+','+repr(self.value)+'}'

    def __repr__(self):
        return self.__str__()

#Dictionery containing Tokens of IF,GOTO,PRINT,STOP
RESERVED_KEYWORDS = {
    'IF': Token('#if', '0'),'GOTO': Token('#goto', '0'),
    'PRINT': Token('#print', '0'),'STOP': Token('#stop', '0')
}

#This class responsible for reading characters in and try to match with lexemes
#if match, convert into Token
class Scanner(object):
    def __init__(self,text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self): 
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None #End of file
        else:
            self.current_char = self.text[self.pos] #if not EOF, get next character

    def skip_whitespace(self): 
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self): #return Token of number 
                      #(Consider all number to be const at this point)
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        token = Token('#const', result)
        return token

    def ident(self): #return Token of ID or IF,PRINT,GOTO,STOP
        result = ''
        while self.current_char is not None and self.current_char in upper\
              and result not in RESERVED_KEYWORDS:
            result += self.current_char
            self.advance()
        token = RESERVED_KEYWORDS.get(result.upper(), Token('#id',result))
        return token

    def get_next_token(self): #call by parser to get next token
        
        while self.current_char is not None:
            
            if self.current_char.isspace(): #if next input_char is whitespace
                self.skip_whitespace()

            if self.current_char in upper:  #if next input_char is alphabet
                return self.ident()

            if self.current_char.isdigit(): #if next input_char is number
                return self.number()
            
            if self.current_char == '+':    #if next input_char is plus sign
                self.advance()
                return Token('#op', '1')

            if self.current_char == '-':    #if next input_char is minus sign
                self.advance()
                return Token('#op', '2')

            if self.current_char == '<':    #if next input_char is less than
                self.advance()
                return Token('#op', '3')
            
            if self.current_char == '=':    #if next input_char is equal sign
                self.advance()
                return Token('#op', '4')

            self.error() #if char is not match any case then Invalid character entered
            
        return Token('#EOF', None) #self.current_char = None (No more characters) return EOF Token

#This class responsible for matching the tokens with syntax
#If the tokens match with syntax, it gets next token
#If the token doesn't match with syntax, it calls self.error >> invalid syntax
class Parser(object):
    def __init__(self,scanner,token_list):
        self.scanner = scanner
        self.current_token = self.scanner.get_next_token()
        self.token_list = token_list

    def error(self):
        raise Exception('Invalid syntax')

    def match(self, token_type): #match current token with the expected token
        if self.current_token.type == token_type:
            print(self.current_token)
            self.current_token = self.scanner.get_next_token()
        else:
            self.error() #if not matched, raise an error
        return

    #Using recursive descent method
    def pgm(self): #pgm := line pgm | EOF
        if self.current_token.type == '#EOF':
            return 
        elif self.current_token.type == '#const':
            self.line_type()
            self.token_list.append('\n')
            self.pgm()
        return

    def line_type(self):
        num = self.current_token.value
        if num in num_range: #check if num is within num_range
            
            #change token from const to line_num type
            self.current_token = Token('#line',num)
            
            self.match('#line') #try to match current_token with '#line'
            self.token_list.append(tag.get('#line'))
            self.token_list.append(str(num))
            self.stmt()
        else: self.error() #num is out of num_range >> invalid
        return

    def stmt(self):
        if self.current_token.type == '#id':
            self.asgmnt()
        elif self.current_token.type == '#if':
            self.if_type()
        elif self.current_token.type == '#print':
            self.print()
        elif self.current_token.type == '#goto':
            self.goto()
        elif self.current_token.type == '#stop':
            self.stop()
        else:
            self.error() #invalid syntax
        return

    def asgmnt(self):
        word = self.current_token.value
        if word in upper:
            self.match('#id')
            self.token_list.append(tag.get('#id'))
            self.token_list.append(str(upper.index(word)+1))
        else: self.error() #ID is out of range >> invalid
        op = self.current_token.type
        self.match('#op')
        self.token_list.append(tag.get('#op'))
        self.token_list.append('4')
        self.exp()
        return

    def exp(self):
        self.term()
        self.exp2()    
        return

    def exp2(self):
        if self.current_token.type == '#op':
            self.match('#op')
            self.token_list.append(tag.get('#op'))
            self.token_list.append('1')
            self.term()
        elif self.current_token.type == '#op':
            self.match('#op')
            self.token_list.append(tag.get('#op'))
            self.token_list.append('2')
            self.term()
        return
        
    def term(self):
        word = self.current_token.value
        if word in upper:
            self.match('#id')
            self.token_list.append(tag.get('#id'))
            self.token_list.append(str(upper.index(word)+1))
        elif word in const_range:
            self.match('#const')
            self.token_list.append(tag.get('#const'))
            self.token_list.append(str(word))
        else: self.error()
        return

    def if_type(self):
        self.match('#if')
        self.token_list.append(tag.get('#if'))
        self.token_list.append('0')
        self.cond()
        num = self.current_token.value
        if num in num_range: 
            self.current_token = Token('#goto',num)
            self.match('#goto')
            self.token_list.append(tag.get('#goto'))
            self.token_list.append(str(num))
        else: self.error() #num is out of num_range >> invalid
        return

    def cond(self):
        self.term()
        self.cond2()
        return
        
    def cond2(self):
        if self.current_token.type == '#op':
            self.match('#op')
            self.token_list.append(tag.get('#op'))
            self.token_list.append('3')
            self.term()
        elif self.current_token.type == '#op':
            self.match('#op')
            self.token_list.append(tag.get('#op'))
            self.token_list.append('4')
            self.term()
        return
        
    def print(self):
        self.match('#print')
        self.token_list.append(tag.get('#print'))
        self.token_list.append('0')
        word = self.current_token.value
        self.match('#id')
        if word in upper:
            self.token_list.append(tag.get('#id'))
            self.token_list.append(str(upper.index(word)+1)) 
        else: self.error()
        return

    def goto(self):
        self.match('#goto')
        self.token_list.append(tag.get('#goto'))
        num = self.current_token.value
        if num in num_range:
            self.current_token = Token('#line',num)
            self.match('#line')
            self.token_list.append(num)
        else: self.error() #num is out of num_range >> invalid
        return

    def stop(self):
        self.match('#stop')
        self.token_list.append(tag.get('#stop'))
        self.token_list.append('0')
        return   

    def parse(self):
        self.pgm() #call the beginning of production
        if self.current_token.type != '#EOF': 
            self.error()
        return self.token_list
    
#get source program
#select input mode
print("Select input mode:\n0:select file\n1:type input")
x = int(input("[0/1]: "))
if x == 0: #get source program from file
    file = input("Enter file name/path: ").strip('\n')
    try: 
        text = open(file).read()
    except Exception as e: #No such file 
        print(e)

elif x == 1: #get source program from typing in command line
    lines = []
    while True:
        line = input()
        if line:
            lines.append(line)
        else:
            break
    text = '\n'.join(lines)
else: print("invalid input mode")
print('Token sequence:')
token_list = [] #list for storing tokens
scanner = Scanner(text.strip('\n\t\r')) 
parser = Parser(scanner,token_list)
token_list = parser.parse()
token_list.append('0') #indicating end of B_code

#printing B_code
print('B_code:')
char = ""
for token in token_list:
    if token == '\n':
        char += token
    else: 
        char += (token+' ')
print(char)

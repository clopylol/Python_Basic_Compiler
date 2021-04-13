###################################################
################# S A B İ T L E R #################
###################################################

#Rakamlar
DIGITS = '0123456789'

###################################################
################# H A T A L A R ###################
###################################################

class Error: 
    def __init__(self, position_start, position_end, error_name, error_details):
        self.position_start = position_start
        self.position_end = position_end
        self.error_name = error_name
        self.error_details = error_details

    def as_string(self):
        result = f'{self.error_name}: {self.error_details}'
        result += f'Dosya: {self.position_start.fileName}, Satır: {self.position_start.line + 1}'
        return result

class IllegalCharError(Error):
    def __init__(self, position_start, position_end, error_details):
        super().__init__(position_start, position_end, 'Geçersiz Karakter', error_details)
        

###################################################
################# P O S I T I O N #################
#Convert = idx, ln, col
###################################################

class Position(object):
    def __init__(self, index, line, column, fileName, fileText):
        self.index = index
        self.line = line
        self.column = column
        self.fileName = fileName
        self.fileText = fileText

    # Satır İçerisinde ilerlemek için kullanacağız.
    def advance(self, current_char):
        self.index += 1
        self.column +=1

        if current_char == '\n':
            self.line +=1
            self.column = 0

        return self

    # Kullanıcıya hangi dosyanın hangi text'i içerisinde hangi satırda hatanın olduğunu gösterebileceğiz.
    def copy(self):
       return Position(self.index, self.line, self.column, self.fileName, self.fileText)
        

###################################################
################# T O K E N L A R #################
###################################################

# Keywords
TT_INT = 'TT_INT' # int tipi
TT_FLOAT = 'FLOAT' # float tipi

# Operators
TT_PLUS = 'PLUS' # Toplama (+) 
TT_MINUS = 'MINUS' # Çıkarma (-) 
TT_DIV = 'DIV' #Bölme (/)
TT_MUL = 'MUL' #Çarpma  (*)

# Special Symbols
TT_LPAREN = 'LPAREN' # Sol Parantez (
TT_RPAREN = 'RPAREN' # Sağ Parantez )


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    #Temsil
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'


###################################################
################# L E X E R L AR ##################
###################################################

class Lexer:
    def __init__(self, fileName, text):
        self.fileName = fileName
        self.text = text
        self.pos = Position(-1, 0, -1, fileName, text)
        self.current_char = None
        self.advance()

    # Line içerisinde ilerlemek için bu func. kullanacağız. 
    def advance(self):
        # else durumuna düştüğümüzde satırın sonun gelmişiz demektir.
        # Girilen text içerisinde, text uzunluğu kadar gezeceğiz.
        self.pos.advance(self.current_char) 
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None


    def make_numbers(self):
        # int tipinde mi ? Yoksa float tipinde mi sayımız onu kontrol etmeliyiz.
        num_str = ''
        dot_counter = 0

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':

                if dot_counter == 1:  # Sayı içerisinde birden fazla nokta olamaz.
                    break 

                dot_counter += 1
                num_str += '.'
            else: 
                num_str += self.current_char
            self.advance()

        # Sayıda hiç nokta yoksa tipi int'dır.   
        if dot_counter == 0: 
            return Token(TT_INT, int(num_str))
        # dot_counter'ın 0'dan farklı olduğu zaman sayıda nokta var demektir. Tipi floattır.
        else: 
            return Token(TT_FLOAT, float(num_str))


    def make_tokens(self):
        tokens = []    
        #Okunan karakter boş (' ') olmadığı sürece:
        while self.current_char != None:

            # Boşluk varsa bir adım ilerle
            if self.current_char in ' \t': 
                self.advance()
           
            elif self.current_char in DIGITS:
               tokens.append(self.make_numbers())

            elif self.current_char == '+': # Okunan karakter + ise bunu TT_PLUS tokeni olarak tutcağız.
                tokens.append(Token(TT_PLUS)) # + karakterini token listemize TT_PLUS adıyla ekledik.
                self.advance() # 1 Karekter ilerle.
            # Toplama işlemi için yaptığımız adımları, en üstte tanımladığımız tüm sabitler içinde yapalım...
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()

            # Eğer tanımlı olan karakterlerden hiç biri gelmediyse hata dönmemiz gerekiyor.
            else: 
                position_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError (position_start, self.pos,"'" + char + "'")

        return tokens, None


###################################################
################# Ç A L I Ş T I R #################
###################################################

def run(fileName,text):
    lexer = Lexer(fileName, text)
    tokens, error = lexer.make_tokens()

    return tokens, error



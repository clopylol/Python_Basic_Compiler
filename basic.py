from string_with_arrows import *

###################################################
################# S A B İ T L E R #################
###################################################

# Rakamlar
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
        result += '\n\n' + \
            string_with_arrows(self.position_start.ftxt,
                               self.position_start, self.position_end)
        return result


class IllegalCharError(Error):
    def __init__(self, position_start, position_end, error_details):
        super().__init__(position_start, position_end,
                         'Geçersiz Karakter', error_details)  # Illegal Character


class InvalidSyntaxError(Error):
    # IllegalSyntax
    def __init__(self, position_start, position_end, error_details):
        super().__init__(position_start, position_end, 'Geçesiz Syntax', error_details)


###################################################
################# P O S I Z Y O N #################
# Convert = idx, ln, col
###################################################

class Position(object):
    def __init__(self, index, line, column, fileName, fileText):
        self.index = index
        self.line = line
        self.column = column
        self.fileName = fileName
        self.fileText = fileText

    # Satır İçerisinde ilerlemek için kullanacağız.
    def advance(self, current_char=None):
        self.index += 1
        self.column += 1

        if current_char == '\n':
            self.line += 1
            self.column = 0

        return self

    # Kullanıcıya hangi dosyanın hangi text'i içerisinde hangi satırda hatanın olduğunu gösterebileceğiz.
    def copy(self):
        return Position(self.index, self.line, self.column, self.fileName, self.fileText)


###################################################
################# T O K E N L A R #################
###################################################

# Değişken Tipi
TT_INT = 'TT_INT'  # int tipi
TT_FLOAT = 'FLOAT'  # float tipi

# Operatörler
TT_PLUS = 'PLUS'  # Toplama (+)
TT_MINUS = 'MINUS'  # Çıkarma (-)
TT_DIV = 'DIV'  # Bölme (/)
TT_MUL = 'MUL'  # Çarpma  (*)

# Özel Semboller
TT_LPAREN = 'LPAREN'  # Sol Parantez (
TT_RPAREN = 'RPAREN'  # Sağ Parantez )

# Satır Sonu (end of line)
TT_EOF = "EOF"


class Token:
    def __init__(self, type_, value=None, position_start=None, position_end=None):
        self.type = type_
        self.value = value

        if position_start:
            self.position_start = position_start.copy()
            self.position_end = position_start.copy()
            self.position_end.advance()

        if position_end:
            self.position_end = position_end

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'
    # Temsil


def __repr__(self):
    if self.value:
        return f'{self.type}:{self.value}'
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
        self.current_char = self.text[self.pos.index] if self.pos.index < len(
            self.text) else None

    def make_numbers(self):
        # int tipinde mi ? Yoksa float tipinde mi sayımız onu kontrol etmeliyiz.
        num_str = ''
        dot_counter = 0  # Nokta Sayısı
        position_start = self.pos.copy()

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
            return Token(TT_INT, int(num_str), position_start, self.pos)
        # dot_counter'ın 0'dan farklı olduğu zaman sayıda nokta var demektir. Tipi floattır.
        else:
            return Token(TT_FLOAT, float(num_str), position_start, self.pos)

    # Token Oluştur
    def make_tokens(self):
        tokens = []
        # Okunan karakter boş (' ') olmadığı sürece:
        while self.current_char != None:

            # Boşluk varsa bir adım ilerle
            if self.current_char in ' \t':
                self.advance()

            elif self.current_char in DIGITS:
                tokens.append(self.make_numbers())

            # Okunan karakter + ise bunu TT_PLUS tokeni olarak tutcağız.
            elif self.current_char == '+':
                # + karakterini token listemize TT_PLUS adıyla ekledik.
                tokens.append(Token(TT_PLUS, position_start=self.pos))
                self.advance()  # 1 Karekter ilerle.
            # Toplama işlemi için yaptığımız adımları, en üstte tanımladığımız tüm sabitler içinde yapalım...

            # Çıkarma İşlemi
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, position_start=self.pos))
                self.advance()
            # Çarpma İşlemi
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, position_start=self.pos))
                self.advance()
            # Bölme İşlemi
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, position_start=self.pos))
                self.advance()
            # Sol Parantez
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, position_start=self.pos))
                self.advance()
            # Sağ Parantez
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, position_start=self.pos))
                self.advance()

            # Eğer tanımlı olan karakterlerden hiç biri gelmediyse hata dönmemiz gerekiyor.
            else:
                position_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(position_start, self.pos, "'" + char + "'")

        tokens.append(Token(TT_EOF, position_start=self.pos))
        return tokens, None

###################################################
#################### N O D E S ####################
###################################################


class NumberNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return  f'{self.tok}'


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

    def __repr__(self):
        return (self.left_node, self.op_tok, self.right_node)


###################################################
############ P A R S E R  R E S U L T #############
###################################################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error:
                self.error = res.error
            return res.node

        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

###################################################
#################### P A R S E R ##################
###################################################


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = 1
        self.advance()

    def advance(self):
        self.tok_idx += 1

        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

######################################################
    def parse(self):
        res = self.expr()

        # Hata yoksa ve Satır Sonu Değilse
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.position_start, self.current_tok.position_end, "Hata: '+', '-', '*', veya '/' bekleniyor !"
            ))
        return res

    def factor(self,):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_INT, TT_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(tok))

        return res.failure(InvalidSyntaxError(tok.position_start, tok.position_end, 'Float veya Int Bekleniyor !'
                                              ))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    #####################################################

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error:
            return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            self.advance()
            right = res.register(func())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

###################################################
################# Ç A L I Ş T I R #################
###################################################


def run(fileName, text):

    # Tokenlerı Üretelim
    lexer = Lexer(fileName, text)
    tokens, error = lexer.make_tokens()

    if error:
        return None, error

    # AST'leri Üret (Soyut Söz Dizimi)
    parser = Parser(tokens)
    ast = parser.parse()

    return ast.node, ast.error

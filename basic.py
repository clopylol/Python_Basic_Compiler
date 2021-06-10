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
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}\n'
        result += f'Dosya: {self.pos_start.fn}, Satır: {self.pos_start.ln + 1}'
        result += '\n\n' + \
            string_with_arrows(self.pos_start.ftxt,
                               self.pos_start, self.pos_end)
        return result


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Geçersiz Karakter', details)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Geçesiz Syntax', details)

###################################################
################# P O S I Z Y O N #################
# Convert = idx, ln, col


class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    # Satır İçerisinde ilerlemek için kullanacağız.
    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    # Kullanıcıya hangi dosyanın hangi text'i içerisinde hangi satırda hatanın olduğunu gösterebileceğiz.
    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

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
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

      # Temsil
    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'

###################################################
################# L E X E R L AR ##################
###################################################


class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

      # Line içerisinde ilerlemek için bu func. kullanacağız.
    def advance(self):
        # else durumuna düştüğümüzde satırın sonun gelmişiz demektir.
        # Girilen text içerisinde, text uzunluğu kadar gezeceğiz.
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(
            self.text) else None

  	# Token Oluştur
    def make_tokens(self):
        tokens = []
		# Okunan karakter boş (' ') olmadığı sürece:
        while self.current_char != None:
            # Boşluk varsa bir adım ilerle
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
                
            # Okunan karakter + ise bunu TT_PLUS tokeni olarak tutcağız.
            elif self.current_char == '+':
                # + karakterini token listemize TT_PLUS adıyla ekledik.
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance() # 1 Karekter ilerle.
                # Toplama işlemi için yaptığımız adımları, en üstte tanımladığımız tüm sabitler içinde yapalım...
			# Çıkarma İşlemi
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
             # Bölme İşlemi
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            # Sol Parantez
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            # Sağ Parantez
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
                
            # Eğer tanımlı olan karakterlerden hiç biri gelmediyse hata dönmemiz gerekiyor.
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        # int tipinde mi ? Yoksa float tipinde mi sayımız onu kontrol etmeliyiz.

        num_str = ''
        dot_count = 0  # Nokta Sayısı
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:  # Sayı içerisinde birden fazla nokta olamaz.
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

            # Sayıda hiç nokta yoksa tipi int'dır.
        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        
        # dot_counter'ın 0'dan farklı olduğu zaman sayıda nokta var demektir. Tipi floattır.
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

#######################################
# NODES
#######################################


class NumberNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'

###################################################
#################### P A R S E R ##################
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

#######################################
# PARSER
#######################################


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self, ):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        
        # Hata yoksa ve Satır Sonu Değilse
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Hata: '+', '-', '*', veya '/' bekleniyor !"
            ))
        return res

    ###################################

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        elif tok.type in (TT_INT, TT_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(tok))

        elif tok.type == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Sağ Parantez Bulunamadı: )"
                ))

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            'Float veya Int Bekleniyor !'
        ))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    ###################################

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error:
            return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

###################################################
################# Ç A L I Ş T I R #################
###################################################

def run(fn, text):
    
    # Tokenlerı Üretelim
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    # AST'leri Üret (Soyut Söz Dizimi)
    parser = Parser(tokens)
    ast = parser.parse()

    return ast.node, ast.error

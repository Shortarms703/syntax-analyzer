from __future__ import annotations

from collections import deque

# Character classes
EOF = -1
LETTER = 0
DIGIT = 1
UNDERSCORE = 2
NEW_LINE = 3
UNKNOWN = 99

# Token codes
INT_LIT = 10
FLOAT_LIT = 12
IDENT = 11
STR_LIT = 13
ASSIGN_OP = 20
ADD_OP = 21
SUB_OP = 22
MULT_OP = 23
DIV_OP = 24
LEFT_PAREN = 25
RIGHT_PAREN = 26
LEFT_BRACE = 27
RIGHT_BRACE = 28
SEMICOLON = 29
LESS_THAN = 30
GREATER_THAN = 31
EQUALS = 32
NOT_EQUALS = 33
AND_OP = 34
OR_OP = 35
IF = 36
ELSE = 37
FOR = 38
WHILE = 39
COMMENT = 40
QUESTION_MARK = 41
COLON = 42
NEWLINE = 43
EOF_LAST = -12
ERROR_PARENTHESES = -2
ERROR_BRACES = -3
ERROR_BRACKETS = -4
ERROR_FUNCTIONS = -5
ERROR_VARIABLE = -6
ERROR_ASSIGHMENTS = -7
ERROR_ARITHMETIC = -8
ERROR_SEMICOLON = -9
ERROR_IDK_YET = -10
ERROR_COMMENT = -11


class Node:
    def __init__(self, value, line, lexeme=None):
        self.value = value
        self.lexeme = lexeme
        self.line = -1
        self.children = []

    def __repr__(self):
        if self.children:
            return f"Node({self.value}:'{self.lexeme}', children: {self.children})"
        else:
            return f"Node({self.value}:'{self.lexeme}')"

    def print_tree(self, level=0):
        spacer = "•   |"
        if self:
            if self.lexeme is not None:
                thing = spacer * level + f"lexeme: {str(self.lexeme)} token: {str(self.value)}" + "\n"
            else:
                thing = spacer * level + f"<{str(self.value)}>" + "\n"
            for child in self.children:
                if not isinstance(child, Node):
                    thing += spacer * (level + 1) + str(child) + "\n"
                else:
                    thing += child.print_tree(level + 1)
            return thing

    def print_leaf_nodes(self):
        if not self.children or self.lexeme:
            return [(self.lexeme, self.value)]
        else:
            leaf_nodes = []
            for child in self.children:
                if not isinstance(child, Node):
                    leaf_nodes.append(child)
                else:
                    leaf_nodes.extend(child.print_leaf_nodes())
            return leaf_nodes

    def find_bracket_error(self):
        if isinstance(self, Error):
            return self

        queue = deque([self])
        highest_error = None

        while queue:
            current_node = queue.popleft()

            if isinstance(current_node, Error):
                if highest_error is None or current_node.line > highest_error.line:
                    highest_error = current_node

            elif isinstance(current_node, Node):
                queue.extend(child for child in current_node.children if child is not None)
        return highest_error

    def find_other_error(self):
        if isinstance(self, Error):
            return self
        for child in self.children:
            if child is None:
                return None
            if isinstance(child, Error):
                return child
            result = child.find_other_error()
            if result is not None:
                return result
        return None

    def find_first_error(self):
        other_error = self.find_other_error()
        bracket_error = self.find_bracket_error()
        if other_error and bracket_error:
            if "Expected" in other_error.error_message and "Unmatched" in bracket_error.error_message:
                return bracket_error
            else:
                return other_error
        else:
            if other_error:
                return other_error
            elif bracket_error:
                return bracket_error


class Error:
    def __init__(self, error_message, line, show_line=True):
        self.error_message = error_message
        self.line = line
        self.show_line = show_line

    def __repr__(self):
        if self.show_line:
            return self.error_message + " at line " + str(self.line)
        else:
            return self.error_message


class Parser:
    bracket_stack = []

    def __init__(self, tokens, lexemes):
        self.tokens = tokens
        self.lexemes = lexemes
        self.pos = 0
        self.current_line = 1
        self.parse_tree = None

    @classmethod
    def add_to_bracket_stack(cls, bracket):
        cls.bracket_stack.append(bracket)

    def parse(self):
        self.parse_tree = Node('program', self.current_line)
        while (parsed_statement := self.parse_statement()) and self.pos < len(self.tokens):
            self.parse_tree.children.append(parsed_statement)
        if bracket_error := self.update_bracket_stack():
            self.parse_tree.children.append(bracket_error)

        bracket_error = self.update_bracket_stack()
        if bracket_error:
            self.parse_tree.children.append(bracket_error)


        if self.bracket_stack:
            if self.bracket_stack[-1] == LEFT_BRACE:
                self.parse_tree.children.append(Error("Unmatched opening {", self.current_line))
            elif self.bracket_stack[-1] == LEFT_PAREN:
                self.parse_tree.children.append(Error("Unmatched opening (", self.current_line))

    def increment_line_num(self):
        while self.tokens[self.pos] == NEWLINE or self.tokens[self.pos] == COMMENT:
            self.pos += 1
            self.current_line += 1

    def update_bracket_stack(self):
        if self.pos >= len(self.tokens):
            return None
        if self.tokens[self.pos] == LEFT_BRACE:
            self.add_to_bracket_stack(LEFT_BRACE)
        elif self.tokens[self.pos] == RIGHT_BRACE:
            if self.bracket_stack and self.bracket_stack[-1] == LEFT_BRACE:
                self.bracket_stack.pop()
            else:
                return Error("Unmatched closing }", self.current_line)
        if self.tokens[self.pos] == LEFT_PAREN:
            self.add_to_bracket_stack(LEFT_PAREN)
        elif self.tokens[self.pos] == RIGHT_PAREN:
            if self.bracket_stack and self.bracket_stack[-1] == LEFT_PAREN:
                self.bracket_stack.pop()
            else:
                return Error("Unmatched closing )", self.current_line)

    def match(self, matchings: list, dont_incrememnt=False, ignore_brackets=False):
        if self.pos >= len(self.tokens):
            return None
        if not ignore_brackets:
            self.update_bracket_stack()
        lexeme = self.lexemes[self.pos]
        for matching in matchings:
            self.increment_line_num()
            if lexeme == 'a block comment':
                return Node(matching, self.current_line, lexeme)
            if self.tokens[self.pos] == matching:
                if not dont_incrememnt:
                    self.pos += 1
                return Node(matching, self.current_line, self.lexemes[self.pos - 1])
        return None

    def match_with_function(self, function):
        if self.pos >= len(self.tokens):
            return None
        self.increment_line_num()
        self.update_bracket_stack()
        if function(self.tokens[self.pos]):
            self.pos += 1
            return Node(self.tokens[self.pos - 1], self.current_line, self.lexemes[self.pos - 1])
        return None

    def parse_statement(self):
        if parsed_comment := self.match([COMMENT]):
            return parsed_comment
        elif self.match([IF]):
            return self.parse_if()
        elif self.match([FOR]):
            return self.parse_for()
        elif self.match([WHILE]):
            return self.parse_while()
        elif self.match([IDENT], dont_incrememnt=True):
            return self.parse_assign(error=False)
        if self.pos >= len(self.tokens):
            return None

    def parse_if(self):
        node = Node('if', self.current_line)
        node.children.append(self.parse_condition())
        node.children.append(self.parse_block())
        return node

    def parse_for(self):
        node = Node('for', self.current_line)
        node.children.append(self.parse_condition())
        node.children.append(self.parse_block())
        return node

    def parse_while(self):
        node = Node('while', self.current_line)
        node.children.append(self.parse_condition())
        node.children.append(self.parse_block())
        return node

    def parse_condition(self):
        node = Node('condition', self.current_line)
        node.children.append(self.parse_left_paren())
        open_parent_count = 1
        while open_parent_count != 0:
            parsed_anything = self.match_with_function(lambda x: True)

            if parsed_anything.value == LEFT_PAREN:
                open_parent_count += 1
            if parsed_anything.value == RIGHT_PAREN:
                open_parent_count -= 1
            node.children.append(parsed_anything)

            if parsed_anything.value == -1:
                break
        return node

    def parse_block(self):
        node = Node('block', self.current_line)
        if parsed_left_brace := self.parse_left_brace(error=False):
            node.children.append(parsed_left_brace)
            while parsed_statement := self.parse_statement():
                node.children.append(parsed_statement)
            node.children.append(self.parse_right_brace())
        else:
            while parsed_statement := self.parse_statement():
                node.children.append(parsed_statement)
        return node

    def parse_left_paren(self):
        if self.match([LEFT_PAREN]):
            return Node(LEFT_PAREN, self.current_line, self.lexemes[self.pos - 1])
        else:
            return Error("Expected '('", self.current_line)

    def parse_right_paren(self):
        if self.match([RIGHT_PAREN]):
            return Node(RIGHT_PAREN, self.current_line, self.lexemes[self.pos - 1])
        else:
            return Error("Expected right parenthesis", self.current_line)

    def parse_left_brace(self, error=True):
        if self.match([LEFT_BRACE]):
            return Node(LEFT_BRACE, self.current_line, self.lexemes[self.pos - 1])
        elif error:
            return Error("Expected left brace", self.current_line)

    def parse_right_brace(self):
        if self.match([RIGHT_BRACE]):
            return Node(RIGHT_BRACE, self.current_line, self.lexemes[self.pos - 1])
        else:
            if self.current_line >= self.tokens.count(NEWLINE) + self.tokens.count(COMMENT):
                return Error("Syntax analysis failed.", self.current_line, show_line=False)
            return Error("Expected right brace", self.current_line)

    def parse_semicolon(self):
        if self.match([SEMICOLON]):
            return Node(SEMICOLON, self.current_line, self.lexemes[self.pos - 1])
        else:
            error = Error("Missing semi colon", self.current_line)
            if self.tokens[self.pos + 2] == FOR:
                error.line += 1
            self.pos += list(self.tokens[self.pos:]).index(NEWLINE)
            return error

    def parse_assign(self, error=True):
        node = Node('assign', self.current_line)
        if parsed_id := self.parse_id(error=error):
            node.children.append(parsed_id)
            if parsed_equals := self.parse_equals(error=False, ignore_brackets=True):
                node.children.append(parsed_equals)
                node.children.append(self.parse_expr())

                if str(self.lexemes[self.pos]).startswith('"') and '\n' in self.lexemes[self.pos]:
                    error = Error("Unclosed string literal", self.current_line)
                    node.children.append(error)
                else:
                    node.children.append(self.parse_semicolon())
                return node
            elif parsed_function_call := self.parse_function_call_brackets():
                node.children.append(parsed_function_call)
                node.children.append(self.parse_semicolon())
                return node
            return node

    def parse_expr(self):
        node = Node('expr', self.current_line)
        term = self.parse_term()
        node.children.append(term)
        if parsed_plus_minus := self.parse_plus_minus():
            node.children.append(parsed_plus_minus)
            parsed_terminal = self.parse_terminal(error=True)

            # for input 19, float plus string
            if isinstance(term.children[0], Node) and isinstance(parsed_terminal, Node):
                left_type = term.children[0].value
                right_type = parsed_terminal.value
                if 13 in [left_type,
                          right_type] and left_type != right_type:  # string somewhere in addition and not being added to another string
                    error = Error("String assignment error", self.current_line)
                    node.children.append(error)

            # this was for some specific test case
            if isinstance(parsed_terminal, Error):
                parsed_terminal.error_message = "Missing operand before operator"
                node.children.append(parsed_terminal)
            else:
                node.children.append(parsed_terminal)
        return node

    def parse_term(self):
        node = Node('term', self.current_line)
        node.children.append(self.parse_terminal())
        if parsed_mult_div := self.parse_mult_div():
            node.children.append(parsed_mult_div)
            node.children.append(self.parse_terminal(True))
        return node

    def parse_terminal(self, error=False):
        if self.pos >= len(self.tokens):
            return Error("Expected terminal", self.current_line)

        if self.match([IDENT], dont_incrememnt=True):
            return self.parse_id(error=error)
        elif self.match([INT_LIT]):
            return Node(INT_LIT, self.current_line, self.lexemes[self.pos - 1])
        elif self.match([FLOAT_LIT]):
            return Node(FLOAT_LIT, self.current_line, self.lexemes[self.pos - 1])
        elif self.match([STR_LIT]):
            return Node(STR_LIT, self.current_line, self.lexemes[self.pos - 1])
        elif error:
            return Error("Expected terminal", self.current_line)

    def parse_id(self, error=False):
        if self.pos >= len(self.tokens):
            return Error("Expected identifier", self.current_line)

        if self.match([IDENT]):
            node = Node('id', self.current_line)
            node.children.append(Node(IDENT, self.current_line, self.lexemes[self.pos - 1]))
            return node
        elif error:
            return Error("Expected identifier", self.current_line)

    def parse_equals(self, error=True, ignore_brackets=False):
        if self.match([ASSIGN_OP], ignore_brackets=ignore_brackets):
            return Node(ASSIGN_OP, self.current_line, self.lexemes[self.pos - 1])
        elif error:
            return Error("Expected assignment", self.current_line)

    def parse_function_call_brackets(self):
        node = Node('function call brackets', self.current_line)
        node.children.append(self.parse_left_paren())
        node.children.append(self.parse_right_paren())
        return node

    def parse_plus_minus(self):
        if matched := self.match([ADD_OP, SUB_OP]):
            return matched

    def parse_mult_div(self):
        if matched := self.match([MULT_OP, DIV_OP]):
            return matched

import os

from parser import Parser, Node

# Global declarations
# Variables
charClass = 0
lexeme = ''
error = ''
nextChar = ''
token = 0


# Function declarations
def addChar():
    global lexeme
    if len(lexeme) <= 98:
        lexeme += nextChar
    else:
        print("Error - lexeme is too long")


def getChar():
    global nextChar, charClass
    try:
        nextChar = in_fp.read(1)
    except Exception as e:
        nextChar = ''
    if nextChar:
        if nextChar.isalpha():
            charClass = LETTER
        elif nextChar == '_':
            charClass = UNDERSCORE
        elif nextChar.isdigit():
            charClass = DIGIT
        elif nextChar == '\n':
            charClass = NEWLINE
        else:
            charClass = UNKNOWN
    else:
        charClass = EOF


def getNonBlank():
    while nextChar.isspace() and nextChar != '\n':
        getChar()


def lex():
    global lexeme, nextToken, charClass, error
    lexeme = ''
    getNonBlank()
    if charClass == LETTER or charClass == UNDERSCORE:
        addChar()
        getChar()
        while charClass == LETTER or charClass == DIGIT or charClass == UNDERSCORE:
            addChar()
            getChar()

        if lexeme == "if":
            nextToken = IF
        elif lexeme == "else":
            nextToken = ELSE
        elif lexeme == "for":
            nextToken = FOR
        elif lexeme == "while":
            nextToken = WHILE
        elif charClass == UNKNOWN and not nextChar.isspace() and nextChar not in "(+-*/<>)":
            addChar()
            error = "Error - illegal identifier"
            nextToken = EOF
        else:
            nextToken = IDENT

    elif charClass == DIGIT:
        addChar()
        getChar()
        while charClass == DIGIT:
            addChar()
            getChar()
        if nextChar == ".":
            addChar()  # Include the decimal point
            getChar()
            while charClass == DIGIT:
                addChar()
                getChar()
            nextToken = FLOAT_LIT
        elif charClass == LETTER or nextChar == "_":
            while charClass == LETTER or charClass == DIGIT or nextChar == "_":
                addChar()
                getChar()
            error = "Error - illegal identifier"
            nextToken = EOF
        else:
            nextToken = INT_LIT
    elif nextChar == "\"":
        addChar()
        getChar()
        while nextChar != "\"" and nextChar != "":
            addChar()
            getChar()
        if nextChar == "\"":
            addChar()  # Include the closing double quote
            getChar()

            nextToken = STR_LIT
        else:
            error = "Error - unclosed string literal"
            nextToken = EOF

    elif charClass == UNKNOWN:
        lookup(nextChar)
        getChar()

    elif charClass == NEWLINE:
        getChar()

        nextToken = NEWLINE
        lexeme = 'NEWLINE'


    elif charClass == EOF:
        nextToken = EOF
        lexeme = 'EOF'

    # print(f"Next token is: {nextToken}, Next lexeme is {lexeme}")
    # print(f"\t{error}")

    return nextToken, lexeme


def lookup(ch):
    global nextToken, lexeme, error
    if ch == '(':
        addChar()
        nextToken = LEFT_PAREN
    elif ch == ')':
        addChar()
        nextToken = RIGHT_PAREN
    elif ch == '{':
        addChar()
        nextToken = LEFT_BRACE
    elif ch == '}':
        addChar()
        nextToken = RIGHT_BRACE
    elif ch == '+':
        addChar()
        nextToken = ADD_OP
    elif ch == '-':
        addChar()
        nextToken = SUB_OP
    elif ch == '*':
        addChar()
        nextToken = MULT_OP
    elif ch == '/':
        addChar()
        getChar()
        if nextChar == '/':
            while nextChar != '\n' and nextChar != '':
                getChar()
            nextToken = COMMENT, 1
            lexeme = "a single line comment"
        elif nextChar == '*':
            addChar()
            getChar()
            comment_line_length = 1
            while not (nextChar == '*' and in_fp.read(1) == '/'):
                if nextChar == '\n':
                    comment_line_length += 1
                if nextChar == '':
                    error = "Error - unclosed block comment"
                    nextToken = EOF
                    break
                getChar()
            getChar()  # Consume the '/'
            nextToken = COMMENT, comment_line_length
            lexeme = "a block comment"
        else:
            nextToken = DIV_OP
    elif ch == '=':
        addChar()
        getChar()
        if nextChar == '=':
            addChar()
            nextToken = EQUALS
        else:
            nextToken = ASSIGN_OP
    elif ch == ';':
        addChar()
        nextToken = SEMICOLON
    elif ch == '<':
        addChar()
        getChar()
        if nextChar == '=':
            addChar()
            nextToken = LESS_THAN
        else:
            nextToken = LESS_THAN
    elif ch == '>':
        addChar()
        getChar()
        if nextChar == '=':
            addChar()
            nextToken = GREATER_THAN
        else:
            nextToken = GREATER_THAN
    elif ch == '!':
        addChar()
        getChar()
        if nextChar == '=':
            addChar()
            nextToken = NOT_EQUALS
        else:
            nextToken = UNKNOWN
    elif ch == '&':
        addChar()
        getChar()
        if nextChar == '&':
            addChar()
            nextToken = AND_OP
        else:
            nextToken = UNKNOWN
    elif ch == '|':
        addChar()
        getChar()
        if nextChar == '|':
            addChar()
            nextToken = OR_OP
        else:
            nextToken = UNKNOWN
    elif ch == '?':
        addChar()
        nextToken = QUESTION_MARK
    elif ch == ':':
        addChar()
        nextToken = COLON
    else:
        addChar()
        nextToken = EOF


# Character classes
EOF = -1
LETTER = 0
DIGIT = 1
UNDERSCORE = 2
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


def check_error(error: str, test_case):
    if test_case == 1:
        assert error == "Missing semi colon at line 4"
    elif test_case == 2:
        assert error == "Unmatched closing } at line 10"
    elif test_case == 3:
        assert error == "Missing operand before operator at line 6"
    elif test_case == 4:
        assert error == 'None'
    elif test_case == 5:
        assert error == "Unmatched closing ) at line 10"
    elif test_case == 6:
        assert error == "None"
    elif test_case == 7:
        assert error == "Missing semi colon at line 8"
    elif test_case == 8:
        assert error == "Missing semi colon at line 9"
    elif test_case == 9:
        assert error == "Expected '(' at line 5"
    elif test_case == 10:
        assert error == "Missing semi colon at line 9"
    # elif test_case == 11:
    #     assert error == "Unmatched closing } at line 14"
    # elif test_case == 12:
    #     assert error == "Expected '(' at line 10"
    elif test_case == 13:
        assert error == "Expected '(' at line 7"
    elif test_case == 14:
        assert error == "None"
    elif test_case == 15:
        assert error == "Unclosed string literal at line 8"
    # elif test_case == 16:
    #     assert error == "String assignment error at line 8"
    elif test_case == 17:
        assert error == "None"
    elif test_case == 18:
        assert error == "None"
    elif test_case == 19:
        assert error == "String assignment error at line 9"
    elif test_case == 20:
        assert error == "Syntax analysis failed."
    else:
        return None

    return True

list_tests_passed = []
for i in range(1, 21):
    file = "Assignment2_TestCases/input" + str(i if i != 1 else '') + ".txt"

    print("~ " * 50)
    print("Test case " + str(i))
    print()
    print(" - Expected output -")
    print(open("Assignment2_TestCases/expected_output" + str(i if i != 1 else '') + ".txt", "r").read())
    print()
    print(" - Program output - ")

    if os.path.exists(file):
        in_fp = open(file, "r")
        getChar()
        token_list = []
        lexemes = []
        nextToken = 0
        while nextToken != EOF:
            nextToken, lexeme = lex()

            if isinstance(nextToken, tuple):
                token_list.append(nextToken[0])
                lexemes.append(lexeme)
                for j in range(nextToken[1] - 1):
                    token_list.append(NEWLINE)
                    lexemes.append('NEWLINE')
            else:
                token_list.append(nextToken)
                lexemes.append(lexeme)


        parser = Parser(token_list, lexemes)
        parser.parse()
        parse_tree: Node = parser.parse_tree

        debug_small = False
        debug_big = False
        if debug_small:
            if debug_big:
                print("token, lexeme list")
                print([(x, y) for x, y in zip(token_list, lexemes)])
                print()
                print("final parse tree: ")
                print(parse_tree)
                print()
                print("nice view: ")
                print(parse_tree.print_tree())
            print("flattened tree: ", parse_tree.print_leaf_nodes())
            print()

        first_error = parse_tree.find_first_error()
        if first_error:
            print("Error:")
            print(first_error)
        else:
            print("Syntax analysis succeed")
        print()

        test_succeeded = check_error(str(first_error), i)
        if test_succeeded == True:
            print("Test case passed")
            list_tests_passed.append(i)
        else:
            print("Test case failed")

    else:
        print("ERROR - cannot open input.txt")

print("~ * " * 25)
print("Correct test cases:", list_tests_passed)
print("Tests passed: " + str(len(list_tests_passed)) + "/20")

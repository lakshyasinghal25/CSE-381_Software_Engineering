# verifier.py
# # Starter skeleton for Hoare Logic Verifier Assignment
# Students must complete the TODO sections.
# Do not import any libraries here

import re

############################################
# Student Information
############################################
# TODO fill in your information. Without this information you will not get any grades
STUDENT_NAME = "Lakshya Singhal"
ROLL_NUMBER = "23075043"


##################################################
# AST DEFINITIONS
##################################################

# Base Classes
class Stmt:
    pass


class Expr:
    pass


class BExpr:
    pass

# Classes representing statement nodes
class Assign(Stmt):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr


class Sequence(Stmt):
    def __init__(self, first, second):
        self.first = first
        self.second = second


class IfElse(Stmt):
    def __init__(self, cond, then_branch, else_branch):
        self.cond = cond
        self.then_branch = then_branch
        self.else_branch = else_branch


class While(Stmt):
    def __init__(self, cond, body, invariant):
        self.cond = cond
        self.body = body
        self.invariant = invariant


# Classes representing Arithmetic Expression nodes
class Int(Expr):
    def __init__(self, val):
        self.val = val
    

class Var(Expr):
    def __init__(self, var):
        self.var = var


class Binary(Expr):
    def __init__(self, left, right, operator):
        self.left = left
        self.right = right
        self.operator = operator


# Classes representing Boolean Expression nodes
class BoolBinary(BExpr):
    def __init__(self, left, right, operator):
        self.left = left
        self.right = right
        self.operator = operator


class Unary(BExpr):
    def __init__(self, bexpr, operator):
        self.bexpr = bexpr
        self.operator = operator

##################################################
# HELPER FUNCTIONS (DO NOT MODIFY)
##################################################

def check_valid(formula):
    """
    Returns True if the formula is valid.
    """
    s = Solver()
    s.add(Not(formula))
    return s.check() == unsat


def get_var(name):
    """
    Creates a Z3 integer variable with the given name.
    """
    return Int(name)


##################################################
# PARSER
##################################################

def parse_program(program_text):
    """
    Parses the program text and returns the AST.

    Milestone 0: Implement the parser so that it returns
    an AST composed of the classes defined above.
    """

    # TODO: Implement parser

    def tokenize(text):
        pattern = r'\d+|[a-zA-Z_][a-zA-Z0-9_]*|==|<=|>=|[(){};=<>+\-*]|;'
        return re.findall(pattern, text)

    tokens = tokenize(program_text)
    current = 0

    # Helper methods
    #####################

    def match(patterns):
        for pattern in patterns:
            if check(pattern):
                advance()
                return True
            
        return False
        
    def check(pattern):
        if isAtEnd():
            return False
        try:
            return bool(re.fullmatch(pattern, peek()))
        except re.error:
            return peek() == pattern
    
    def peek():
        nonlocal current
        return tokens[current]
    
    def advance():
        nonlocal current
        if not isAtEnd():
            current += 1
        return previous()

    def previous():
        nonlocal current
        if current > 0: 
            return tokens[current-1]
        return None
    
    def isAtEnd():
        nonlocal current
        return current >= len(tokens)
    
    def error(token, message):
        raise SyntaxError(f"Error at '{token}': {message}")
     

    # Perser Methods
    ##################

    def stmt_list():
        ast = stmt()

        while match([";"]):
            if isAtEnd() or check("}"):
                break;
            second = stmt()
            ast = Sequence(ast, second)
        
        if (not isAtEnd()) and (not check("}")):
            raise error(peek(), "Expected end of line")

        return ast
    
    def stmt():
        if match(["while"]):
            return parse_while()
        
        elif match(["if"]):
            return parse_if()

        elif match(["not"]):
            return parse_expr()     # Is this correct or shall we throw an error ?
        
        elif match([r'[a-zA-Z_][a-zA-Z0-9_]*']):
            return parse_assign()
        
        else:
            raise error(peek(), "Invalid token")

    def parse_assign():
        var = previous()
        
        if match(["="]):
            expr = parse_expr()
            return Assign(var, expr)
        
        raise error(previous(), "Unused variable")

    def parse_if():
        if match(["("]):
            cond = parse_expr()
            if match([")"]) and match(["{"]):
                then_branch = stmt_list()
                if match(["}"]) and match(["else"]) and match(["{"]):
                    else_branch = stmt_list()
                    if match(["}"]):
                        return IfElse(cond, then_branch, else_branch)
        
        raise error(previous(), "Invalid Syntax")
    
    def parse_while():
        if match(["("]):
            cond = parse_expr()
            if match([")"]) and match(["invariant"]) and match(["("]):
                invariant = parse_expr()
                if match([")"]) and match(["{"]):
                    body = stmt_list()
                    if match(["}"]):
                        return While(cond, body, invariant)
                    
        raise error(previous(), "Invalid Syntax")
    
    def parse_expr():
        return parse_or()
    
    def parse_or():
        ast = parse_and()

        while match(["or"]):
            operator = previous()
            right = parse_and()
            ast = BoolBinary(ast, right, operator)
        
        return ast
    
    def parse_and():
        ast = parse_not()

        while match(["and"]):
            operator = previous()
            right = parse_not()
            ast = BoolBinary(ast, right, operator)

        return ast
    
    def parse_not():
        if match(["not"]):
            operator = previous()
            right = parse_not()
            return Unary(right, operator)
        
        return parse_equality()
    
    def parse_equality():
        ast = parse_comparison()

        while match(["==", "!="]):
            operator = previous()
            right = parse_comparison()
            ast = BoolBinary(ast, right, operator)

        return ast
    
    def parse_comparison():
        ast = parse_term()

        while match(["<", ">", "<=", ">="]):
            operator = previous()
            right = parse_term()
            ast = BoolBinary(ast, right, operator)

        return ast

    def parse_term():
        ast = parse_factor()

        while match(["+", "-"]):
            operator = previous()
            right = parse_factor()
            ast = Binary(ast, right, operator)

        return ast
    
    def parse_factor():
        ast = parse_primary()

        while match(["/", "*"]):
            operator = previous()
            right = parse_primary()
            ast = Binary(ast, right, operator)

        return ast
    
    def parse_primary():
        if match([r'\d']):
            return Int(previous())
        
        elif match([r'[a-zA-Z_][a-zA-Z0-9_]*']):
            return Var(previous())
            
        raise error(peek(), "Invalid token")
    
    def parse():
        return stmt_list()
        
    return parse()

##################################################
# MAIN ENTRY FUNCTION
##################################################

def verify(program_text: str, pre: str, post: str) -> bool:
    """
    Entry point for the verifier.

    Inputs:
        program_text : program as a string
        pre          : precondition as string
        post         : postcondition as string

    Output:
        True  -> Hoare triple is valid
        False -> Hoare triple is not valid
    """

    ast = parse_program(program_text)

    # Convert pre/post strings into Z3 expressions
    pre_formula = eval(pre)
    post_formula = eval(post)

    return verify_stmt(ast, pre_formula, post_formula)


##################################################
# DISPATCHER
##################################################

def verify_stmt(stmt, pre, post):
    """
    Dispatch to the correct verification rule.
    """

    # if isinstance(stmt, Assign):
    #     return verify_assign(stmt, pre, post)

    # elif isinstance(stmt, Sequence):
    #     return verify_sequence(stmt, pre, post)

    # elif isinstance(stmt, IfElse):
    #     return verify_if(stmt, pre, post)

    # elif isinstance(stmt, While):
    #     return verify_while(stmt, pre, post)

    # else:
    #     raise Exception("Unknown statement type")


##################################################
# ASSIGNMENT RULE
##################################################

def verify_assign(stmt, pre, post):
    """
    Milestone 1:
    Implement the Hoare assignment rule using Z3.
    """

    # TODO: Implement assignment verification
    raise NotImplementedError


##################################################
# SEQUENCE RULE
##################################################

def verify_sequence(stmt, pre, post):
    """
    Milestone 2:
    Verify sequential composition.
    """

    # TODO: Implement sequence rule
    raise NotImplementedError


##################################################
# IF-ELSE RULE
##################################################

def verify_if(stmt, pre, post):
    """
    Milestone 3:
    Verify conditional statements.
    """

    # TODO: Implement if-else verification
    raise NotImplementedError


##################################################
# WHILE RULE
##################################################

def verify_while(stmt, pre, post):
    """
    Milestone 4:
    Verify while loops using the provided invariant.

    Required checks:

    1. pre ⇒ invariant
    2. {invariant ∧ cond} body {invariant}
    3. (invariant ∧ ¬cond) ⇒ post
    """

    # TODO: Implement while verification
    raise NotImplementedError

# Testing..,

program_text = "while(x > 0) invariant(x = 0) {x = x + 2; y = y-1;}"
pre = "True"
post = "True"

print(verify(program_text, pre, post))
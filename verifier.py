# verifier.py
# # Starter skeleton for Hoare Logic Verifier Assignment
# Students must complete the TODO sections.
# Do not import any libraries here

import re
import z3

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
class IntConst(Expr):
    def __init__(self, value):
        self.value = value
    

class Var(Expr):
    def __init__(self, var):
        self.var = var


class BinOp(Expr):
    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op


# Classes representing Boolean Expression nodes
class RelOp(BExpr):
    def __init__(self, op, left, right):
        self.op = op            # "==", "<", "<=", ">", ">="
        self.left = left    
        self.right = right 

class BoolOp(BExpr):
    def __init__(self, op, left, right):
        self.op = op            # "and", "or"
        self.left = left 
        self.right = right 


class NotOp(BExpr):
    def __init__(self, operand):
        self.operand = operand

##################################################
# HELPER FUNCTIONS (DO NOT MODIFY)
##################################################

def check_valid(formula):
    """
    Returns True if the formula is valid.
    """
    s = z3.Solver()
    s.add(z3.Not(formula))
    return s.check() == z3.unsat


def get_var(name):
    """
    Creates a Z3 integer variable with the given name.
    """
    return z3.Int(name)


def to_z3_expr(expr: Expr):
    if isinstance(expr, IntConst):
        return expr.value         

    elif isinstance(expr, Var):
        return get_var(expr.var)   

    elif isinstance(expr, BinOp):
        left  = to_z3_expr(expr.left)   
        right = to_z3_expr(expr.right) 

        if expr.op == '+':
            return left + right
        elif expr.op == '-':
            return left - right
        elif expr.op == '*':
            return left * right
        else:
            raise ValueError(f"Unknown operator: {expr.op}")

    else:
        raise ValueError(f"Unknown expression type: {type(expr)}")


def to_z3_bexpr(bexpr):
    if isinstance(bexpr, RelOp):
        left  = to_z3_expr(bexpr.left)
        right = to_z3_expr(bexpr.right)

        if bexpr.op == '==':   return left == right
        elif bexpr.op == '>':  return left > right
        elif bexpr.op == '>=': return left >= right
        elif bexpr.op == '<':  return left < right
        elif bexpr.op == '<=': return left <= right
        else:
            raise ValueError(f"Unknown operator: {bexpr.op}")

    elif isinstance(bexpr, BoolOp):
        left  = to_z3_bexpr(bexpr.left)
        right = to_z3_bexpr(bexpr.right)

        if bexpr.op == 'and':  return z3.And(left, right)
        elif bexpr.op == 'or': return z3.Or(left, right)
        else:
            raise ValueError(f"Unknown operator: {bexpr.op}")

    elif isinstance(bexpr, NotOp):              # your class is NotOp
        return z3.Not(to_z3_bexpr(bexpr.operand))

    else:
        raise ValueError(f"Unknown bexpr type: {type(bexpr)}")
    

def substitute(formula, var_name, expr):
    # Z3 has a built-in function for this:
    z3_var = get_var(var_name)
    z3_expr = to_z3_expr(expr)
    return z3.substitute(formula, (z3_var, z3_expr))

def collect_vars(node):
    if isinstance(node, Assign):
        return {node.var} | collect_vars(node.expr)
    elif isinstance(node, Var):
        return {node.var}
    elif isinstance(node, IntConst):
        return set()
    elif isinstance(node, BinOp):
        return collect_vars(node.left) | collect_vars(node.right)
    elif isinstance(node, Sequence):
        return collect_vars(node.first) | collect_vars(node.second)
    elif isinstance(node, IfElse):
        return collect_vars(node.cond) | collect_vars(node.then_branch) | collect_vars(node.else_branch)
    elif isinstance(node, While):
        return collect_vars(node.cond) | collect_vars(node.body) | collect_vars(node.invariant)
    elif isinstance(node, RelOp) or isinstance(node, BoolOp):
        return collect_vars(node.left) | collect_vars(node.right)
    elif isinstance(node, NotOp):
        return collect_vars(node.operand)
    else:
        return set()
    
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
            ast = BoolOp(operator, ast, right)
        
        return ast
    
    def parse_and():
        ast = parse_not()

        while match(["and"]):
            operator = previous()
            right = parse_not()
            ast = BoolOp(operator, ast, right)

        return ast
    
    def parse_not():
        if match(["not"]):
            right = parse_not()
            return NotOp(right)
        
        return parse_equality()
    
    def parse_equality():
        ast = parse_comparison()

        while match(["==", "!="]):
            operator = previous()
            right = parse_comparison()
            ast = RelOp(operator, ast, right)

        return ast
    
    def parse_comparison():
        ast = parse_term()

        while match(["<", ">", "<=", ">="]):
            operator = previous()
            right = parse_term()
            ast = RelOp(operator, ast, right)

        return ast

    def parse_term():
        ast = parse_factor()

        while match(["+", "-"]):
            operator = previous()
            right = parse_factor()
            ast = BinOp(ast, right, operator)

        return ast
    
    def parse_factor():
        ast = parse_primary()

        while match(["/", "*"]):
            operator = previous()
            right = parse_primary()
            ast = BinOp(ast, right, operator)

        return ast
    
    def parse_primary():
        if match([r'\d+']):
            return IntConst(previous())
        
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

    # Step 1: collect all variable names used in the program
    variables = collect_vars(ast)

    # Step 2: create Z3 Int variables and put them in a local dict
    z3_vars = {name: z3.Int(name) for name in variables}

    # Step 3: eval with those variables in scope
    pre_formula  = eval(pre,  {"__builtins__": {}}, z3_vars)
    post_formula = eval(post, {"__builtins__": {}}, z3_vars)

    return verify_stmt(ast, pre_formula, post_formula)


##################################################
# DISPATCHER
##################################################

def verify_stmt(stmt, pre, post):
    """
    Dispatch to the correct verification rule.
    """

    if isinstance(stmt, Assign):
        return verify_assign(stmt, pre, post)

    elif isinstance(stmt, Sequence):
        return verify_sequence(stmt, pre, post)

    elif isinstance(stmt, IfElse):
        return verify_if(stmt, pre, post)

    elif isinstance(stmt, While):
        return verify_while(stmt, pre, post)

    else:
        raise Exception("Unknown statement type")


##################################################
# ASSIGNMENT RULE
##################################################

def verify_assign(stmt, pre, post):
    """
    Milestone 1:
    Implement the Hoare assignment rule using Z3.
    """

    # TODO: Implement assignment verification

    post = substitute(post, stmt.var, stmt.expr)
    formula = z3.Implies(pre, post)
    return check_valid(formula)


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

program_text = "x = x + 65"
pre = "x >= 1"
post = "x >= 8"

print(verify(program_text, pre, post))
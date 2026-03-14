# verifier.py
# # Starter skeleton for Hoare Logic Verifier Assignment
# Students must complete the TODO sections.
# Do not import any libraries here


############################################
# Student Information
############################################
# TODO fill in your information. Without this information you will not get any grades
STUDENT_NAME = "Your Name"
ROLL_NUMBER = "Your Roll Number"


##################################################
# AST DEFINITIONS
##################################################

class Stmt:
    pass


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
    raise NotImplementedError


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

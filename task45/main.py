from __future__ import annotations
from typing import Callable, Union


class Request:
    def __init__(self, opcode, op1, op2):
        self.opcode = opcode
        self.op1 = op1
        self.op2 = op2


# Chain of responsibility pattern
class Handler:
    def __init__(self, transformer: Callable[[Request], Union[str, int]] = None, opcode: str = "", nextHandler: Handler = None):
        self.nextHandler = nextHandler
        self.transformer = transformer
        self.opcode = opcode

    def execute(self, request: Request) -> Union[str, int, float]:
        if request.opcode == self.opcode:
            return self.transformer(request)
        elif self.nextHandler is not None:
            return self.nextHandler.execute(request)
        else:
            return "No action was found found the given request"

    def addAtEnd(self, nextHandler: Handler):
        if self.nextHandler is None:
            self.nextHandler = nextHandler
        else:
            self.nextHandler.addAtEnd(nextHandler)


# Builder pattern
class HandlerBuilder:
    def __init__(self):
        self.product = Handler()

    def setTransformer(self, transformer: Callable[[Request], Union[str, int]]):
        self.product.transformer = transformer

    def setOpcode(self, opcode: str):
        self.product.opcode = opcode

    def setNextHandler(self, handler: Handler):
        self.product.opcode = handler

    def getHandler(self) -> Handler:
        return self.product


class Calculator:
    def __init__(self):

        hbuilder = HandlerBuilder()
        hbuilder.setOpcode("+")
        hbuilder.setTransformer(lambda request: request.op1 + request.op2)
        self.handlers = hbuilder.getHandler()
        hbuilder = HandlerBuilder()
        hbuilder.setOpcode("-")
        hbuilder.setTransformer(lambda request: request.op1 - request.op2)
        self.handlers.addAtEnd(hbuilder.getHandler())
        hbuilder = HandlerBuilder()
        hbuilder.setOpcode("*")
        hbuilder.setTransformer(lambda request: request.op1 * request.op2)
        self.handlers.addAtEnd(hbuilder.getHandler())
        hbuilder = HandlerBuilder()
        hbuilder.setOpcode("/")
        hbuilder.setTransformer(lambda request: request.op1 / request.op2 if request.op2 != 0 else "division by zero")
        self.handlers.addAtEnd(hbuilder.getHandler())

        self.mementos = []
        self.opcode = ""
        self.op1, self.op2, self.mistakes, self.result = [0]*4

    def emplaceResult(self, opcode, op1, op2):
        self.result = self.handlers.execute(Request(opcode, op1, op2))
        self.opcode, self.op1, self.op2 = opcode, op1, op2
        self.mistakes += type(self.result) is str
        self.pushAMemento()

    # Memento pattern
    def pushAMemento(self):
        self.mementos.append((self.opcode, self.op1, self.op2, self.result, self.mistakes))

    def restorePreviousMemento(self) -> str:
        if len(self.mementos) > 1:
            self.mementos.pop()
            self.opcode, self.op1, self.op2, self.result, self.mistakes = self.mementos[-1]
            return "memento restored"
        else:
            return "nothing to restore"

    def getDisplayString(self) -> str:
        if type(self.result) is str:
            return str(self.result)
        if self.opcode == "":
            return "no operations stored"
        return f"{self.op1} {self.opcode} {self.op2} = {self.result} (total mistakes in history: {self.mistakes})"


# driver code

def isInt(x) -> bool:
    try:
        int(x)
        return True
    except ValueError:
        return False


calculator = Calculator()
while True:
    command = input('Provide a command ("help" for a list)\n')
    if command == "help":
        print("help, evaluate [number opcode number], display, restoreMemento, mementoSize")
    elif command == "display":
        print(calculator.getDisplayString())
    elif command == "restoreMemento":
        print(calculator.restorePreviousMemento())
    elif command.find("evaluate ") == 0:
        expr = command[len("evaluate "):].split()
        if not (len(expr) == 3 and len(expr[1]) == 1 and isInt(expr[0]) and isInt(expr[2])):
            print("400 bad request")
            calculator.mistakes += 1
        else:
            calculator.emplaceResult(expr[1], int(expr[0]), int(expr[2]))
            print(calculator.getDisplayString())
    elif command == "mementoSize":
        print(f"Memento stack size: {len(calculator.mementos)}")
        print("A peek of what will the state change to if you revert: ")
        print(calculator.mementos[-2] if len(calculator.mementos) > 1 else "(nothing)")
    else:
        print("Unrecognised command")
        calculator.mistakes += 1


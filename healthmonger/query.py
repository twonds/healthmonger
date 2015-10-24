import re
import json

# Prebuild regular expressions for parsing query strings.
PREFIX = re.compile(r'.[^: )]+')
POSTFIX = re.compile(r'.[^ )]*')
STRING = re.compile(r'"([^"\\]|\\.|\\)+"')
COLON = re.compile(r' *: *')
NOT = re.compile(r'not +')
WHITESPACE = re.compile(r' +')
ANY = re.compile(r'.')
OP = re.compile(r'[><]?=|[><]')
AND_OR = re.compile(r'(and|or)\b')
NUMERIC = re.compile(r'(recommendation|metascore|width|height)$')


class ParserError(ValueError):
    """Exception thrown when we have an invalid query.
    """
    pass


class SearchQueryParser:
    """
    """

    def __init__(self):
        self._reset()

    def parse(self, s):
        """Query string parser
        """
        self._reset(s)
        result = []
        stack = [result]

        while self.index < self.input_length:
            c = self.input[self.index]
            if c == '(':
                stack.append(result)
                result = []
                self._read(ANY)
            elif c == ')':
                if not stack:
                    self._raise_parse_error(c)
                tmp = stack.pop()
                if result:
                    tmp.append(self._flatten(result))
                result = tmp
                self._read(ANY)
            elif c == ' ':
                self._read(WHITESPACE)
            else:
                if len(result) % 2:
                    result.append(self._read(AND_OR))
                    self._read(WHITESPACE)
                f = self._read_feature()
                if f:
                    result.append(f)
                else:
                    self._read(ANY)
        return self._flatten(result)

    def _read(self, regex):
        """
        """
        m = regex.match(self.input, self.index)
        if m is None:
            return None
        self.index = m.end()
        return m.group()

    def _reset(self, s=None):
        self.input = s or ""
        self.input_length = len(self.input)
        self.index = 0
        self.result = None
        self.op = And

    def _raise_parse_error(self, c):
        error_msg = "Unexpected '{0}' at index {1} (input length {2})"
        error_msg = error_msg.format(c, self.index, self.input_length)
        raise ParserError(error_msg)

    def _read_feature(self):
        not_ = bool(self._read(NOT))
        name = self._read(PREFIX)
        op = None
        value = None
        if name is None:
            return None
        if self._read(COLON):
            op = NUMERIC.match(name) and self._read(OP)
            value = self._read(STRING)
            value = json.loads(value) if value else self._read(POSTFIX)
            if op and isinstance(value, basestring):
                try:
                    value = json.loads(value)
                except ValueError:
                    pass
        if op:
            res = Numerical(name, op, value)
        elif value:
            res = Literal('%s:%s' % (name, value))
        else:
            res = Literal(name)
        return Not(res) if not_ else res

    def _flatten(self, lst):
        if not lst:
            return None
        op = And
        vals = iter(lst)
        result = vals.next()
        for val in vals:
            if val == 'and':
                op = And
            elif val == 'or':
                op = Or
            elif isinstance(val, QueryOp):
                result = op(result, val)
        return result


class QueryOp(object):
    """
    """
    def __init__(self, *args):
        self.arguments = args
        if not (self.MIN_ARGS <= len(args) <= self.MAX_ARGS):
            error_msg = "fail MIN_ARGS:{0} <= ARGS_LEN:{1} <= MAX_ARGS:{2}"
            error_msg = error_msg.format(self.MIN_ARGS,
                                         len(args),
                                         self.MAX_ARGS)
            raise ParserError(error_msg)

    def __repr__(self):
        arg_str = ', '.join(map(repr, self.arguments))
        return '{0}({1})'.format(type(self).__name__, arg_str)

    def __eq__(self, other):
        arg_length_check = (self.arguments == other.arguments)
        return isinstance(other, type(self)) and arg_length_check


class Literal(QueryOp):
    """Represents a literal key lookup, e.g. category:puzzles or tag:dress-up.
    """
    MIN_ARGS = 1
    MAX_ARGS = 1


class Numerical(QueryOp):
    """Represents a numerical query, e.g. age:>=88
    """
    MIN_ARGS = 3
    MAX_ARGS = 3


class And(QueryOp):
    """Represents an and operation built of `QueryOp` objects.
    """
    MIN_ARGS = 2
    MAX_ARGS = 2


class Or(QueryOp):
    """Represents a binary or operation built of `QueryOp` objects.
    """
    MIN_ARGS = 2
    MAX_ARGS = 2


class Not(QueryOp):
    """Represents a unary not operation that accepts a `QueryOp`.
    """
    MIN_ARGS = 1
    MAX_ARGS = 1

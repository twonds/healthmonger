import unittest

from healthmonger import query


class QueryOpTest(unittest.TestCase):
    """Ensure query ops are built correctly.
    """

    def test_literal(self):
        literal = query.Literal('category:health')
        # Looks odd but tests the __eq__ method in QueryOp
        self.assertEqual(literal, literal)
        self.assertEqual("Literal('category:health')",
                         str(literal))

    def test_numerical_error(self):
        with self.assertRaises(query.ParserError):
            query.Numerical('age:>=88')

    def test_numerical(self):
        num = query.Numerical('age', ('-inf', 88), (88, '+inf'))
        # Looks odd but tests the __eq__ method in QueryOp
        self.assertEqual(num, num)
        self.assertEqual("Numerical('age', ('-inf', 88), (88, '+inf'))",
                         str(num))

    def test_and_error(self):
        with self.assertRaises(query.ParserError):
            query.And('wat')

    def test_and(self):
        num = query.And('age', 42)
        # Looks odd but tests the __eq__ method in QueryOp
        self.assertEqual(num, num)
        self.assertEqual("And('age', 42)",
                         str(num))


class ParseQueryTest(unittest.TestCase):
    """Parse some query strings to ensure operations are correct.
    """

    def test_parse_literal(self):
        literal = query.Literal('category:age')
        qp = query.SearchQueryParser()
        query_string = "category:age"
        result = qp.parse(query_string)
        self.assertEqual(literal, result)

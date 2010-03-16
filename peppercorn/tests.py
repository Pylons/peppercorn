import unittest

class TestParse(unittest.TestCase):
    def _callFUT(self, fields):
        from peppercorn import parse
        return parse(fields)
        
    def test_it(self):
        fields = [
            ('name', 'project1'),
            ('title', 'Cool project'),
            ('__start__', 'dates:sequence'),
            ('__start__', 'date:sequence'),
            ('day', '10'),
            ('month', '12'),
            ('year', '2008'),
            ('__end__', 'date:sequence'),
            ('__start__', 'date:sequence'),
            ('day', '10'),
            ('month', '12'),
            ('year', '2009'),
            ('__end__', 'date:sequence'),
            ('__end__', 'dates:sequence'),
            ]

        result = self._callFUT(fields)
        
        self.assertEqual(
            result,
            {'dates': [['10', '12', '2008'],
                       ['10', '12', '2009']],
             'name': 'project1',
             'title': 'Cool project'})


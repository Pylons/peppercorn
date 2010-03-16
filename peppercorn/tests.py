import unittest

class TestParse(unittest.TestCase):
    def _callFUT(self, fields):
        from peppercorn import parse
        return parse(fields)
        
    def test_functional(self):
        fields = [
            ('name', 'project1'),
            ('title', 'Cool project'),
            ('__start__', 'series:mapping'),
            ('name', 'date series 1'),
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
            ('__end__', 'series:mapping'),
            ]

        result = self._callFUT(fields)
        
        self.assertEqual(
            result,
            {'series':
             {'name':'date series 1',
              'dates': [['10', '12', '2008'],
                        ['10', '12', '2009']],
              },
             'name': 'project1',
             'title': 'Cool project'})

    def test_bad_start_marker(self):
        fields = [
            ('__start__', 'something:unknown'),
            ]
        
        self.assertRaises(ValueError, self._callFUT, fields)

    def test_unnamed_start_marker(self):
        fields = [
            ('__start__', 'mapping'),
            ('name', 'fred'),
            ('__end__', ''),
            ]

        result = self._callFUT(fields)
        self.assertEqual(result, {'': {'name':'fred'}})
        

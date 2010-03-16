import unittest

class TestParse(unittest.TestCase):
    def _callFUT(self, fields):
        from peppercorn import parse
        return parse(fields)
        
    def test_functional(self):
        from peppercorn import START, END, MAPPING, SEQUENCE
        fields = [
            ('name', 'project1'),
            ('title', 'Cool project'),
            (START, 'series:%s' % MAPPING),
            ('name', 'date series 1'),
            (START, 'dates:%s' % SEQUENCE),
            (START, 'date:%s' % SEQUENCE),
            ('day', '10'),
            ('month', '12'),
            ('year', '2008'),
            (END, 'date:%s' % SEQUENCE),
            (START, 'date:%s' % SEQUENCE),
            ('day', '10'),
            ('month', '12'),
            ('year', '2009'),
            (END, 'date:%s' % SEQUENCE),
            (END, 'dates:%s' % SEQUENCE),
            (END, 'series:%s' % MAPPING),
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
        from peppercorn import START
        fields = [
            (START, 'something:unknown'),
            ]
        
        self.assertRaises(ValueError, self._callFUT, fields)

    def test_unnamed_start_marker(self):
        from peppercorn import START, END, MAPPING
        fields = [
            (START, MAPPING),
            ('name', 'fred'),
            (END, ''),
            ]

        result = self._callFUT(fields)
        self.assertEqual(result, {'': {'name':'fred'}})
        

import unittest
import MTGLardFetcher

class PrawMock:
    body = "alsdfjlasfdjlsfjl"
    id = 'id0'
    author = 'author0'

    def __init__(self, body):
        self.body = body

class UnitTest(unittest.TestCase):

    def test_match0(self):
        d = PrawMock('nothing matches')
        v = MTGLardFetcher.get_matches(d.body) 
        self.assertEqual(v, [])

    def test_match1(self):
        d = PrawMock('[[x]]')
        v = MTGLardFetcher.get_matches(d.body) 
        self.assertEqual(v[0], 'x')

    def test_match2(self):
        d = PrawMock('[[x]] some text [[y]]\n[[zzz]]')
        v = MTGLardFetcher.get_matches(d.body) 
        self.assertEqual(v[1], 'y')

    def test_match3(self):
        d = PrawMock('[[x]] some text [[[[[[[[[y]]')
        v = MTGLardFetcher.get_matches(d.body) 
        print(v)
        self.assertEqual(v[1], 'y')

if __name__ == '__main__':
    unittest.main()

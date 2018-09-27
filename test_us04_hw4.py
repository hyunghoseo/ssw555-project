# jmcgirr hw4 unit test
# I pledge

import unittest
import datetime

# suggest running with -b to suppress the prints

class us04Tests(unittest.TestCase):
    def test1(self):
        marr = datetime.datetime.now()
        div = datetime.datetime(2001, 2, 24)
        with self.assertRaises(SystemExit) as cm:
            testUs05(marr,div)
        self.assertEqual(cm.exception.code,-1,'Test 1 failed - wrong code')
    def test2(self):
        div = datetime.datetime.now()
        marr = datetime.datetime(2001, 2, 24)
        try:
            testUs05(marr, div)
        except SystemExit:
            self.fail('Test 2 - this should not have thrown an exception')
    def test3(self):
        marr = datetime.datetime.now()
        div = datetime.datetime(2001, 2, 24)
        with self.assertRaises(TypeError) as cm:
            testUs05(marr)
    def test4(self):
        with self.assertRaises(TypeError) as cm:
            testUs05()
    def test5(self):
        marr = datetime.datetime(2020, 2, 24)
        div = datetime.datetime.now()
        with self.assertRaises(SystemExit) as cm:
            testUs05(marr,div)
        self.assertEqual(cm.exception.code,-1)

# code from project ported into a function to test
def testUs05(marrdate, divdate):
    entry = {
        'id':'test',
        'marr': marrdate,
        'div': divdate
    }

    # begin us04 code
    if entry.get("div") and entry.get("marr") and (get_age(entry.get("marr"), entry.get("div")) < 0):
        print "Error: FAM " + entry["id"] + " has a marriage date before birth date"
        exit(-1)
    # end us04 code

# project dependency code
def get_age(birth, death):
    return death.year - birth.year - ((death.month, death.day) < (birth.month, birth.day))

if __name__ == '__main__':
    unittest.main()
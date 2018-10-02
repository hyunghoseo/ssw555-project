import unittest
import sys
from contextlib import contextmanager
from StringIO import StringIO
from datetime import date
import run

@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

run.main("testfile.ged")

# Birth before marriage
class US02Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []
        run.famList = []
        
    def test_no_birth(self):
        entry = {"id": "i01"}
        with captured_output() as (out,err):
            run.add_entry(entry, "INDI")
        output = out.getvalue().strip()
        self.assertIn("INDI i01 is missing a birth date", output)
    
    def test_no_marr(self):
        entry = {"id": "i02", "birth": date.today()}
        with captured_output() as (out,err):
            run.add_entry(entry, "INDI")
        output = out.getvalue().strip()
        self.assertEquals("", output)
    
    def test_birth_before_marr(self):
        entry = {"id": "i03", "birth": date(1992,5,23), "fams": "f01"}
        famEntry = {"id": "f01", "marr": date(2017,3,4)}
        with captured_output() as (out,err):
            run.add_entry(famEntry, "FAM")
            run.add_entry(entry, "INDI")
        output = out.getvalue().strip()
        self.assertEquals("", output)
        
    def test_marr_before_birth(self):
        entry = {"id": "i04", "birth": date(1998,3,25), "fams": "f02"}
        famEntry = {"id": "f02", "marr": date(1993,4,6)}
        with captured_output() as (out,err):
            run.add_entry(famEntry, "FAM")
            run.add_entry(entry, "INDI")
        output = out.getvalue().strip()
        self.assertIn("INDI i04 has marriage date before birth date", output)
        
    def test_marr_birth_same(self):
        entry = {"id": "i05", "birth": date.today(), "fams": "f03"}
        famEntry = {"id": "f03", "marr": date.today()}
        with captured_output() as (out,err):
            run.add_entry(famEntry, "FAM")
            run.add_entry(entry, "INDI")
        output = out.getvalue().strip()
        self.assertEquals("", output)
        
# Birth before death
class US03Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []
        run.famList = []
        
    def test_birth_before_death(self):
        entry = {"id": "i01", "birth": date(1992,5,23), "death": date(2017,3,4)}
        with captured_output() as (out,err):
            run.add_entry(entry, "INDI")
        output = out.getvalue().strip()
        self.assertEquals("", output)
        
    def test_death_before_birth(self):
        entry = {"id": "i02", "birth": date(1998,3,25), "death": date(1993,4,6)}
        with captured_output() as (out,err):
            run.add_entry(entry, "INDI")
        output = out.getvalue().strip()
        self.assertIn("INDI i02 has death date before birth date", output)
        
    def test_death_birth_same(self):
        entry = {"id": "i05", "birth": date.today(), "death": date.today()}
        with captured_output() as (out,err):
            run.add_entry(entry, "INDI")
        output = out.getvalue().strip()
        self.assertEquals("", output)

unittest.main()